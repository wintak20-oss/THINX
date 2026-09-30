# Test Data for Learning Thinx

This folder contains safe, realistic example datasets for learning how Thinx works without using real research data.

## Purpose

- **Learn safely** - Practice without risking real research data
- **Test features** - Try AI mapping, transformations, and queries
- **Quick setup** - No need to wait for real database access
- **Show demos** - Present Thinx capabilities to colleagues
- **Troubleshoot** - Verify installation works correctly

## Available Test Files

### Interview_mock_comprehensive.csv (Recommended)

**Description:** A complete, ready-to-use test dataset with 10 realistic human trafficking cases

**Contents:**
- 10 victim case studies (anonymized)
- Multiple incident types: trafficking, smuggling, kidnapping, exploitation
- Covers all data types: victim info, incidents, traffickers, locations
- Properly formatted column names for AI recognition

**Columns included:**

| Category | Columns | Examples |
|----------|---------|----------|
| **Victim** | `victim_id`, `victim_age`, `victim_gender`, `victim_nationality`, `victim_marital_status`, `victim_displacement_status` | 27 years, Male, Eritrea, Single, Refugee |
| **Incident** | `incident_id`, `incident_date`, `incident_type`, `incident_description` | 2023-05-15, Trafficking, Forced labor |
| **Trafficker** | `trafficker_id`, `trafficker_name`, `trafficker_nationality` | T001, Ahmed Hassan, Libyan |
| **Location** | `location_id`, `location_description` | LOC001, Tripoli, Libya |

**Best for:**
- First-time users learning Thinx
- Testing the AI Smart Mapper
- Practicing data transformations
- Demonstrating Thinx to stakeholders

**Expected CDM Mapping Results:**
- `victim_id` → `Victim.id`
- `victim_age` → `Victim.age`
- `victim_gender` → `Victim.gender`
- `victim_nationality` → `Victim.nationality`
- `victim_marital_status` → `Victim.maritalStatus`
- `victim_displacement_status` → `Victim.displacementStatus`
- `incident_id` → `Incident.id`
- `incident_date` → `Incident.date`
- `incident_type` → `Incident.type`
- `incident_description` → `Incident.description`
- `trafficker_id` → `Trafficker.id`
- `trafficker_name` → `Trafficker.name`
- `trafficker_nationality` → `Trafficker.nationality`
- `location_id` → `Location.id`
- `location_description` → `Location.description`

### Legacy Excel Files

**Interview_mock_1.xlsx, Interview_mock_2.xlsx, Interview_mock_3.xlsx**

Purpose: Original test files (may need column name updates)
Status: Legacy format

## Tutorial 1: Test the AI Smart Mapper (15 minutes)

**What you'll learn:** How to use AI to automatically organize data columns

**Prerequisites:**
- Thinx running with `--profile full`
- AI model downloaded (see [AI_MAPPER.md](../docs/AI_MAPPER.md))

**Steps:**

1. **Start Thinx** (if not already running):
   ```bash
   docker-compose --profile full up
   ```

2. **Open the interface:** http://localhost

3. **Upload the test data:**
   - Navigate to Step 2: Upload Data
   - Click "Choose File"
   - Select `Interview_mock_comprehensive.csv`
   - Click "Upload"
   - Wait for: "File uploaded successfully"

4. **Move to Step 3:**
   - Click "Step 3: Schema & Validation"
   - Locate "AI Smart Mapper" section

5. **Download AI Model** (first time only):
   - Find "Download New Model" section
   - Type: `llama3.2`
   - Click "Download"
   - Wait 5-15 minutes
   - When done, click "Refresh"

6. **Run the AI Mapper:**
   - Select "llama3.2" from dropdown
   - Click "Suggest Mappings"
   - Wait 30-60 seconds (loading spinner appears)

7. **Review the results:**
   - View mapping table
   - **Expected mappings:**
     - `victim_age` → `Victim.age`
     - `victim_gender` → `Victim.gender`
     - `victim_nationality` → `Victim.nationality`
     - `incident_type` → `Incident.type`
     - `trafficker_name` → `Trafficker.name`

8. **Apply the mappings:**
   - Click "Apply Mapping to File"
   - Wait for: "Mappings applied successfully"

Success: Your data is now properly structured.

---

## Tutorial 2: Preview and Transform Data (10 minutes)

**What you'll learn:** How to view and modify data before processing

**Prerequisites:**
- Completed Tutorial 1, or uploaded any data file

**Steps:**

1. **Navigate to Step 3** (Schema & Validation)

2. **Preview your data:**
   - Find "Data Transformation Tools" section
   - Click "Preview Data" button
   - View first 10 rows of dataset in table

3. **Try transformation - Age Categories:**
   - In "Select Column" dropdown, choose `victim_age`
   - In "Select Transformation", choose "Numerical → Categorical"
   - Click "Apply Transformation"
   - **Result:** Ages convert to categories
     - 0-17 → "Child"
     - 18-25 → "Young Adult"
     - 26-60 → "Adult"
     - 60+ → "Senior"

4. **Try transformation - Text Case:**
   - Select column: `victim_gender`
   - Select transformation: "Normalize Text Case"
   - Choose: "Title Case"
   - Click "Apply"
   - **Result:** "female" → "Female", "male" → "Male"

5. **Preview again** to see your changes

Note: You can chain multiple transformations - apply one after another.

---

## Tutorial 3: Query the Data (Advanced, 20 minutes)

**What you'll learn:** How to load data into the database and run queries

**Prerequisites:**
- Mock data file
- AllegroGraph running (comes with `--profile full`)

**Steps:**

1. **Create a repository in AllegroGraph:**
   - Open http://localhost:10035
   - Login: `admin` / `admin123`
   - Click "Create Repository"
   - Name: `test_data`
   - Click "Create"

2. **Process and upload mock data:**
   - This step typically uses the `push_to_allegrograph.py` script
   - See main [README.md](../README.md#data-processing-pipeline) for details

3. **Connect Thinx to the test database:**
   - Go to http://localhost
   - Click "Add New Connection"
   - Fill in:
     - Name: `Test Dataset`
     - Server: `allegrograph`
     - Port: `10035`
     - Repository: `test_data`
     - Username: `admin`
     - Password: `admin123`
   - Click "Save Connection"

4. **View the data:**
   - Click "View Data" on your connection
   - View victim statistics and data table

5. **Try a SPARQL query** (Advanced):
   - Open AllegroGraph at http://localhost:10035
   - Select your `test_data` repository
   - Go to "Query" tab
   - Try sample queries from `sparql queries/mock_*.rq` files

**Expected results:** 10 victims, multiple incidents, and various statistics.

## Common Data Model (CDM) Entities

The mock data aligns with these CDM entities:

### Victim

- `id` (required) - Unique identifier
- `age` - Age in years
- `gender` - Gender identity
- `nationality` - Country of origin
- `maritalStatus` - Marital status
- `displacementStatus` - Refugee/IDP status

### Incident

- `id` (required) - Unique identifier
- `date` - Date of incident (YYYY-MM-DD)
- `type` - Type (Trafficking, Smuggling, Kidnapping, etc.)
- `description` - Detailed description

### Trafficker

- `id` (required) - Unique identifier
- `name` - Name of trafficker
- `nationality` - Country of origin

### Location

- `id` (required) - Unique identifier
- `description` - Location name/description

## Data Quality Notes

### Good Column Names (AI will map correctly)

- `victim_age`, `victim_gender`, `victim_nationality`
- `incident_date`, `incident_type`
- `trafficker_name`, `trafficker_nationality`
- `location_description`

### Poor Column Names (AI may struggle)

- `age`, `gender`, `nationality` (ambiguous - could be victim or trafficker)
- `col1`, `col2`, `data` (no semantic meaning)
- `field_x`, `unnamed` (unclear purpose)

## Creating Your Own Mock Data

To create custom test data:

1. **Use descriptive column names** that include entity type
2. **Follow CDM field names** when possible
3. **Include realistic values** for better AI training
4. **Cover multiple scenarios** to test edge cases
5. **Export as CSV or Excel** (CSV preferred for speed)

### Template Structure

If creating your own test file:

```csv
victim_id,victim_age,victim_gender,victim_nationality,incident_id,incident_type,incident_date
V001,25,Female,Syrian,INC001,Trafficking,2024-01-15
V002,32,Male,Eritrean,INC002,Smuggling,2024-02-20
V003,19,Female,Nigerian,INC003,Exploitation,2024-03-10
```

**Tips for good column names:**
- Include entity type: `victim_age`, not just `age`
- Be descriptive: `incident_date`, not `date`
- Use underscores: `trafficker_name`, not `traffickername`
- Be consistent: `victim_gender`, not `gender_victim`

---

## Troubleshooting

### "No data file found" Error

**Cause:** Attempted to preview/transform data before uploading file

**Solution:**
1. Go to Step 2: Upload Data
2. Click "Choose File"
3. Select your mock data file
4. Click "Upload"
5. Wait for confirmation message
6. Try Step 3 again

---

### AI Mapping Returns "null" or Empty for All Fields

**Cause:** AI couldn't understand your column names

**Solutions:**

**Option 1 - Use better column names:**
- Change `age` → `victim_age`
- Change `gender` → `victim_gender`
- Change `name` → `trafficker_name`

**Option 2 - Try a different AI model:**
1. Download a larger model: `mistral` or `llama3:8b`
2. These understand context better
3. Re-run the mapper

**Option 3 - Check your data format:**
- Is it a valid CSV or Excel file?
- Do you have column headers in the first row?
- Are there any special characters in column names?

---

### Transformation Fails or Shows Error

**Common causes and fixes:**

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "Column not found" | Column name typo or doesn't exist | Check spelling, refresh preview |
| "Invalid data type" | Wrong transformation for data type | Can't categorize text, can't normalize numbers |
| "No data loaded" | File wasn't uploaded properly | Re-upload file, check file format |

---

### Expected Mappings Don't Appear

**Example:** `victim_age` should map to `Victim.age` but shows something else

**Debugging steps:**

1. **Check your column name format:**
   - Good: `victim_age`, `victim_gender`, `victim_nationality`
   - Bad: `age`, `col1`, `data`

2. **Try a different AI model:**
   - `llama3.2` is good for most cases
   - `mistral` is better for complex/ambiguous names

3. **Manually verify the CDM:**
   - Check [README.md](../README.md) for correct entity field names
   - Entities: `Victim`, `Incident`, `Trafficker`, `Location`
   - Fields: `age`, `gender`, `nationality`, `name`, etc.

4. **Check the AI response:**
   - Does it explain why it chose that mapping?
   - Is there a confidence score?

---

## Getting Help

### Still Stuck?

1. **Check main documentation:**
   - [README.md](../README.md) - Complete user guide
   - [QUICK_START.md](../QUICK_START.md) - Setup troubleshooting
   - [AI_MAPPER.md](../docs/AI_MAPPER.md) - AI-specific help

2. **Check logs for errors:**
   ```bash
   # View backend logs
   docker-compose logs backend
   
   # View all logs
   docker-compose logs
   ```

3. **Verify your setup:**
   ```bash
   # Check all containers are running
   docker-compose ps
   
   # Should see: frontend, backend, allegrograph, ollama (if full profile)
   ```

4. **Try a fresh start:**
   ```bash
   docker-compose down -v
   docker-compose --profile full up --build
   ```

### Report Issues

When asking for help, include:
- Your operating system (Windows/Mac/Linux)
- Which tutorial you were following
- The exact error message
- What step you were on when it failed
