<template>
  <div class="catalog-browser">
    <div class="card">
      <div class="card-header">
        📚 Browse EEPA Data Catalogs
      </div>

      <div class="info-banner">
        <p>
          <strong>FAIR Data Point:</strong> EEPA FAIR Data Point provides metadata 
          about available sensitive refugee and human trafficking research datasets.
        </p>
        <p>
          <a href="https://fairdp.colo.ba.be/" target="_blank" rel="noopener noreferrer" class="fdp-link">
            🔗 Visit FAIR Data Point
          </a>
        </p>
        <p>
          <strong>Contact for Access:</strong> {{ fdpContact }}
        </p>
        <p class="note">
          Browse available catalogs below. After selecting a catalog, you'll need to 
          contact the data owner to request AllegroGraph credentials.
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading catalogs from FAIR Data Point...</p>
      </div>

      <!-- Error State -->
      <div v-if="error" class="alert error">
        {{ error }}
      </div>

      <!-- Catalogs List -->
      <div v-if="!loading && catalogs.length > 0" class="catalogs-list">
        <div
          v-for="catalog in catalogs"
          :key="catalog.id"
          :class="['catalog-card', { selected: selectedCatalog?.id === catalog.id }]"
          @click="selectCatalog(catalog)"
        >
          <div class="catalog-header">
            <h3>{{ catalog.title || 'Untitled Catalog' }}</h3>
            <span v-if="selectedCatalog?.id === catalog.id" class="selected-badge">✓ Selected</span>
          </div>
          
          <p class="catalog-description">
            {{ catalog.description || 'No description available' }}
          </p>
          
          <div class="catalog-meta">
            <div class="meta-item">
              <strong>Publisher:</strong> {{ catalog.publisher || 'Unknown' }}
            </div>
            <div class="meta-item">
              <strong>Datasets:</strong> {{ catalog.dataset_count || 0 }}
            </div>
            <div v-if="catalog.modified" class="meta-item">
              <strong>Last Modified:</strong> {{ formatDate(catalog.modified) }}
            </div>
            <div v-if="catalog.license" class="meta-item">
              <strong>License:</strong> {{ catalog.license }}
            </div>
          </div>

          <div v-if="catalog.themes && catalog.themes.length > 0" class="themes">
            <strong>Themes:</strong>
            <span v-for="(theme, idx) in catalog.themes.slice(0, 3)" :key="idx" class="theme-tag">
              {{ getThemeName(theme) }}
            </span>
            <span v-if="catalog.themes.length > 3" class="theme-more">
              +{{ catalog.themes.length - 3 }} more
            </span>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && !error && catalogs.length === 0" class="empty-state">
        <p>No catalogs available at this time.</p>
      </div>

      <!-- Action Buttons -->
      <div class="actions" v-if="selectedCatalog">
        <button class="primary" @click="proceedWithCatalog">
          Proceed to Add Connection
        </button>
        <button class="secondary" @click="cancelSelection">
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'CatalogBrowser',
  
  data() {
    return {
      loading: true,
      error: null,
      catalogs: [],
      selectedCatalog: null,
      fdpContact: 'HDS@eepa.be'
    }
  },
  
  mounted() {
    this.loadCatalogs()
  },
  
  methods: {
    async loadCatalogs() {
      this.loading = true
      this.error = null
      
      try {
        // First get FDP info for contact
        const infoResponse = await api.getFairDataPointInfo()
        if (infoResponse.success && infoResponse.info.contact) {
          this.fdpContact = infoResponse.info.contact
        }
        
        // Then get catalogs
        const response = await api.getFairCatalogs()
        
        if (response.success) {
          this.catalogs = response.catalogs
        } else {
          this.error = response.error || 'Failed to load catalogs'
        }
      } catch (err) {
        console.error('Error loading catalogs:', err)
        this.error = 'Unable to connect to FAIR Data Point. Please try again later.'
      } finally {
        this.loading = false
      }
    },
    
    selectCatalog(catalog) {
      this.selectedCatalog = catalog
    },
    
    cancelSelection() {
      this.selectedCatalog = null
      this.$emit('cancel')
    },
    
    proceedWithCatalog() {
      if (this.selectedCatalog) {
        this.$emit('catalog-selected', this.selectedCatalog)
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
      } catch (e) {
        return dateString
      }
    },
    
    getThemeName(themeUrl) {
      // Extract readable name from theme URL
      const parts = themeUrl.split('/')
      const lastPart = parts[parts.length - 1]
      return lastPart.replace(/_/g, ' ').replace(/-/g, ' ')
    }
  }
}
</script>

<style scoped>
.catalog-browser {
  margin: 20px 0;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.card-header {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 20px;
  color: #2c3e50;
}

.info-banner {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  padding: 16px;
  margin-bottom: 24px;
  border-radius: 4px;
}

.info-banner p {
  margin: 8px 0;
  line-height: 1.6;
}

.info-banner .note {
  font-size: 0.95rem;
  color: #555;
  font-style: italic;
  margin-top: 12px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.alert {
  padding: 12px 16px;
  margin-bottom: 16px;
  border-radius: 4px;
}

.alert.error {
  background: #ffebee;
  color: #c62828;
  border-left: 4px solid #c62828;
}

.catalogs-list {
  display: grid;
  gap: 16px;
  margin-bottom: 24px;
}

.catalog-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fafafa;
}

.catalog-card:hover {
  border-color: #2196f3;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.catalog-card.selected {
  border-color: #4caf50;
  background: #f1f8f4;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
}

.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.catalog-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.selected-badge {
  background: #4caf50;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: bold;
}

.catalog-description {
  color: #555;
  line-height: 1.6;
  margin-bottom: 16px;
}

.catalog-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
  font-size: 0.9rem;
}

.meta-item {
  color: #666;
}

.meta-item strong {
  color: #333;
}

.meta-item a {
  color: #2196f3;
  text-decoration: none;
}

.meta-item a:hover {
  text-decoration: underline;
}

.themes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  font-size: 0.9rem;
  color: #666;
}

.theme-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.85rem;
  text-transform: capitalize;
}

.theme-more {
  color: #999;
  font-style: italic;
}

.fdp-link {
  display: inline-flex;
  align-items: center;
  color: #1976d2;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.fdp-link:hover {
  color: #1565c0;
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

button.primary {
  background: #4caf50;
  color: white;
}

button.primary:hover {
  background: #45a049;
}

button.secondary {
  background: #e0e0e0;
  color: #333;
}

button.secondary:hover {
  background: #d0d0d0;
}
</style>
