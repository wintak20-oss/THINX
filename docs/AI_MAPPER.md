# AI Smart Mapper Guide

## Overview

The AI Smart Mapper is a tool that automatically organizes data columns to match Thinx's standard format (the Common Data Model). Instead of manually renaming columns, the AI performs this task automatically.

### Purpose

**Problem:** Interview data often has columns like:
- `"name_of_victim"`, `"victim name"`, `"Name"`, `"respondent_name"`

**Thinx expects:** `Victim.name`

**Solution:** AI reads column names, understands their meaning, and suggests correct standard names.

### Example

**Your data (before):**
```
age | gender | country | trafficker_name | incident_date
27  | Male   | Eritrea | John Smith      | 2023-05-15
```

**AI suggestions:**
- `age` → `Victim.age`
- `gender` → `Victim.gender`
- `country` → `Victim.nationality`
- `trafficker_name` → `Trafficker.name`
- `incident_date` → `Incident.date`

Click "Apply" and data is ready to use.

---

## How It Works

The AI functions as an automated assistant that:

1. Reads column names (e.g., "age", "victim_gender", "nationality")
2. Compares them to Thinx's standard format
3. Suggests the best match (e.g., "age" → "Victim.age")
4. Applies renaming when approved

### Privacy and Security

**Important:** The AI runs entirely on local infrastructure. Your sensitive research data:
- Never leaves your system
- Never connects to the internet
- Never touches external AI services like ChatGPT or Claude
- Is GDPR compliant by design

This is called "local AI" or "on-premise AI" - the model runs in a Docker container on your own hardware.

## Prerequisites

Before starting:
- Thinx running with `--profile full` (includes AI)
- At least 2GB free disk space (for AI model)
- Data file ready (Excel or CSV format)

To verify AI is enabled:
```bash
docker-compose --profile full up --build
```

## Step-by-Step Guide

### Step 1: Check if AI Is Available

1. Open Thinx at http://localhost
2. Upload a data file (or use test data from `Mock data/` folder)
3. Go to Step 3: Schema & Validation
4. Look for the "AI Smart Mapper" section

**If you see it:** Continue to Step 2.

**If you don't see it:**
```bash
# Check if Ollama is running
docker ps

# Look for a container with "ollama" in the name
# If not there, restart with full profile:
docker-compose --profile full up -d
```

### Step 2: Download an AI Model

**What is a "model"?** A downloaded component that provides intelligence to the AI. Different models have different:
- **Size** (disk space required)
- **Speed** (processing time)
- **Accuracy** (quality of suggestions)

#### Which Model to Choose

**For most researchers:** `llama3.2`

| Model Name | Size | Speed | Accuracy | Best For |
|-----------|------|-------|----------|----------|
| **llama3.2** | 2GB | Fast | Good | Standard recommendation |
| **phi3** | 2.3GB | Very Fast | Good | Older computers |
| **mistral** | 4GB | Medium | Excellent | Better results needed |
| **gemma2:2b** | 1.6GB | Very Fast | Decent | Quick testing |
| **llama3:8b** | 4.7GB | Slow | Excellent | Maximum accuracy |

**Recommendation:** If this is your first time, choose **llama3.2**. It provides balanced performance.

#### How to Download (Using the Interface)

1. In Step 3: Schema & Validation, find the "Download New Model" section
2. In the text box, type: `llama3.2`
3. Click the "Download" button
4. Wait 5-15 minutes (downloading 2GB file)
5. When complete: "Model downloaded successfully"
6. Click "Refresh" - your model appears in the dropdown

Note: The download only happens once. After that, the model is saved and ready to use instantly.

#### Alternative: Download via Command Line

If you prefer using the terminal:

```bash
# For Docker setup
docker exec -it ollama_service ollama pull llama3.2

# For local Ollama installation
ollama pull llama3.2
```

### Step 3: Upload Your Data

1. Go to Step 2: Upload Data
2. Click "Choose File" or drag-and-drop
3. Select your Excel or CSV file
4. Click "Upload"
5. Wait for confirmation: "File uploaded successfully"

**Supported file formats:**
- `.xlsx` (Excel)
- `.csv` (Comma-separated values)
- `.json` (Advanced users)

### Step 4: Run the AI Mapper

1. Go to Step 3: Schema & Validation
2. Find the "AI Smart Mapper" section
3. Click the dropdown menu and select your model (e.g., `llama3.2`)
4. Click "Suggest Mappings"
5. Wait 30-60 seconds while AI analyzes data
   - Loading spinner appears
   - AI reads column names and compares to standard format
6. Review the suggestions in the table that appears

### Step 5: Review and Apply Suggestions

The AI shows a table like this:

| Your Column Name | AI Suggestion | Confidence |
|-----------------|---------------|------------|
| `age` | `Victim.age` | High |
| `victim_gender` | `Victim.gender` | High |
| `nationality` | `Victim.nationality` | High |
| `trafficker_name` | `Trafficker.name` | Medium |

**What to check:**
- Green/High confidence: Usually correct, safe to accept
- Yellow/Medium confidence: Double-check these
- Red/Low confidence: Review carefully or skip

**To apply changes:**
1. Click "Apply Mapping to File" at the bottom
2. Your file is automatically restructured
3. See: "Mappings applied successfully"
4. Continue to next step in workflow

---

## Frequently Asked Questions

### General Questions

**Q: Do I need to download a model every time?**  
A: No. Once downloaded, the model stays on your computer. You only download once.

**Q: Can I use multiple models?**  
A: Yes. Download several and try them to see which gives the best results.

**Q: Does this cost money?**  
A: No, all models are free and open-source.

**Q: Is my data sent to the internet?**  
A: No. Everything runs locally on your computer. Your data never leaves your system.

**Q: How long does mapping take?**  
A: Usually 30-60 seconds for typical datasets (up to 100 columns).

**Q: Can I undo if the AI makes mistakes?**  
A: Yes. Keep a backup of your original file, or simply re-upload it.

### Troubleshooting

**Q: "AI not available" message?**  
A: Make sure you started with `--profile full`:
```bash
docker-compose down
docker-compose --profile full up --build
```

**Q: Model download is stuck or very slow?**  
A: Check your internet connection. Large models (4GB+) take time.

**Q: "Out of memory" error?**  
A: Your computer might not have enough RAM. Try a smaller model like `gemma2:2b`.

**Q: AI suggestions are wrong or nonsensical?**  
A: Try a different model (e.g., switch from `phi3` to `mistral`). Some models work better for certain data.

**Q: Nothing happens when I click "Suggest Mappings"?**  
A: Check the browser console (press F12) for errors. Also check Docker logs:
```bash
docker-compose logs ollama
```

**Q: Can I manually fix AI suggestions?**  
A: Yes. You can manually edit the mapping suggestions before applying them (feature depends on implementation).

---

## Understanding AI Mapping Results

When the AI finishes, you see a detailed breakdown of its suggestions.

### Interpreting the Output

The AI provides three pieces of information for each column:

1. **Your Original Column Name** - What you called it
2. **Suggested Mapping** - What it should be called in Thinx's format
3. **Confidence Level** - How sure the AI is

### Confidence Levels Explained

| Level | What It Means | What You Should Do |
|-------|--------------|-------------------|
| **High (80-100%)** | AI is very confident | Usually safe to accept |
| **Medium (50-79%)** | AI thinks it's probably right | Review carefully |
| **Low (0-49%)** | AI is guessing | Double-check or manually assign |

### Common Mapping Patterns

The AI recognizes these common patterns:

**Victim Information:**
- `age`, `victim_age`, `Age` → `Victim.age`
- `gender`, `sex`, `victim_gender` → `Victim.gender`
- `nationality`, `country`, `origin` → `Victim.nationality`
- `name`, `victim_name`, `respondent` → `Victim.name`

**Trafficker Information:**
- `trafficker`, `trafficker_name`, `perpetrator` → `Trafficker.name`
- `trafficker_nationality`, `trafficker_country` → `Trafficker.nationality`

**Incident Information:**
- `incident_date`, `date`, `occurrence_date` → `Incident.date`
- `incident_type`, `crime_type`, `abuse_type` → `Incident.type`
- `description`, `incident_description`, `details` → `Incident.description`

**Location Information:**
- `location`, `place`, `border` → `Location.name`
- `location_description`, `place_details` → `Location.description`

### Example Output

```text
Column Mapping Results:
----------------------
Original Column: "age"
Suggested Mapping: "Victim.age"
Confidence: 95% (High)

Original Column: "gender of victim"
Suggested Mapping: "Victim.gender"
Confidence: 90% (High)

Original Column: "country"
Suggested Mapping: "Victim.nationality"
Confidence: 65% (Medium)
Note: Could also be trafficker nationality - please verify

Original Column: "date"
Suggested Mapping: "Incident.date"
Confidence: 45% (Low)
Note: Ambiguous - could be interview date or incident date
```

### JSON Output Format

```json
{
  "victim_id": "victim_id",
  "name": "victim_name", 
  "age": "victim_age",
  "nationality": "victim_nationality",
  "unknown_column": null
}
```

- **Keys**: Your original column names
- **Values**: Suggested CDM field names
- **null**: No good match found (column will be skipped)

### CDM Fields

The Common Data Model includes fields across several entities:

**Victim Fields:**
- `victim_id`, `victim_name`, `victim_age`, `victim_gender`
- `victim_nationality`, `victim_education_level`
- Sensitive: `victim_ethnicity`, `victim_religion`

**Trafficker Fields:**
- `trafficker_id`, `trafficker_name`, `trafficker_gender`
- `trafficker_nationality`, `trafficker_age`

**Incident Fields:**
- `incident_id`, `incident_date`, `incident_location`
- `incident_type`, `border_crossed`

**Exploitation Fields:**
- `exploitation_type`, `duration_days`, `labor_hours_per_day`
- `physical_abuse`, `psychological_abuse`

See `hds_cdm.ttl` for the complete schema definition.

## Best Practices

### 1. Use Descriptive Column Names

The AI works better with clear column names:

**Good**: `victim_age`, `date_of_birth`, `country_of_origin`  
**Poor**: `col1`, `data`, `field_x`

### 2. Review Before Applying

Always review the AI's suggestions before applying them. The AI may:
- Misinterpret ambiguous column names
- Map similar-sounding but semantically different fields
- Miss domain-specific terminology

### 3. Choose the Right Model

- **Start with llama3.2**: Good balance of speed and accuracy
- **Use larger models** if mappings are poor
- **Consider phi3** for faster processing on limited hardware

### 4. Pre-clean Your Data

For best results:
- Ensure column names are in English
- Remove special characters from headers
- Use consistent naming conventions

## Troubleshooting

### "AI service unavailable"

**Problem**: Ollama container is not running

**Solutions**:
```bash
# Check if Ollama is running
docker ps | grep ollama

# Start with full profile
docker-compose --profile full up -d ollama

# Check Ollama logs
docker logs ollama
```

### "No models found"

**Problem**: No models downloaded yet

**Solution**: Download a model using the UI or terminal (see Step 2 above)

### "Model download failed"

**Possible causes**:
- No internet connection
- Invalid model name
- Insufficient disk space
- Ollama service not responding

**Solutions**:
```bash
# Check Ollama status
docker exec -it ollama ollama list

# Verify connectivity
curl http://localhost:11434/api/tags

# Check disk space
df -h
```

### "Mapping took too long / timed out"

**Problem**: Large models or many columns can take time

**Solutions**:
- Use a smaller model (phi3, gemma2:2b)
- Reduce the number of columns in your file
- Increase timeout in `backend/utils/ai_mapper.py`

### Poor Mapping Quality

**If mappings are incorrect**:
1. Try a larger model (llama3:8b, mistral)
2. Rename ambiguous columns in your source file
3. Manually adjust the mappings after AI suggestion
4. Consider mapping manually for critical fields

## Advanced Configuration

### Custom Ollama Host

If running Ollama on a different host:

```python
# In backend/utils/ai_mapper.py
mapper = SmartMapper(host='http://your-ollama-host:11434')
```

Or set environment variable:
```bash
export OLLAMA_HOST=http://your-ollama-host:11434
```

### Adjusting the Prompt

The mapping prompt is in `backend/utils/ai_mapper.py`:

```python
def _build_prompt(self, source_columns, target_schema):
    return f"""
    You are a data integration expert. Map the source columns to the target schema fields.
    
    Source Columns: {json.dumps(source_columns)}
    
    Target Schema (Common Data Model):
    {json.dumps(target_schema)}
    
    Return a JSON object where keys are Source Columns and values are the best matching Target Schema field.
    If no good match exists, map to null.
    """
```

You can modify this to:
- Add examples
- Specify domain context
- Include mapping rules

### Custom Models

You can use any model from Ollama's library:

```bash
# Vision models (if you need image analysis)
ollama pull llava

# Code-focused models
ollama pull codellama

# Multilingual models
ollama pull aya
```

## Privacy and Security

### Data Privacy

- Local Processing: All AI processing happens locally
- No External Calls: Data never leaves your infrastructure
- GDPR Compliant: Suitable for sensitive human trafficking data

### Model Source

- All models are open-source
- Downloaded from Ollama's official library
- Can be audited and verified

### Security Considerations

- Models run in isolated Docker containers
- No internet access required after download
- Logging can be disabled for sensitive operations

## API Reference

### Check AI Status

```http
GET /api/ai-status
```

**Response**:
```json
{
  "available": true,
  "host": "http://ollama:11434"
}
```

### List Models

```http
GET /api/ai-models
```

**Response**:
```json
{
  "success": true,
  "models": [
    {
      "name": "llama3.2:latest",
      "size": 2011051792,
      "modified_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Download Model

```http
POST /api/pull-model
Content-Type: application/json

{
  "model": "llama3.2"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Started downloading model 'llama3.2'..."
}
```

### Suggest Mapping

```http
POST /api/suggest-mapping
Content-Type: application/json

{
  "columns": ["name", "age", "country"],
  "model": "llama3.2"
}
```

**Response**:
```json
{
  "success": true,
  "mapping": {
    "name": "victim_name",
    "age": "victim_age",
    "country": "victim_nationality"
  }
}
```

### Apply Mapping

```http
POST /api/apply-mapping
Content-Type: application/json

{
  "mapping": {
    "name": "victim_name",
    "age": "victim_age"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Column mapping applied successfully"
}
```

## Performance Tips

1. **Model Selection**: Smaller models (2-3GB) are usually sufficient for mapping tasks
2. **Batch Processing**: Process multiple files with the same model to avoid re-loading
3. **Resource Allocation**: Allocate at least 4GB RAM to the Ollama container for smooth operation
4. **SSD Storage**: Store models on SSD for faster loading

## Support

For issues or questions:
1. Check the [main README](../README.md)
2. Review [TROUBLESHOOTING](../README.md#troubleshooting) section
3. Check Ollama documentation: [ollama.com/docs](https://ollama.com/docs)
4. Contact the development team

## References

- **Ollama**: [ollama.com](https://ollama.com)
- **Model Library**: [ollama.com/library](https://ollama.com/library)
- **Llama Models**: [llama.meta.com](https://llama.meta.com)
- **Common Data Model**: See `hds_cdm.ttl` in project root
