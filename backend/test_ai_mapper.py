"""
Test script for AI Mapper refactoring
"""
import json
from utils.ai_mapper import SmartMapper

def test_parse_response():
    """Test the new _parse_response method"""
    mapper = SmartMapper()
    source_columns = ["user_age", "curr_loc", "unknown_field"]
    
    # Test 1: Clean JSON
    print("Test 1: Clean JSON")
    response1 = '{"mapping": {"user_age": "Victim.age", "curr_loc": "Location.name", "unknown_field": null}, "transformations": {"user_age": "to_numerical"}}'
    result1 = mapper._parse_response(response1, source_columns)
    print(f"Result: {json.dumps(result1, indent=2)}")
    print(f"Pass: {'error' not in result1}\n")
    
    # Test 2: JSON with markdown code blocks
    print("Test 2: JSON with markdown code blocks")
    response2 = '```json\n{"mapping": {"user_age": "Victim.age", "curr_loc": "Location.name", "unknown_field": null}, "transformations": {}}\n```'
    result2 = mapper._parse_response(response2, source_columns)
    print(f"Result: {json.dumps(result2, indent=2)}")
    print(f"Pass: {'error' not in result2}\n")
    
    # Test 3: JSON with extra text (should still work if JSON is extractable)
    print("Test 3: JSON with just ``` markers")
    response3 = '```\n{"mapping": {"user_age": "Victim.age", "curr_loc": "Location.name", "unknown_field": null}, "transformations": {}}\n```'
    result3 = mapper._parse_response(response3, source_columns)
    print(f"Result: {json.dumps(result3, indent=2)}")
    print(f"Pass: {'error' not in result3}\n")
    
    # Test 4: Missing columns (should fail validation)
    print("Test 4: Missing columns (should fail)")
    response4 = '{"mapping": {"user_age": "Victim.age"}, "transformations": {}}'
    result4 = mapper._parse_response(response4, source_columns)
    print(f"Result: {json.dumps(result4, indent=2)}")
    print(f"Pass: {'error' in result4 and 'Missing columns' in result4['error']}\n")
    
    # Test 5: Extra columns (should fail validation)
    print("Test 5: Extra columns (should fail)")
    response5 = '{"mapping": {"user_age": "Victim.age", "curr_loc": "Location.name", "unknown_field": null, "extra_col": "Victim.id"}, "transformations": {}}'
    result5 = mapper._parse_response(response5, source_columns)
    print(f"Result: {json.dumps(result5, indent=2)}")
    print(f"Pass: {'error' in result5 and 'Extra columns' in result5['error']}\n")
    
    # Test 6: Invalid JSON (should fail parsing)
    print("Test 6: Invalid JSON (should fail)")
    response6 = '{"mapping": {"user_age": "Victim.age", invalid json'
    result6 = mapper._parse_response(response6, source_columns)
    print(f"Result: {json.dumps(result6, indent=2)}")
    print(f"Pass: {'error' in result6 and 'Invalid JSON' in result6['error']}\n")

    # Test 7: Schema definition (should work after stripping)
    print("Test 7: Complex response that should be cleaned")
    response7 = '```json\n{"mapping": {"user_age": "Victim.age", "curr_loc": "Location.name", "unknown_field": null}, "transformations": {"user_age": "to_numerical"}}\n```'
    result7 = mapper._parse_response(response7, source_columns)
    print(f"Result: {json.dumps(result7, indent=2)}")
    print(f"Pass: {'error' not in result7}\n")

if __name__ == "__main__":
    test_parse_response()
