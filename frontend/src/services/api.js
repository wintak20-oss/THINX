/**
 * API Service for communicating with Flask backend
 */

import axios from 'axios'

// Get API URL from environment or default to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 150000  // Increased to 150 seconds for AI operations
})

// Request interceptor for logging (development only)
apiClient.interceptors.request.use(
  config => {
    if (import.meta.env.MODE === 'development') {
      console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`)
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // Only log errors in development mode
    if (import.meta.env.MODE === 'development') {
      if (error.response) {
        console.error('API Error:', error.response.data)
      } else if (error.request) {
        console.error('API Error: No response from server')
      } else {
        console.error('API Error:', error.message)
      }
    }
    return Promise.reject(error)
  }
)

export default {
  // Connection management
  async getConnections(userId = null) {
    const params = userId ? { user_id: userId } : {}
    const response = await apiClient.get('/connections', { params })
    return response.data
  },

  async getConnection(id) {
    const response = await apiClient.get(`/connections/${id}`)
    return response.data
  },

  async createConnection(connectionData) {
    const response = await apiClient.post('/connections', connectionData)
    return response.data
  },

  async updateConnection(id, connectionData) {
    const response = await apiClient.put(`/connections/${id}`, connectionData)
    return response.data
  },

  async deleteConnection(id) {
    const response = await apiClient.delete(`/connections/${id}`)
    return response.data
  },

  async activateConnection(id) {
    const response = await apiClient.post(`/connections/${id}/activate`)
    return response.data
  },

  async getActiveConnection() {
    const response = await apiClient.get('/connections/active')
    return response.data
  },

  // Data operations
  async getData(connectionId = null, limit = 100, offset = 0) {
    const params = { limit, offset }
    if (connectionId) {
      params.connection_id = connectionId
    }
    const response = await apiClient.get('/data', { params })
    return response.data
  },

  async executeQuery(query, connectionId = null) {
    const response = await apiClient.post('/query', {
      query,
      connection_id: connectionId
    })
    return response.data
  },

  async getStatistics(connectionId = null) {
    const params = connectionId ? { connection_id: connectionId } : {}
    const response = await apiClient.get('/statistics', { params })
    return response.data
  },

  // Ontology
  async getOntology() {
    const response = await apiClient.get('/ontology')
    return response.data
  },

  // Schema
  async getSchema() {
    const response = await apiClient.get('/schema')
    return response.data
  },

  // AI Features
  async checkAiStatus() {
    const response = await apiClient.get('/ai-status')
    return response.data
  },

  async getFileColumns() {
    const response = await apiClient.get('/file-columns')
    return response.data
  },

  async getAiModels() {
    const response = await apiClient.get('/ai-models')
    return response.data
  },

  async pullModel(modelName) {
    const response = await apiClient.post('/pull-model', { model: modelName })
    return response.data
  },

  async suggestMapping(columns, model = 'llama3', signal = null) {
    const config = signal ? { signal } : {}
    const response = await apiClient.post('/suggest-mapping', { columns, model }, config)
    return response.data
  },

  async applyMapping(mapping) {
    const response = await apiClient.post('/apply-mapping', { mapping })
    return response.data
  },

  async getDataPreview() {
    const response = await apiClient.get('/data-preview')
    return response.data
  },

  async transformColumn(column, transformType, options = {}) {
    const response = await apiClient.post('/transform-column', {
      column,
      transform_type: transformType,
      options
    })
    return response.data
  },

  // File operations
  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // Validation
  async validateData() {
    const response = await apiClient.post('/validate')
    return response.data
  },

  // Run notebook
  async runNotebook(notebook) {
    const response = await apiClient.post('/run-notebook', { notebook })
    return response.data
  },

  // Push to AllegroGraph
  async pushToAllegroGraph(connectionId) {
    const response = await apiClient.post('/push-to-allegrograph', {
      connection_id: connectionId
    })
    return response.data
  },

  // Health check
  async healthCheck() {
    const response = await apiClient.get('/health')
    return response.data
  },

  // FAIR Data Point
  async getFairDataPointInfo() {
    const response = await apiClient.get('/fair/info')
    return response.data
  },

  async getFairCatalogs() {
    const response = await apiClient.get('/fair/catalogs')
    return response.data
  },

  async getFairCatalogDetails(catalogId) {
    // URL encode the catalog ID
    const encodedId = encodeURIComponent(catalogId)
    const response = await apiClient.get(`/fair/catalogs/${encodedId}`)
    return response.data
  }
}
