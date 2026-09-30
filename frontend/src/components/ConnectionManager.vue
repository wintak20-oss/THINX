<template>
  <div class="connection-manager">
    <div class="card">
      <div class="card-header">
        🔌 Connection Manager
      </div>

      <!-- Alert messages -->
      <div v-if="alertMessage" :class="['alert', alertType]">
        {{ alertMessage }}
      </div>

      <!-- Add Connection Buttons -->
      <div class="actions">
        <button class="primary" @click="toggleAddForm('allegrograph')">
          {{ showAddForm === 'allegrograph' ? '✕ Cancel' : '➕ Add AllegroGraph Connection' }}
        </button>
        <button class="secondary" @click="showCatalogBrowser = !showCatalogBrowser">
          {{ showCatalogBrowser ? '✕ Cancel' : '📚 Browse EEPA Data Catalogs' }}
        </button>
      </div>

      <!-- FAIR Data Point Catalog Browser -->
      <CatalogBrowser
        v-if="showCatalogBrowser && !showAddForm"
        @catalog-selected="handleCatalogSelected"
        @cancel="showCatalogBrowser = false"
      />

      <!-- Add/Edit Connection Form -->
      <ConnectionForm
        v-if="showAddForm === 'allegrograph'"
        :connection="editingConnection"
        :catalogMetadata="selectedCatalogMetadata"
        @save="handleSaveConnection"
        @cancel="cancelEdit"
      />

      <!-- Connections List -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading connections...</p>
      </div>

      <ConnectionList
        v-else
        :connections="connections"
        @activate="handleActivate"
        @edit="handleEdit"
        @delete="handleDelete"
        @view-data="viewData"
      />
    </div>
  </div>
</template>

<script>
import api from '../services/api'
import ConnectionForm from './ConnectionForm.vue'
import ConnectionList from './ConnectionList.vue'
import CatalogBrowser from './CatalogBrowser.vue'

export default {
  name: 'ConnectionManager',
  
  components: {
    ConnectionForm,
    ConnectionList,
    CatalogBrowser
  },

  props: {
    user: {
      type: Object,
      required: false
    }
  },

  data() {
    return {
      connections: [],
      loading: false,
      showAddForm: null, // null or 'allegrograph'
      showCatalogBrowser: false,
      editingConnection: null,
      selectedCatalogMetadata: null,
      alertMessage: '',
      alertType: 'success'
    }
  },

  mounted() {
    this.loadConnections()
  },

  methods: {
    async loadConnections() {
      this.loading = true
      try {
        const userId = this.user?.id
        const response = await api.getConnections(userId)
        if (response.success) {
          this.connections = response.connections
        }
      } catch (error) {
        this.showAlert('Failed to load connections: ' + error.message, 'error')
      } finally {
        this.loading = false
      }
    },

    toggleAddForm(type) {
      if (this.showAddForm === type) {
        this.showAddForm = null
        this.editingConnection = null
      } else {
        this.showAddForm = type
        this.editingConnection = null
      }
    },

    async handleSaveConnection(connectionData) {
      try {
        // Add user_id to connection data
        const dataWithUser = {
          ...connectionData,
          user_id: this.user?.id
        }
        
        let response
        if (this.editingConnection) {
          // Update existing
          response = await api.updateConnection(this.editingConnection.id, dataWithUser)
        } else {
          // Create new
          response = await api.createConnection(dataWithUser)
        }

        if (response.success) {
          this.showAlert(response.message, 'success')
          this.loadConnections()
          this.showAddForm = null
          this.editingConnection = null
        } else {
          this.showAlert(response.error || 'Failed to save connection', 'error')
        }
      } catch (error) {
        const errorMsg = error.response?.data?.error || error.message
        this.showAlert('Error saving connection: ' + errorMsg, 'error')
      }
    },

    async handleActivate(connection) {
      try {
        const response = await api.activateConnection(connection.id)
        if (response.success) {
          this.showAlert(`Activated connection: ${connection.name}`, 'success')
          this.loadConnections()
        }
      } catch (error) {
        this.showAlert('Failed to activate connection: ' + error.message, 'error')
      }
    },

    handleEdit(connection) {
      this.editingConnection = connection
      // Determine which form to show based on connection type
      this.showAddForm = 'allegrograph'
    },

    async handleDelete(connection) {
      if (!confirm(`Delete connection "${connection.name}"?`)) {
        return
      }

      try {
        const response = await api.deleteConnection(connection.id)
        if (response.success) {
          this.showAlert('Connection deleted successfully', 'success')
          this.loadConnections()
        }
      } catch (error) {
        this.showAlert('Failed to delete connection: ' + error.message, 'error')
      }
    },

    cancelEdit() {
      this.showAddForm = null
      this.editingConnection = null
      this.selectedCatalogMetadata = null
    },

    handleCatalogSelected(catalog) {
      // Store catalog metadata and show connection form
      this.selectedCatalogMetadata = {
        catalog_id: catalog.id,
        catalog_title: catalog.title,
        catalog_publisher: catalog.publisher,
        catalog_contact: catalog.contact,
        catalog_license: catalog.license,
        catalog_themes: catalog.themes || [],
        dataset_count: catalog.dataset_count || 0,
        description: catalog.description
      }
      
      this.showCatalogBrowser = false
      this.showAddForm = 'allegrograph'
      
      this.showAlert(
        `Selected catalog: ${catalog.title}. Please provide AllegroGraph credentials to connect.`,
        'success'
      )
    },

    viewData(connection) {
      // Activate and navigate to data viewer
      this.handleActivate(connection).then(() => {
        this.$router.push('/data')
      })
    },

    showAlert(message, type = 'success') {
      this.alertMessage = message
      this.alertType = type
      setTimeout(() => {
        this.alertMessage = ''
      }, 5000)
    }
  }
}
</script>

<style scoped>
.connection-manager {
  max-width: 1000px;
  margin: 0 auto;
}

.actions {
  margin-bottom: 1.5rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.alert {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
