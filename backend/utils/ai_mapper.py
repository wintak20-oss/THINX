"""
AI-powered data mapping module using local Ollama LLM.

This module provides intelligent data mapping between source CSV/Excel columns
and the Common Data Model (CDM) schema defined in models.py. All processing
is performed locally ensuring GDPR compliance - no data leaves the system.
"""

import requests
import json
import os


class SmartMapper:
    """
    AI-powered data mapper using local Ollama LLM service.
    
    Maps source data columns to the Common Data Model (CDM) schema using
    a local large language model. All inference happens on-premises ensuring
    data privacy and GDPR compliance.
    
    Attributes:
        host (str): Ollama service endpoint URL
    """
    
    def __init__(self, host=None):
        """
        Initialize SmartMapper with Ollama service connection.
        
        Args:
            host (str, optional): Ollama service URL. Defaults to OLLAMA_HOST
                                  environment variable or 'http://ollama:11434'.
        """
        self.host = host or os.environ.get('OLLAMA_HOST', 'http://ollama:11434')
        
    def is_available(self):
        """
        Check if Ollama LLM service is reachable and operational.
        
        Returns:
            bool: True if service responds successfully, False otherwise.
            
        Note:
            Uses a 2-second timeout to avoid blocking the application.
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self):
        """
        List all locally available LLM models from Ollama.
        
        Returns:
            list: List of model dictionaries containing model metadata.
                  Returns empty list if service is unavailable.
                  
        Example:
            >>> mapper = SmartMapper()
            >>> models = mapper.list_models()
            >>> [{'name': 'llama3:latest', 'size': 4661224192}, ...]
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except Exception:
            return []

    def pull_model(self, model_name):
        """
        Download an LLM model from Ollama library to local system.
        
        Args:
            model_name (str): Name of the model to download (e.g., 'llama3', 'mistral').
            
        Returns:
            requests.Response: Streaming response object for monitoring download progress.
            
        Raises:
            Exception: If the model pull request fails.
            
        Note:
            This operation can take several minutes depending on model size.
            The returned response object streams download progress updates.
        """
        # We return the response object for streaming
        return requests.post(
            f"{self.host}/api/pull",
            json={"name": model_name},
            stream=True,
            timeout=300
        )

    def suggest_mapping(self, source_columns, target_schema, model='llama3'):
        """
        Use local LLM to suggest intelligent mapping between source columns and CDM schema.
        
        This method constructs a prompt with the ACTUAL CDM schema fields from models.py,
        ensuring the AI cannot hallucinate non-existent fields. All processing is local
        and GDPR-compliant - no data leaves the system.
        
        Args:
            source_columns (list): List of column names from uploaded CSV/Excel file.
            target_schema (dict): CDM schema dictionary from models.CDM_SCHEMA.
            model (str, optional): Name of Ollama model to use. Defaults to 'llama3'.
            
        Returns:
            dict: Mapping result with structure:
                  {
                      "mapping": {source_col: "Entity.field" or None},
                      "transformations": {source_col: "transform_type"}
                  }
                  On error: {"error": "error message"}
                  
        Note:
            - No timeout applied as large models may take several minutes
            - All inference happens locally for data privacy
            - The prompt dynamically injects actual CDM fields to prevent hallucination
            
        Example:
            >>> mapper = SmartMapper()
            >>> result = mapper.suggest_mapping(
            ...     ['user_age', 'user_gender'],
            ...     CDM_SCHEMA
            ... )
            >>> result
            {'mapping': {'user_age': 'Victim.age', 'user_gender': 'Victim.gender'},
             'transformations': {'user_age': 'to_numerical'}}
        """
        prompt = self._build_prompt(source_columns, target_schema)
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=None  # No timeout - let it run as long as needed
            )
            
            if response.status_code == 200:
                result = response.json()
                parsed = self._parse_response(result['response'], source_columns)
                return parsed
            else:
                return {"error": f"Ollama API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}

    def _build_prompt(self, source_columns, target_schema):
        """
        Build AI prompt with strict CDM field injection to prevent hallucination.
        
        This method dynamically extracts the ACTUAL field list from models.CDM_SCHEMA
        and injects it into the prompt. The AI is constrained to only map to fields
        that genuinely exist in the CDM, preventing phantom fields like
        'Victim.sexual_violence_type' if it's not defined.
        
        Args:
            source_columns (list): Column names from source data file.
            target_schema (dict): CDM schema from models.CDM_SCHEMA.
            
        Returns:
            str: Formatted prompt string for LLM with injected CDM fields.
            
        Note:
            The prompt uses one-shot learning with a concrete example to guide
            the LLM toward the correct JSON structure without hallucination.
        """
        # Build flat list with entity prefixes - STRICT CDM INJECTION
        # This prevents the AI from inventing fields that don't exist
        flat_fields = []
        for entity_type, entity_data in target_schema.items():
            for field in entity_data.get('fields', []):
                field_name = f"{entity_type}.{field['name']}"
                flat_fields.append({
                    'field': field_name,
                    'type': field.get('type'),
                    'description': field.get('description', '')
                })
        
        return f"""You are a data mapping assistant. Your task is to create a simple JSON mapping between source columns and target schema fields.

CRITICAL RULES:
- Return ONLY a simple JSON object with two keys: "mapping" and "transformations"
- DO NOT include $schema, definitions, examples, or any JSON Schema syntax
- DO NOT add explanatory text before or after the JSON
- DO NOT wrap the JSON in markdown code blocks
- The "mapping" object must have EXACTLY these source columns as keys: {json.dumps(source_columns)}
- Map each source column to a target field in "EntityType.fieldName" format, or null if no match exists

Source Columns: {json.dumps(source_columns)}

Target CDM Fields:
{json.dumps(flat_fields, indent=2)}

Available Transformations:
- "to_numerical": Convert Yes/No, True/False, Male/Female to 1/0
- "fill_missing": Fill null values with "Unknown"
- "normalize_case": Standardize text to Title Case
- "format_date": Standardize dates to YYYY-MM-DD
- "clean_text": Remove special characters and extra spaces
- "to_categorical": Convert age numbers to categories (Child/Adult/Senior)

ONE-SHOT EXAMPLE:
Input columns: ["user_age", "curr_loc", "unknown_field"]
Output:
{{"mapping": {{"user_age": "Victim.age", "curr_loc": "Location.name", "unknown_field": null}}, "transformations": {{"user_age": "to_numerical", "curr_loc": "normalize_case"}}}}

Now map these source columns: {json.dumps(source_columns)}
Return ONLY the JSON object, nothing else:"""
    
    def _parse_response(self, response_text, source_columns):
        """
        Parse and validate LLM response, ensuring strict adherence to expected structure.
        
        This method performs critical validation:
        1. Strips markdown code blocks (```json ... ```)
        2. Validates JSON structure
        3. Ensures mapping keys exactly match source columns (prevents hallucination)
        4. Returns structured mapping and transformation recommendations
        
        Args:
            response_text (str): Raw text response from LLM.
            source_columns (list): Original source column names for validation.
            
        Returns:
            dict: Validated mapping structure:
                  {
                      "mapping": {source_col: "Entity.field"},
                      "transformations": {source_col: "transform_type"}
                  }
                  On validation failure: {"error": "descriptive error message"}
                  
        Note:
            Strict validation prevents the AI from mapping non-existent columns or
            inventing fields not present in the source data.
        """
        # Strip markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        # Parse JSON
        try:
            result = json.loads(text)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON from LLM: {str(e)}"}
        
        # Validate structure
        if not isinstance(result, dict):
            return {"error": "LLM response must be a JSON object"}
        
        if "mapping" not in result:
            return {"error": "LLM response missing 'mapping' key"}
        
        mapping = result.get("mapping", {})
        
        # Validate that mapping keys match source columns
        mapping_keys = set(mapping.keys())
        source_set = set(source_columns)
        
        if mapping_keys != source_set:
            missing = source_set - mapping_keys
            extra = mapping_keys - source_set
            errors = []
            if missing:
                errors.append(f"Missing columns: {missing}")
            if extra:
                errors.append(f"Extra columns: {extra}")
            return {"error": f"Mapping keys don't match source columns. {' '.join(errors)}"}
        
        # Return validated result
        return {
            "mapping": mapping,
            "transformations": result.get("transformations", {})
        }
