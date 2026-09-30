<template>
  <div class="workflow-manager">
    <!-- Workflow Progress Tracker -->
      <div class="workflow-progress">
        <div class="progress-steps">
          <div 
            v-for="step in steps" 
            :key="step.id"
            :class="['progress-step', { 
              'completed': step.id < currentStep, 
              'active': step.id === currentStep 
            }]"
          >
            <div class="step-circle">{{ step.id }}</div>
            <div class="step-label">{{ step.label }}</div>
          </div>
        </div>
      </div>

      <!-- Step 1: Connection Manager -->
      <div v-show="currentStep === 1" class="workflow-section">
        <div class="section-header">
          <i class="fas fa-plug"></i>
          <div>
            <h2>Step 1: Configure AllegroGraph Connection</h2>
            <p class="text-muted mb-0">Set up connection to your AllegroGraph database</p>
          </div>
        </div>
        
        <ConnectionManager :user="user" />
        
        <div class="step-actions">
          <button 
            class="btn btn-primary btn-lg" 
            @click="nextStep"
          >
            Continue to Upload Data <i class="fas fa-arrow-right ms-2"></i>
          </button>
        </div>
      </div>

      <!-- Step 2: Upload Data -->
      <div v-show="currentStep === 2" class="workflow-section">
        <div class="section-header">
          <i class="fas fa-cloud-upload-alt"></i>
          <div>
            <h2>Step 2: Upload & Inspect Data</h2>
            <p class="text-muted mb-0">Upload your interview data file (Excel or JSON format)</p>
          </div>
        </div>

        <div class="upload-zone" @click="triggerFileUpload" @dragover.prevent @drop.prevent="handleFileDrop">
          <i class="fas fa-cloud-upload-alt upload-icon"></i>
          <h4>Drop your file here or click to browse</h4>
          <p class="text-muted">Supported formats: .xlsx, .xls, .json</p>
          <p class="text-muted"><small>Maximum file size: 50MB</small></p>
          <input 
            ref="fileInput" 
            type="file" 
            accept=".xlsx,.xls,.json" 
            @change="handleFileSelect"
            style="display: none;"
          >
        </div>

        <div v-if="uploadedFile" class="alert alert-success">
          <i class="fas fa-check-circle me-2"></i>
          File uploaded: <strong>{{ uploadedFile.name }}</strong> ({{ formatFileSize(uploadedFile.size) }})
        </div>

        <div class="step-actions">
          <button class="btn btn-secondary" @click="previousStep">
            <i class="fas fa-arrow-left me-2"></i> Back
          </button>
          <button 
            class="btn btn-primary btn-lg" 
            @click="nextStep"
            :disabled="!uploadedFile"
          >
            Continue to Schema Validation <i class="fas fa-arrow-right ms-2"></i>
          </button>
        </div>
      </div>

      <!-- Step 3: Schema & Validation -->
      <div v-show="currentStep === 3" class="workflow-section">
        <div class="section-header">
          <i class="fas fa-sitemap"></i>
          <div>
            <h2>Step 3: Common Data Model Schema & Validation</h2>
            <p class="text-muted mb-0">Understand the data structure and validate your file</p>
          </div>
        </div>

        <div class="alert alert-info">
          <i class="fas fa-info-circle me-2"></i>
          <strong>About the Common Data Model:</strong> Thinx uses a standardized schema (hds_cdm.ttl) 
          for human trafficking research data. Each field is classified by sensitivity level and GDPR category.
        </div>

        <!-- Schema Visualization -->
        <div v-if="schema" class="schema-container mb-4">
          <!-- AI Mapping Suggestion -->
          <div v-if="aiAvailable" class="ai-mapping-section mb-4">
            <div class="card border-primary">
              <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                <span><i class="fas fa-robot me-2"></i> AI Smart Mapper</span>
                <span class="badge bg-light text-primary">Experimental</span>
              </div>
              <div class="card-body">
                <!-- Information Section -->
                <div class="alert alert-info mb-3">
                  <h6 class="alert-heading"><i class="fas fa-info-circle me-2"></i>About AI Smart Mapper</h6>
                  <p class="mb-2">
                    The AI Smart Mapper uses a local Large Language Model (LLM) via Ollama to automatically analyze your data columns 
                    and suggest the best mappings to the Common Data Model fields. This helps you quickly structure your data without manual mapping.
                  </p>
                  <details>
                    <summary style="cursor: pointer;" class="text-primary"><strong>How it works & Where to find models</strong></summary>
                    <ul class="mt-2 mb-0">
                      <li><strong>Step 1:</strong> Download a model from <a href="https://ollama.com/library" target="_blank">Ollama Library</a></li>
                      <li><strong>Step 2:</strong> Enter the model name below (e.g., "llama3.2", "mistral", "phi3")</li>
                      <li><strong>Step 3:</strong> Click "Download Model" and wait for it to complete</li>
                      <li><strong>Step 4:</strong> Select the model and use "Suggest Mappings" to analyze your data</li>
                      <li><strong>Recommended models:</strong> llama3.2 (2GB), phi3 (2.3GB), mistral (4GB)</li>
                      <li>Larger models provide better accuracy but take longer to download</li>
                    </ul>
                  </details>
                </div>

                <!-- Model Download Section -->
                <div class="model-download-section mb-4">
                  <h6><i class="fas fa-download me-2"></i>Download New Model</h6>
                  <div class="row g-2">
                    <div class="col-md-8">
                      <input 
                        v-model="newModelName" 
                        type="text" 
                        class="form-control" 
                        placeholder="e.g., llama3.2, mistral, phi3"
                        :disabled="pullingModel"
                      />
                      <small class="text-muted">
                        Browse available models at <a href="https://ollama.com/library" target="_blank">ollama.com/library</a>
                      </small>
                    </div>
                    <div class="col-md-4">
                      <button 
                        class="btn btn-success w-100" 
                        @click="downloadModel"
                        :disabled="!newModelName || pullingModel"
                      >
                        <i :class="['fas', pullingModel ? 'fa-spinner fa-spin' : 'fa-download', 'me-2']"></i>
                        {{ pullingModel ? 'Downloading...' : 'Download' }}
                      </button>
                    </div>
                  </div>
                  <div v-if="pullingModel" class="mt-3">
                    <div class="progress" style="height: 25px;">
                      <div class="progress-bar progress-bar-striped progress-bar-animated bg-success" 
                           role="progressbar" 
                           style="width: 100%">
                        <i class="fas fa-download me-2"></i> Downloading model... This may take 5-15 minutes
                      </div>
                    </div>
                  </div>
                  <div v-if="pullStatus" class="alert mt-2" :class="pullStatus.success ? 'alert-success' : 'alert-info'">
                    <small>{{ pullStatus.message }}</small>
                  </div>
                </div>

                <!-- Model Selection Section -->
                <div class="model-selection-section mb-3">
                  <h6><i class="fas fa-brain me-2"></i>Select Model for Mapping</h6>
                  <div class="row g-2">
                    <div class="col-md-8">
                      <select v-model="selectedModel" class="form-select">
                        <option value="" disabled>Select AI Model</option>
                        <option v-for="model in aiModels" :key="model.name" :value="model.name">
                          {{ model.name }} ({{ formatSize(model.size) }})
                        </option>
                      </select>
                    </div>
                    <div class="col-md-4">
                      <button 
                        class="btn btn-outline-secondary w-100" 
                        @click="refreshModels"
                        title="Refresh Model List"
                      >
                        <i class="fas fa-sync-alt me-2"></i> Refresh
                      </button>
                    </div>
                  </div>
                </div>

                <div v-if="aiModels.length === 0" class="alert alert-warning">
                  <i class="fas fa-exclamation-triangle me-2"></i>
                  <strong>No models found.</strong> Download a model using the form above to get started.
                </div>

                <div class="d-flex gap-2">
                  <button 
                    class="btn btn-outline-primary flex-grow-1" 
                    @click="runSmartMapping"
                    :disabled="mappingLoading || !selectedModel"
                  >
                    <i :class="['fas', mappingLoading ? 'fa-spinner fa-spin' : 'fa-magic', 'me-2']"></i>
                    {{ mappingLoading ? 'Analyzing... (30+ seconds)' : 'Suggest Mappings' }}
                  </button>
                  <button 
                    class="btn btn-info" 
                    @click="showSchemaReference = !showSchemaReference"
                    title="View Valid CDM Fields"
                  >
                    <i class="fas fa-book me-2"></i> Schema Reference
                  </button>
                  <button 
                    v-if="mappingLoading"
                    class="btn btn-danger" 
                    @click="stopMapping"
                    title="Stop AI Analysis"
                  >
                    <i class="fas fa-stop me-2"></i> Stop
                  </button>
                </div>

                <!-- Schema Reference Modal -->
                <div v-if="showSchemaReference" class="schema-reference-modal mt-3">
                  <div class="card border-info">
                    <div class="card-header bg-info text-white d-flex justify-content-between align-items-center">
                      <span><i class="fas fa-book me-2"></i> Common Data Model (CDM) Schema Reference</span>
                      <button class="btn btn-sm btn-light" @click="showSchemaReference = false">
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
                    <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                      <div class="alert alert-light">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Use this reference to verify AI suggestions.</strong> The AI should only suggest fields from these valid CDM categories.
                      </div>
                      
                      <!-- Victim Fields -->
                      <div class="schema-ref-section mb-3">
                        <h6 class="text-primary"><i class="fas fa-user me-2"></i>Victim</h6>
                        <div class="schema-fields-list">
                          <span class="badge bg-light text-dark me-2 mb-2">id</span>
                          <span class="badge bg-light text-dark me-2 mb-2">age</span>
                          <span class="badge bg-light text-dark me-2 mb-2">ageGroup</span>
                          <span class="badge bg-light text-dark me-2 mb-2">gender</span>
                          <span class="badge bg-light text-dark me-2 mb-2">nationality</span>
                          <span class="badge bg-light text-dark me-2 mb-2">ethnicity</span>
                          <span class="badge bg-light text-dark me-2 mb-2">maritalStatus</span>
                          <span class="badge bg-light text-dark me-2 mb-2">parentalStatus</span>
                          <span class="badge bg-light text-dark me-2 mb-2">name</span>
                          <span class="badge bg-light text-dark me-2 mb-2">description</span>
                          <span class="badge bg-light text-dark me-2 mb-2">displacementStatus</span>
                          <span class="badge bg-light text-dark me-2 mb-2">captivityStatus</span>
                          <span class="badge bg-light text-dark me-2 mb-2">category</span>
                        </div>
                      </div>
                      
                      <!-- Incident Fields -->
                      <div class="schema-ref-section mb-3">
                        <h6 class="text-danger"><i class="fas fa-exclamation-triangle me-2"></i>Incident</h6>
                        <div class="schema-fields-list">
                          <span class="badge bg-light text-dark me-2 mb-2">id</span>
                          <span class="badge bg-light text-dark me-2 mb-2">date</span>
                          <span class="badge bg-light text-dark me-2 mb-2">type</span>
                          <span class="badge bg-light text-dark me-2 mb-2">description</span>
                          <span class="badge bg-light text-dark me-2 mb-2">timeRange</span>
                        </div>
                      </div>
                      
                      <!-- Location Fields -->
                      <div class="schema-ref-section mb-3">
                        <h6 class="text-success"><i class="fas fa-map-marker-alt me-2"></i>Location</h6>
                        <div class="schema-fields-list">
                          <span class="badge bg-light text-dark me-2 mb-2">id</span>
                          <span class="badge bg-light text-dark me-2 mb-2">description</span>
                        </div>
                      </div>
                      
                      <!-- Trafficker Fields -->
                      <div class="schema-ref-section mb-3">
                        <h6 class="text-warning"><i class="fas fa-user-secret me-2"></i>Trafficker</h6>
                        <div class="schema-fields-list">
                          <span class="badge bg-light text-dark me-2 mb-2">age</span>
                          <span class="badge bg-light text-dark me-2 mb-2">ageGroup</span>
                          <span class="badge bg-light text-dark me-2 mb-2">gender</span>
                          <span class="badge bg-light text-dark me-2 mb-2">nationality</span>
                          <span class="badge bg-light text-dark me-2 mb-2">ethnicity</span>
                          <span class="badge bg-light text-dark me-2 mb-2">category</span>
                        </div>
                      </div>
                      
                      <!-- Record Fields -->
                      <div class="schema-ref-section mb-3">
                        <h6 class="text-info"><i class="fas fa-file-alt me-2"></i>Record (Metadata)</h6>
                        <div class="schema-fields-list">
                          <span class="badge bg-light text-dark me-2 mb-2">id</span>
                          <span class="badge bg-light text-dark me-2 mb-2">date</span>
                          <span class="badge bg-light text-dark me-2 mb-2">inputBy</span>
                          <span class="badge bg-light text-dark me-2 mb-2">source</span>
                          <span class="badge bg-light text-dark me-2 mb-2">updatedAt</span>
                          <span class="badge bg-light text-dark me-2 mb-2">timeRange</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="mappingLoading" class="mt-3">
                  <div class="ai-progress-container">
                    <div class="progress mb-2" style="height: 25px;">
                      <div class="progress-bar progress-bar-striped progress-bar-animated bg-primary" 
                           role="progressbar" 
                           :style="`width: ${mappingProgress}%`">
                        <i class="fas fa-brain me-2"></i> {{ mappingStatusText }}
                      </div>
                    </div>
                    <div class="ai-progress-steps">
                      <div v-for="(step, index) in aiProgressSteps" 
                           :key="index" 
                           :class="['progress-step-item', { 'completed': step.completed, 'active': step.active }]">
                        <i :class="['fas', step.completed ? 'fa-check-circle' : (step.active ? 'fa-spinner fa-spin' : 'fa-circle'), 'me-1']"></i>
                        {{ step.text }}
                      </div>
                    </div>
                  </div>
                  <small class="text-muted d-block mt-2">
                    <i class="fas fa-info-circle me-1"></i>
                    Time varies by model: 1-5 minutes for larger models. Using: <strong>{{ selectedModel }}</strong>
                    <br>
                    <i class="fas fa-lightbulb me-1"></i>
                    <em>Tip: Click "Stop" if taking too long, then try a smaller model like phi3 or gemma2:2b</em>
                  </small>
                </div>
                
                <div v-if="suggestedMapping" class="mt-3">
                  <h6>Suggested Mappings:</h6>
                  <div class="table-responsive">
                    <table class="table table-sm table-bordered">
                      <thead>
                        <tr>
                          <th>Your Column</th>
                          <th>Mapped To (CDM)</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(target, source) in suggestedMapping" :key="source">
                          <td>{{ source }}</td>
                          <td>
                            <span v-if="target" class="badge bg-success">{{ target }}</span>
                            <span v-else class="badge bg-secondary">No match</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <button 
                    class="btn btn-success mt-2" 
                    @click="applyMapping"
                    :disabled="applyingMapping"
                  >
                    <i :class="['fas', applyingMapping ? 'fa-spinner fa-spin' : 'fa-check', 'me-2']"></i>
                    Apply Mapping to File
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Data Transformation Tools -->
          <div class="transformation-tools-section mb-4">
            <div class="card border-info">
              <div class="card-header bg-info text-white">
                <div class="d-flex justify-content-between align-items-center">
                  <h5 class="mb-0"><i class="fas fa-tools me-2"></i> Data Transformation Tools <span class="badge bg-light text-info ms-2">Optional</span></h5>
                </div>
                <small class="d-block mt-1">Clean and standardize your data before mapping</small>
              </div>
              <div class="card-body">
                <div class="alert alert-light border-info mb-3">
                  <i class="fas fa-info-circle text-info me-2"></i>
                  <strong>Optional Step:</strong> Use these tools to clean and standardize your data before mapping. 
                  Common operations: fill missing values, normalize text, convert data types.
                </div>

                <!-- Data Preview Button -->
                <div class="mb-3">
                  <div class="alert alert-warning" v-if="!uploadedFile">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Required:</strong> Upload a data file in Step 2 first to use transformation tools.
                  </div>
                  <button 
                    class="btn btn-info btn-lg" 
                    @click="loadDataPreview"
                    :disabled="loadingPreview || !uploadedFile"
                  >
                    <i :class="['fas', loadingPreview ? 'fa-spinner fa-spin' : 'fa-table', 'me-2']"></i>
                    {{ loadingPreview ? 'Loading Preview...' : 'Load Data Preview' }}
                  </button>
                  <small class="text-muted ms-3" v-if="uploadedFile">Click to view first 10 rows of your data</small>
                </div>

                <div v-if="dataPreview" class="data-preview-section">
                  <h6><i class="fas fa-table me-2"></i>Data Preview (First 10 rows, Total: {{ dataPreview.row_count }})</h6>
                  <div class="table-responsive mb-3">
                    <table class="table table-sm table-bordered">
                      <thead>
                        <tr>
                          <th v-for="col in dataPreview.columns" :key="col">{{ col }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(row, idx) in dataPreview.preview" :key="idx">
                          <td v-for="col in dataPreview.columns" :key="col">{{ row[col] }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <!-- Transformation Options -->
                  <div class="transform-options mt-4 p-4 bg-light rounded">
                    <h5 class="mb-3">
                      <i class="fas fa-magic me-2 text-primary"></i>
                      Transform Column Data
                    </h5>
                    <p class="text-muted mb-3">Select a column and choose a transformation to apply. Changes are saved immediately to your file.</p>
                    
                    <div class="row g-3">
                      <!-- Column Selection -->
                      <div class="col-md-5">
                        <label for="transform-column-select" class="form-label fw-bold">
                          <i class="fas fa-columns me-1"></i> 1. Select Column
                        </label>
                        <select id="transform-column-select" v-model="transformColumn" class="form-select form-select-lg">
                          <option value="">-- Choose a column to transform --</option>
                          <option v-for="col in dataPreview.columns" :key="col" :value="col">
                            {{ col }}
                          </option>
                        </select>
                      </div>

                      <!-- Transformation Type -->
                      <div class="col-md-5">
                        <label for="transform-type-select" class="form-label fw-bold">
                          <i class="fas fa-cog me-1"></i> 2. Choose Transformation
                        </label>
                        <select id="transform-type-select" v-model="transformType" class="form-select form-select-lg" :disabled="!transformColumn">
                          <option value="">-- Choose operation --</option>
                          <option value="fill_missing">🔧 Fill Missing/Empty Values</option>
                          <option value="clean_text">🧹 Clean Text (remove special chars)</option>
                          <option value="normalize_case">📝 Normalize Text Case</option>
                          <option value="format_date">📅 Format Dates</option>
                          <option value="to_categorical">📊 Number → Category</option>
                          <option value="to_numerical">🔢 Category → Number</option>
                        </select>
                      </div>

                      <!-- Apply Button -->
                      <div class="col-md-2 d-flex align-items-end">
                        <button 
                          class="btn btn-success btn-lg w-100" 
                          @click="applyTransformation"
                          :disabled="!transformColumn || !transformType || transforming"
                        >
                          <i :class="['fas', transforming ? 'fa-spinner fa-spin' : 'fa-check', 'me-2']"></i>
                          {{ transforming ? 'Applying...' : 'Apply' }}
                        </button>
                      </div>
                    </div>

                    <!-- Transformation Options Details -->
                    <div v-if="transformType" class="alert alert-info mt-3">
                      <strong><i class="fas fa-lightbulb me-2"></i>What this does:</strong>
                      <div v-if="transformType === 'fill_missing'" class="mt-2">
                        Replaces all empty, null, or missing values with "Unknown" (or your custom value)
                      </div>
                      <div v-else-if="transformType === 'clean_text'" class="mt-2">
                        Removes special characters and extra whitespace. Example: "Name!!!  " → "Name"
                      </div>
                      <div v-else-if="transformType === 'normalize_case'" class="mt-2">
                        Standardizes text capitalization. Example: "john SMITH" → "John Smith" (Title Case)
                      </div>
                      <div v-else-if="transformType === 'format_date'" class="mt-2">
                        Converts all dates to standard format (YYYY-MM-DD). Example: "12/31/2023" → "2023-12-31"
                      </div>
                      <div v-else-if="transformType === 'to_categorical'" class="mt-2">
                        <strong class="text-danger">⚠️ For numerical columns only!</strong><br>
                        Converts numbers to age categories. Example: Age 25 → "Young Adult" (0-18=Child, 19-35=Young Adult, 36-60=Adult, 60+=Senior)<br>
                        <em class="text-muted">Don't use this on text columns like Yes/No. Use "Category → Number" for those.</em>
                      </div>
                      <div v-else-if="transformType === 'to_numerical'" class="mt-2">
                        Converts text categories to numbers. Example: "Yes" → 1, "No" → 0 OR "Male" → 0, "Female" → 1, "Other" → 2<br>
                        <em class="text-muted">Use this for Yes/No or Male/Female/Other columns.</em>
                      </div>
                      <div v-else-if="transformType === 'normalize_case'">
                        <strong>Text Case:</strong> Standardizes capitalization (Title Case, UPPER CASE, or lower case)
                        <div class="mt-2">
                          <select v-model="transformOptions.case" class="form-select form-select-sm">
                            <option value="title">Title Case</option>
                            <option value="upper">UPPER CASE</option>
                            <option value="lower">lower case</option>
                          </select>
                        </div>
                      </div>
                      <div v-else-if="transformType === 'format_date'">
                        <strong>Date Format:</strong> Standardizes dates to YYYY-MM-DD format
                      </div>
                      <div v-else-if="transformType === 'clean_text'">
                        <strong>Clean Text:</strong> Removes special characters and extra spaces
                      </div>
                      <div v-else-if="transformType === 'fill_missing'">
                        <strong>Fill Missing:</strong> Replaces empty/null values with "Unknown"
                      </div>
                    </div>

                    <!-- Transformation Result -->
                    <div v-if="transformResult" class="mt-3">
                      <div class="alert" :class="transformResult.success ? 'alert-success' : 'alert-danger'">
                        <h6 class="alert-heading">
                          <i :class="['fas', transformResult.success ? 'fa-check-circle' : 'fa-exclamation-circle', 'me-2']"></i>
                          {{ transformResult.success ? 'Transformation Applied' : 'Transformation Failed' }}
                        </h6>
                        <p class="mb-2">{{ transformResult.message }}</p>
                        <div v-if="transformResult.preview && transformResult.preview.length" class="mt-3">
                          <strong class="d-block mb-2"><i class="fas fa-eye me-1"></i> Preview (First 5 values):</strong>
                          <div class="bg-white p-2 rounded border">
                            <code class="text-dark">{{ transformResult.preview.map(v => v === null ? '[empty]' : v).join('  |  ') }}</code>
                          </div>
                        </div>
                        <button class="btn btn-sm btn-outline-success mt-2" @click="loadDataPreview">
                          <i class="fas fa-sync me-1"></i> Refresh Preview
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-for="(entityData, entityName) in schema" :key="entityName" class="schema-entity">
            <div class="schema-entity-title">
              <i class="fas fa-cube me-2"></i>{{ entityName }}
              <span class="badge bg-secondary ms-2">{{ entityData.fields.length }} fields</span>
            </div>
            <div v-if="entityData.description" class="schema-entity-description">
              {{ entityData.description }}
            </div>
            <div class="schema-fields">
              <div v-for="field in entityData.fields" :key="field.name" class="schema-field">
                <div v-if="field.sensitive" class="sensitive-indicator">
                  <i class="fas fa-lock me-1"></i> SENSITIVE
                </div>
                <div class="field-name">{{ field.name }}</div>
                <div class="field-meta">
                  <span :class="['field-badge', field.required ? 'badge-required' : 'badge-optional']">
                    {{ field.required ? 'Required' : 'Optional' }}
                  </span>
                  <span class="field-badge bg-secondary text-white">{{ field.type }}</span>
                  <span v-if="field.gdpr_category" :class="['field-badge', getGdprBadgeClass(field.gdpr_category)]">
                    {{ getGdprLabel(field.gdpr_category) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Validation Section -->
        <div class="validation-section mt-5 pt-4">
          <h3 class="mb-4"><i class="fas fa-check-double me-2"></i> Data Validation</h3>
          
          <button class="btn btn-primary mb-4" @click="runValidation" :disabled="validating || !uploadedFile">
            <i :class="['fas', validating ? 'fa-spinner fa-spin' : 'fa-play-circle', 'me-2']"></i>
            {{ validating ? 'Validating...' : 'Validate Uploaded File' }}
          </button>

          <div v-if="validationResult" class="validation-panel">
            <h5 class="mb-3"><i class="fas fa-chart-bar me-2"></i> Validation Summary</h5>
            <div class="alert" :class="validationResult.passed ? 'alert-success' : 'alert-warning'">
              <div><strong>Status:</strong> {{ validationResult.passed ? 'Passed' : 'Issues Found' }}</div>
              <div><strong>Total Rows:</strong> {{ validationResult.total_rows }}</div>
              <div><strong>Valid Rows:</strong> {{ validationResult.valid_rows }}</div>
            </div>

            <div v-if="validationResult.errors.length" class="alert alert-danger mt-3">
              <h6><i class="fas fa-exclamation-circle me-2"></i> Validation Errors</h6>
              <ul class="mb-0">
                <li v-for="(error, index) in validationResult.errors" :key="index">{{ error }}</li>
              </ul>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <button class="btn btn-secondary" @click="previousStep">
            <i class="fas fa-arrow-left me-2"></i> Back
          </button>
          <button class="btn btn-primary btn-lg" @click="nextStep">
            Continue to Processing <i class="fas fa-arrow-right ms-2"></i>
          </button>
        </div>
      </div>

      <!-- Step 4: Process & Clean Data -->
      <div v-show="currentStep === 4" class="workflow-section">
        <div class="section-header">
          <i class="fas fa-cogs"></i>
          <div>
            <h2>Step 4: Process & Clean Data</h2>
            <p class="text-muted mb-0">Clean data, merge duplicates, and prepare final JSON output</p>
          </div>
        </div>

        <div class="alert alert-info">
          <i class="fas fa-info-circle me-2"></i>
          This step executes the data processing pipeline, which includes: data cleaning and standardization, 
          duplicate detection and merging, and generation of final JSON output ready for RDF conversion.
        </div>

        <div class="card mb-3">
          <div class="card-body">
            <h5 class="card-title"><i class="fas fa-tasks me-2"></i> Processing Pipeline</h5>
            <div class="processing-steps">
              <div class="processing-step">
                <div class="step-number">1</div>
                <div class="step-content">
                  <strong>Data Cleaning & Standardization</strong>
                  <p class="text-muted mb-0">Standardize formats, handle missing values, and normalize data fields</p>
                </div>
              </div>
              <div class="processing-step">
                <div class="step-number">2</div>
                <div class="step-content">
                  <strong>Duplicate Detection & Merging</strong>
                  <p class="text-muted mb-0">Identify and merge duplicate victim records to ensure data integrity</p>
                </div>
              </div>
              <div class="processing-step">
                <div class="step-number">3</div>
                <div class="step-content">
                  <strong>JSON Output Generation</strong>
                  <p class="text-muted mb-0">Create final structured JSON with deduplicated victim records</p>
                </div>
              </div>
              <div class="processing-step">
                <div class="step-number">4</div>
                <div class="step-content">
                  <strong>Quality Assurance</strong>
                  <p class="text-muted mb-0">Validate data integrity and prepare for RDF conversion</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <button 
          class="btn btn-primary btn-lg mb-3" 
          @click="runAllProcessing" 
          :disabled="processing || !uploadedFile"
        >
          <i :class="['fas', processing ? 'fa-spinner fa-spin' : 'fa-play-circle', 'me-2']"></i>
          {{ processing ? 'Processing...' : 'Start Data Processing' }}
        </button>

        <div v-if="processingResult" class="alert" :class="processingResult.success ? 'alert-success' : 'alert-danger'">
          <h6><i :class="['fas', processingResult.success ? 'fa-check-circle' : 'fa-exclamation-circle', 'me-2']"></i>
            {{ processingResult.success ? 'Processing Complete' : 'Processing Failed' }}
          </h6>
          <p class="mb-2">{{ processingResult.message }}</p>
          <pre v-if="processingResult.output" class="output-box">{{ processingResult.output }}</pre>
        </div>

        <div class="step-actions">
          <button class="btn btn-secondary" @click="previousStep">
            <i class="fas fa-arrow-left me-2"></i> Back
          </button>
          <button class="btn btn-primary btn-lg" @click="nextStep">
            Continue to Export <i class="fas fa-arrow-right ms-2"></i>
          </button>
        </div>
      </div>

      <!-- Step 5: Push to AllegroGraph -->
      <div v-show="currentStep === 5" class="workflow-section">
        <div class="section-header">
          <i class="fas fa-database"></i>
          <div>
            <h2>Step 5: Push to AllegroGraph</h2>
            <p class="text-muted mb-0">Select target repository and export RDF data</p>
          </div>
        </div>

        <div class="form-group mb-4">
          <label for="targetConnection" class="form-label">
            <strong>Select Target AllegroGraph Connection</strong>
          </label>
          <select 
            id="targetConnection" 
            v-model="selectedConnectionId" 
            class="form-select"
          >
            <option value="">-- Select a connection --</option>
            <option 
              v-for="conn in allegroGraphConnections" 
              :key="conn.id" 
              :value="conn.id"
            >
              {{ conn.name }} ({{ conn.host }}:{{ conn.port }}/{{ conn.repository }})
            </option>
          </select>
          <small class="text-muted">
            Choose which AllegroGraph repository to upload your RDF data to
          </small>
        </div>

        <div v-if="selectedConnectionId && !processingResult" class="success-box">
          <i class="fas fa-check-circle"></i>
          <h4>Ready to Export</h4>
          <p>Your processed RDF data will be pushed to the selected repository.</p>
        </div>

        <div v-if="processingResult" class="alert mt-4" :class="processingResult.success ? 'alert-success' : 'alert-danger'">
          <h6>
            <i :class="['fas', processingResult.success ? 'fa-check-circle' : 'fa-exclamation-circle', 'me-2']"></i>
            {{ processingResult.success ? 'Success' : 'Error' }}
          </h6>
          <p class="mb-2">{{ processingResult.message }}</p>
          <pre v-if="processingResult.output" class="output-box">{{ processingResult.output }}</pre>
        </div>

        <div class="step-actions">
          <button class="btn btn-secondary" @click="previousStep">
            <i class="fas fa-arrow-left me-2"></i> Back
          </button>
          <button 
            class="btn btn-success btn-lg" 
            @click="handleExport"
            :disabled="!selectedConnectionId"
          >
            <i class="fas fa-upload me-2"></i> Push to AllegroGraph
          </button>
        </div>
      </div>
  </div>
</template>

<script>
import ConnectionManager from './ConnectionManager.vue'
import api from '../services/api'

export default {
  name: 'WorkflowManager',
  
  components: {
    ConnectionManager
  },

  props: {
    user: {
      type: Object,
      required: false
    }
  },

  data() {
    return {
      currentStep: 1,
      uploadedFile: null,
      selectedConnectionId: '',
      allegroGraphConnections: [],
      schema: null,
      validating: false,
      validationResult: null,
      processing: false,
      processingResult: null,
      aiAvailable: false,
      aiModels: [],
      selectedModel: '',
      mappingLoading: false,
      applyingMapping: false,
      suggestedMapping: null,
      newModelName: '',
      pullingModel: false,
      pullStatus: null,
      // AI Progress tracking
      mappingProgress: 0,
      mappingStatusText: '',
      mappingAbortController: null,
      aiProgressSteps: [
        { text: 'Preparing data...', completed: false, active: false },
        { text: 'Loading AI model...', completed: false, active: false },
        { text: 'Analyzing columns...', completed: false, active: false },
        { text: 'Generating mappings...', completed: false, active: false }
      ],
      showSchemaReference: false,
      // Data transformation
      dataPreview: null,
      loadingPreview: false,
      transformColumn: '',
      transformType: '',
      transformOptions: {
        case: 'title'
      },
      transforming: false,
      transformResult: null,
      steps: [
        { id: 1, label: 'Connection Setup' },
        { id: 2, label: 'Upload Data' },
        { id: 3, label: 'Schema & Validation' },
        { id: 4, label: 'Process & Generate RDF' },
        { id: 5, label: 'Push to AllegroGraph' }
      ]
    }
  },

  mounted() {
    this.loadConnections()
    this.loadSchema()
    this.checkAiStatus()
  },

  methods: {
    async checkAiStatus() {
      try {
        const status = await api.checkAiStatus()
        this.aiAvailable = status.available
        if (this.aiAvailable) {
          this.refreshModels()
        }
      } catch (error) {
        // AI service not available - this is optional
        this.aiAvailable = false
      }
    },

    async refreshModels() {
      try {
        const response = await api.getAiModels()
        if (response.success) {
          this.aiModels = response.models
          if (this.aiModels.length > 0 && !this.selectedModel) {
            // Prefer llama3 if available
            const llama3 = this.aiModels.find(m => m.name.includes('llama3'))
            this.selectedModel = llama3 ? llama3.name : this.aiModels[0].name
          }
        }
      } catch (error) {
        // Failed to load models - AI feature not available
        this.aiAvailable = false
      }
    },

    formatSize(bytes) {
      if (!bytes) return 'Unknown size'
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      if (bytes === 0) return '0 B'
      const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)))
      return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i]
    },

    async runSmartMapping() {
      this.mappingLoading = true
      this.suggestedMapping = null
      this.mappingProgress = 0
      this.mappingAbortController = new AbortController()
      
      // Reset progress steps
      this.aiProgressSteps.forEach(step => {
        step.completed = false
        step.active = false
      })
      
      try {
        // Step 1: Preparing data
        this.updateAIProgress(0, 'Preparing data...', 20)
        const colResponse = await api.getFileColumns()
        if (!colResponse.success) throw new Error(colResponse.error)
        
        // Step 2: Model loading (simulated - happens on server)
        this.updateAIProgress(1, 'Loading AI model...', 40)
        await this.sleep(500) // Brief pause to show progress
        
        // Step 3: Analyzing columns
        this.updateAIProgress(2, 'Analyzing columns with AI (this may take 1-5 minutes)...', 60)
        
        // Request mapping from AI (this is the long operation)
        const mapResponse = await api.suggestMapping(
          colResponse.columns, 
          this.selectedModel,
          this.mappingAbortController.signal
        )
        
        // Step 4: Generating mappings
        this.updateAIProgress(3, 'Generating mappings...', 90)
        
        if (mapResponse.success) {
          // Validate that mapping is a proper object
          if (!mapResponse.mapping || typeof mapResponse.mapping !== 'object') {
            throw new Error('AI response format error. Please try a different model.')
          }
          
          this.suggestedMapping = mapResponse.mapping
          
          // Show transformations that were applied
          if (mapResponse.transformations_applied && mapResponse.transformations_applied.length > 0) {
            const transformList = mapResponse.transformations_applied
              .map(t => `• ${t.column}: ${t.transformation}`)
              .join('\n')
            alert('✓ AI Mapping Complete!\n\n' +
                  'Auto-applied transformations:\n' + transformList + 
                  '\n\nYour data has been cleaned and mapped.')
          }
          
          this.updateAIProgress(3, 'Complete!', 100)
          await this.sleep(500)
        } else {
          // Check if it's a JSON parsing error
          const errorMsg = mapResponse.error || 'Unknown error'
          if (errorMsg.includes('JSON') || errorMsg.includes('parse') || errorMsg.includes('format')) {
            throw new Error('AI response format error. Please try a different model.')
          }
          throw new Error(errorMsg)
        }
      } catch (error) {
        if (error.name === 'AbortError' || error.message.includes('abort')) {
          alert('✓ AI analysis stopped by user.')
        } else {
          let errorMsg = error.message || 'Unknown error'
          
          // Check for format errors
          if (error.response?.data?.error) {
            const backendError = error.response.data.error
            if (backendError.includes('JSON') || backendError.includes('parse') || backendError.includes('format')) {
              errorMsg = 'AI response format error. Please try a different model.'
            } else {
              errorMsg = backendError
            }
          }
          
          alert('❌ Failed to generate mapping:\n\n' + errorMsg + '\n\nTip: Try a different model or a smaller model like "phi3" or "gemma2:2b".')
        }
      } finally {
        this.mappingLoading = false
        this.mappingAbortController = null
        // Reset progress after completion
        setTimeout(() => {
          this.mappingProgress = 0
          this.aiProgressSteps.forEach(step => {
            step.completed = false
            step.active = false
          })
        }, 2000)
      }
    },

    stopMapping() {
      if (this.mappingAbortController) {
        this.mappingAbortController.abort()
        this.mappingLoading = false
        this.updateAIProgress(0, 'Stopped by user', 0)
      }
    },

    updateAIProgress(stepIndex, statusText, progress) {
      // Mark previous steps as completed
      for (let i = 0; i < stepIndex; i++) {
        this.aiProgressSteps[i].completed = true
        this.aiProgressSteps[i].active = false
      }
      // Mark current step as active
      if (stepIndex < this.aiProgressSteps.length) {
        this.aiProgressSteps[stepIndex].active = true
        this.aiProgressSteps[stepIndex].completed = false
      }
      // Update overall progress
      this.mappingStatusText = statusText
      this.mappingProgress = progress
    },

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    },

    async applyMapping() {
      if (!this.suggestedMapping) return
      
      this.applyingMapping = true
      try {
        const response = await api.applyMapping(this.suggestedMapping)
        if (response.success) {
          alert('✓ ' + response.message)
          // Clear mapping after success
          this.suggestedMapping = null
        } else {
          alert('Failed to apply mapping: ' + response.error)
        }
      } catch (error) {
        alert('Error applying mapping: ' + error.message)
      } finally {
        this.applyingMapping = false
      }
    },

    async downloadModel() {
      if (!this.newModelName) return

      this.pullingModel = true
      this.pullStatus = { success: false, message: 'Starting download...' }

      try {
        const response = await api.pullModel(this.newModelName.trim())
        if (response.success) {
          this.pullStatus = { 
            success: true, 
            message: `Model "${this.newModelName}" download started. This may take several minutes. Refresh the model list to check when it's available.` 
          }
          // Clear input and refresh after a delay
          setTimeout(() => {
            this.newModelName = ''
            this.refreshModels()
          }, 3000)
        } else {
          this.pullStatus = { 
            success: false, 
            message: 'Download failed: ' + response.error 
          }
        }
      } catch (error) {
        this.pullStatus = { 
          success: false, 
          message: 'Error: ' + (error.response?.data?.error || error.message)
        }
      } finally {
        this.pullingModel = false
      }
    },

    async loadDataPreview() {
      if (!this.uploadedFile) {
        alert('Please upload a data file in Step 2 first.')
        return
      }
      
      this.loadingPreview = true
      this.dataPreview = null
      try {
        const response = await api.getDataPreview()
        
        if (response && response.success === true) {
          this.dataPreview = response
        } else {
          const errorMsg = response?.error || 'Unable to load preview'
          alert('❌ Failed to load data preview:\n\n' + errorMsg + '\n\n📝 Make sure you have uploaded a file in Step 2.')
        }
      } catch (error) {
        // Handle HTTP error responses (404, 500, etc.)
        let errorMsg = 'Unknown error'
        if (error.response?.data?.error) {
          errorMsg = error.response.data.error
        } else if (error.response?.data) {
          errorMsg = JSON.stringify(error.response.data)
        } else if (error.message) {
          errorMsg = error.message
        }
        alert('❌ Error loading preview:\n\n' + errorMsg + '\n\n📝 Make sure you have uploaded a file in Step 2.')
      } finally {
        this.loadingPreview = false
      }
    },

    async applyTransformation() {
      if (!this.transformColumn || !this.transformType) return

      this.transforming = true
      this.transformResult = null

      try {
        const response = await api.transformColumn(
          this.transformColumn,
          this.transformType,
          this.transformOptions
        )

        if (response.success) {
          this.transformResult = {
            success: true,
            message: response.message,
            preview: response.preview
          }
          // Reload preview after transformation
          setTimeout(() => {
            this.loadDataPreview()
          }, 1000)
        } else {
          this.transformResult = {
            success: false,
            message: response.error
          }
        }
      } catch (error) {
        this.transformResult = {
          success: false,
          message: error.response?.data?.error || error.message
        }
      } finally {
        this.transforming = false
      }
    },
    async loadConnections() {
      try {
        const userId = this.user?.id
        const response = await api.getConnections(userId)
        if (response.success) {
          this.allegroGraphConnections = response.connections
        }
      } catch (error) {
        // Failed to load connections - will use empty list
        this.allegroGraphConnections = []
      }
    },

    nextStep() {
      if (this.currentStep < this.steps.length) {
        this.currentStep++
        // Reload connections when reaching step 5
        if (this.currentStep === 5) {
          this.loadConnections()
        }
      }
    },

    previousStep() {
      if (this.currentStep > 1) {
        this.currentStep--
      }
    },

    triggerFileUpload() {
      this.$refs.fileInput.click()
    },

    async handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        await this.uploadFile(file)
      }
    },

    async handleFileDrop(event) {
      const file = event.dataTransfer.files[0]
      if (file) {
        await this.uploadFile(file)
      }
    },

    async uploadFile(file) {
      try {
        const response = await api.uploadFile(file)
        if (response.success) {
          this.uploadedFile = {
            name: file.name,
            size: file.size,
            type: response.file_type,
            uploaded: true
          }
          alert('✓ ' + response.message)
        }
      } catch (error) {
        const errorMsg = error.response?.data?.error || error.message
        alert('Upload failed: ' + errorMsg)
      }
    },

    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
    },

    async loadSchema() {
      try {
        const response = await api.getSchema()
        if (response.success) {
          this.schema = response.schema
        }
      } catch (error) {
        // Schema not available - will use defaults
        this.schema = null
      }
    },

    async runValidation() {
      if (!this.uploadedFile) {
        alert('Please upload a file first')
        return
      }

      this.validating = true
      this.validationResult = null

      try {
        const response = await api.validateData()
        if (response.success) {
          this.validationResult = response.validation
        }
      } catch (error) {
        const errorMsg = error.response?.data?.error || error.message
        alert('❌ Validation failed:\n\n' + errorMsg + '\n\n💡 Tip: Check that your file format matches the expected structure.')
      } finally {
        this.validating = false
      }
    },

    async runAllProcessing() {
      this.processing = true
      this.processingResult = null

      try {
        // Step 1: Run processing.ipynb
        const response1 = await api.runNotebook('processing.ipynb')
        if (!response1.success) {
          throw new Error(response1.error || 'Processing notebook failed')
        }

        // Step 2: Run json_creator.ipynb
        const response2 = await api.runNotebook('json_creator.ipynb')
        if (!response2.success) {
          throw new Error(response2.error || 'JSON creator notebook failed')
        }

        this.processingResult = {
          success: true,
          message: 'Data processing completed successfully! Final JSON output is ready for RDF conversion.',
          output: `Processing Step:\n${response1.output || '(no output)'}\n\nJSON Generation Step:\n${response2.output || '(no output)'}`
        }
      } catch (error) {
        const errorMsg = error.response?.data?.error || error.message
        this.processingResult = {
          success: false,
          message: 'Processing failed: ' + errorMsg
        }
      } finally {
        this.processing = false
      }
    },

    getGdprBadgeClass(category) {
      const classes = {
        'special_category': 'badge-special-category',
        'criminal_offense': 'badge-criminal',
        'indirect_identifier': 'badge-indirect',
        'personal': 'badge-sensitive'
      }
      return classes[category] || ''
    },

    getGdprLabel(category) {
      const labels = {
        'special_category': 'GDPR Special Category',
        'criminal_offense': 'Criminal Offense',
        'indirect_identifier': 'Indirect Identifier',
        'personal': 'Personal Data'
      }
      return labels[category] || category
    },

    async handleExport() {
      if (!this.selectedConnectionId) {
        alert('Please select a target connection')
        return
      }

      const selectedConn = this.allegroGraphConnections.find(
        conn => conn.id === this.selectedConnectionId
      )

      if (!confirm(`Push RDF data to:\n${selectedConn.name}\n(${selectedConn.host}:${selectedConn.port}/${selectedConn.repository})?`)) {
        return
      }

      this.processing = 'export'
      this.processingResult = null

      try {
        const response = await api.pushToAllegroGraph(this.selectedConnectionId)
        
        if (response.success) {
          this.processingResult = {
            success: true,
            message: response.message,
            output: response.output
          }
          alert('✓ ' + response.message)
        } else {
          this.processingResult = {
            success: false,
            message: response.error
          }
          alert('Error: ' + response.error)
        }
      } catch (error) {
        const errorMsg = error.response?.data?.error || error.message
        this.processingResult = {
          success: false,
          message: 'Failed to push data: ' + errorMsg
        }
        alert('Error: ' + errorMsg)
      } finally {
        this.processing = false
      }
    }
  }
}
</script>

<style scoped>
.workflow-manager {
  background: linear-gradient(to bottom, #f8fafc, #e2e8f0);
  padding: 2rem 0;
}

.workflow-progress {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
}

.progress-step {
  flex: 1;
  text-align: center;
  position: relative;
}

.progress-step::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 0;
  right: 0;
  height: 3px;
  background: #e5e7eb;
  z-index: 0;
}

.progress-step:first-child::before {
  left: 50%;
}

.progress-step:last-child::before {
  right: 50%;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.5rem;
  position: relative;
  z-index: 1;
  font-weight: bold;
  transition: all 0.3s;
}

.progress-step.active .step-circle {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: scale(1.1);
}

.progress-step.completed .step-circle {
  background: #10b981;
  color: white;
}

.progress-step.completed::before {
  background: #10b981;
}

.step-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
}

.progress-step.active .step-label {
  color: #667eea;
  font-weight: 700;
}

.workflow-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.section-header i {
  font-size: 2rem;
  color: #667eea;
  margin-top: 0.25rem;
}

.section-header h2 {
  margin: 0;
  color: #1e293b;
  font-size: 1.75rem;
  font-weight: 700;
}

.upload-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f8fafc;
}

.upload-zone:hover {
  border-color: #667eea;
  background: #f1f5f9;
}

.upload-icon {
  font-size: 4rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.info-box {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-box i {
  color: #3b82f6;
  font-size: 1.5rem;
}

.success-box {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  margin-bottom: 1.5rem;
}

.success-box i {
  color: #10b981;
  font-size: 3rem;
  margin-bottom: 1rem;
}

.success-box h4 {
  color: #065f46;
  margin-bottom: 0.5rem;
}

.step-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: 1.1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
  border: none;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  color: white;
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #1e293b;
  font-weight: 600;
}

.form-select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s;
  background: white;
}

.form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.text-muted {
  color: #64748b;
  font-size: 0.875rem;
}

.alert {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.alert-info {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
}

.alert-success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #065f46;
}

.alert-warning {
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
}

.alert-danger {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.schema-container {
  max-height: 500px;
  overflow-y: auto;
}

.schema-entity {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.schema-entity-title {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.schema-entity-description {
  background: #f8f9fa;
  padding: 0.75rem 1rem;
  border-bottom: 2px solid #e5e7eb;
  color: #64748b;
  font-size: 0.9rem;
  font-style: italic;
}

.schema-fields {
  padding: 1rem;
}

.schema-field {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
  position: relative;
}

.schema-field:last-child {
  border-bottom: none;
}

.sensitive-indicator {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #fef2f2;
  color: #991b1b;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.field-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.field-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.field-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-required {
  background: #fee2e2;
  color: #991b1b;
}

.badge-optional {
  background: #e0e7ff;
  color: #3730a3;
}

.badge-special-category {
  background: #fef2f2;
  color: #991b1b;
}

.badge-criminal {
  background: #fff1f2;
  color: #9f1239;
}

.badge-indirect {
  background: #fffbeb;
  color: #92400e;
}

.badge-sensitive {
  background: #fef3c7;
  color: #78350f;
}

.validation-section {
  border-top: 3px solid #e5e7eb;
}

.validation-panel {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
}

.card-title {
  margin-bottom: 1rem;
  color: #1e293b;
  font-weight: 600;
}

.d-flex {
  display: flex;
}

.gap-2 {
  gap: 0.5rem;
}

.gap-3 {
  gap: 1rem;
}

.output-box {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  margin-bottom: 0;
  white-space: pre-wrap;
}

.processing-steps {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.processing-step {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.step-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
  padding-top: 0.25rem;
}

.step-content strong {
  display: block;
  margin-bottom: 0.25rem;
  color: #1e293b;
}

/* Data Transformation Tools */
.transformation-tools-section .card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.data-preview-section {
  margin-top: 1.5rem;
}

.data-preview-section .table {
  font-size: 0.85rem;
  margin-bottom: 0;
}

.data-preview-section .table th {
  background: #f1f5f9;
  font-weight: 600;
  white-space: nowrap;
}

.data-preview-section .table td {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.transform-options {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e2e8f0;
}

.transform-details {
  font-size: 0.9rem;
}

/* Schema Reference Modal */
.schema-reference-modal {
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.schema-ref-section {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid;
}

.schema-ref-section:nth-child(2) {
  border-left-color: #0d6efd;
}

.schema-ref-section:nth-child(3) {
  border-left-color: #dc3545;
}

.schema-ref-section:nth-child(4) {
  border-left-color: #198754;
}

.schema-ref-section:nth-child(5) {
  border-left-color: #ffc107;
}

.schema-ref-section:nth-child(6) {
  border-left-color: #0dcaf0;
}

.schema-ref-section h6 {
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.schema-fields-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.schema-fields-list .badge {
  font-size: 0.85rem;
  padding: 0.4rem 0.8rem;
  border: 1px solid #dee2e6;
}

.transform-details strong {
  color: #334155;
}

/* Progress bars */
.progress {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}

.progress-bar {
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* AI Mapping Section improvements */
.ai-mapping-section .card {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  transition: all 0.3s;
}

.ai-mapping-section .card:hover {
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.25);
}

/* AI Progress Steps */
.ai-progress-container {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.ai-progress-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
  margin-top: 1rem;
}

.progress-step-item {
  padding: 0.5rem;
  background: white;
  border-radius: 6px;
  font-size: 0.85rem;
  transition: all 0.3s;
  border: 1px solid #e2e8f0;
}

.progress-step-item.completed {
  background: #ecfdf5;
  border-color: #10b981;
  color: #047857;
}

.progress-step-item.completed i {
  color: #10b981;
}

.progress-step-item.active {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #1e40af;
  font-weight: 500;
}

.progress-step-item.active i {
  color: #3b82f6;
}

.progress-step-item:not(.active):not(.completed) {
  color: #94a3b8;
}

.progress-step-item:not(.active):not(.completed) i {
  color: #cbd5e1;
}

.model-download-section,
.model-selection-section {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .progress-steps {
    flex-direction: column;
    gap: 1rem;
  }

  .progress-step::before {
    display: none;
  }

  .step-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .data-preview-section .table-responsive {
    font-size: 0.75rem;
  }
}
</style>
