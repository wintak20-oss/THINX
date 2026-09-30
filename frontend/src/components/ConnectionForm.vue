<template>
  <div class="connection-form">
    <div class="form-header">
      <h3>{{ isEdit ? '✏️ Edit Connection' : '➕ Add New Database Connection' }}</h3>
      <p class="form-description">
        Enter your AllegroGraph database credentials. If you don't have these, contact your system administrator.
      </p>
    </div>

    <!-- Catalog Metadata Info -->
    <div v-if="catalogMetadata" class="catalog-info">
      <div class="info-header">
        📚 Selected Catalog Information
      </div>
      <div class="info-grid">
        <div class="info-item">
          <strong>Catalog:</strong> {{ catalogMetadata.catalog_title }}
        </div>
        <div class="info-item">
          <strong>Publisher:</strong> {{ catalogMetadata.catalog_publisher }}
        </div>
        <div class="info-item">
          <strong>Contact:</strong> {{ catalogMetadata.catalog_contact }}
        </div>
        <div class="info-item">
          <strong>Datasets:</strong> {{ catalogMetadata.dataset_count }}
        </div>
      </div>
      <p class="catalog-note">
        <strong>Note:</strong> Please provide AllegroGraph credentials to access this catalog's data.
      </p>
    </div>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="name">
          Connection Name *
          <span class="label-help" title="A friendly name to identify this connection">ℹ️</span>
        </label>
        <input
          id="name"
          v-model="formData.name"
          type="text"
          placeholder="e.g., Main Research Database"
          required
        />
        <small class="help-text">Choose a descriptive name to identify this database</small>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="host">
            Server Address *
            <span class="label-help" title="The hostname or IP address of the AllegroGraph server">ℹ️</span>
          </label>
          <input
            id="host"
            v-model="formData.host"
            type="text"
            placeholder="e.g., allegrograph or 192.168.1.100"
            required
          />
          <small class="help-text">Hostname (e.g., "allegrograph") or IP address</small>
        </div>

        <div class="form-group">
          <label for="port">
            Port *
            <span class="label-help" title="Usually 10035 for AllegroGraph">ℹ️</span>
          </label>
          <input
            id="port"
            v-model.number="formData.port"
            type="number"
            placeholder="10035"
            required
            min="1"
            max="65535"
          />
          <small class="help-text">Default: 10035</small>
        </div>
      </div>

      <div class="form-group">
        <label for="repository">
          Repository Name *
          <span class="label-help" title="The name of the AllegroGraph repository to connect to">ℹ️</span>
        </label>
        <input
          id="repository"
          v-model="formData.repository"
          type="text"
          placeholder="e.g., humantrafficking"
          required
        />
        <small class="help-text">The repository must exist in AllegroGraph</small>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="username">
            Username *
            <span class="label-help" title="Your AllegroGraph username">ℹ️</span>
          </label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="AllegroGraph username"
            required
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="password">
            Password *
            <span class="label-help" title="Your AllegroGraph password">ℹ️</span>
          </label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="AllegroGraph password"
            required
            autocomplete="current-password"
          />
        </div>
      </div>

      <div class="form-group">
        <div class="checkbox-wrapper">
          <label class="checkbox-label">
            <input
              v-model="formData.test_connection"
              type="checkbox"
            />
            <span class="checkbox-text">Test connection before saving</span>
          </label>
          <small class="help-text">
            <i class="fas fa-info-circle"></i>
            Recommended: Verifies that the connection works. Uncheck only if the database is temporarily unavailable.
          </small>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="secondary" @click="$emit('cancel')">
          <i class="fas fa-times"></i> Cancel
        </button>
        <button type="submit" class="primary">
          <i class="fas fa-save"></i> {{ isEdit ? 'Update' : 'Save' }} Connection
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'ConnectionForm',

  props: {
    connection: {
      type: Object,
      default: null
    },
    catalogMetadata: {
      type: Object,
      default: null
    }
  },

  emits: ['save', 'cancel'],

  data() {
    return {
      formData: {
        name: '',
        host: '',
        port: 10035,
        repository: '',
        username: '',
        password: '',
        test_connection: false,
        type: 'allegrograph'
      }
    }
  },

  computed: {
    isEdit() {
      return this.connection !== null
    }
  },

  mounted() {
    if (this.connection) {
      this.formData = { ...this.connection }
    } else if (this.catalogMetadata) {
      // Pre-fill connection name from catalog
      this.formData.name = this.catalogMetadata.catalog_title || ''
    }
  },

  methods: {
    handleSubmit() {
      // Merge catalog metadata with form data if available
      const dataToSave = { ...this.formData }
      
      if (this.catalogMetadata) {
        dataToSave.catalog_id = this.catalogMetadata.catalog_id
        dataToSave.catalog_title = this.catalogMetadata.catalog_title
        dataToSave.catalog_publisher = this.catalogMetadata.catalog_publisher
        dataToSave.catalog_contact = this.catalogMetadata.catalog_contact
        dataToSave.catalog_license = this.catalogMetadata.catalog_license
        dataToSave.catalog_themes = this.catalogMetadata.catalog_themes
        dataToSave.dataset_count = this.catalogMetadata.dataset_count
        dataToSave.description = this.catalogMetadata.description || this.formData.description
      }
      
      this.$emit('save', dataToSave)
    }
  }
}
</script>

<style scoped>
.connection-form {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.connection-form h3 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.help-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
  cursor: pointer;
}

.catalog-info {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
  padding: 16px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.info-header {
  font-weight: bold;
  margin-bottom: 12px;
  color: #2c3e50;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.info-item {
  font-size: 0.9rem;
}

.info-item strong {
  color: #333;
}

.catalog-note {
  font-size: 0.9rem;
  color: #555;
  font-style: italic;
  margin-top: 8px;
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
