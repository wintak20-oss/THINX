<template>
  <div class="data-viewer">
    <div class="card">
      <div class="card-header">
        <h2><i class="fas fa-table"></i> Data Viewer</h2>
        <button class="btn btn-secondary" @click="$router.push('/')">
          <i class="fas fa-arrow-left"></i> Back to Connections
        </button>
      </div>

      <!-- Active Connection Info -->
      <div v-if="activeConnection" class="active-connection-info">
        <strong>Active Connection:</strong> {{ activeConnection.name }}
        ({{ activeConnection.host }}:{{ activeConnection.port }}/{{ activeConnection.repository }})
      </div>

      <div v-else class="alert error">
        No active connection. Please select a connection first.
      </div>

      <!-- Statistics -->
      <div v-if="statistics" class="statistics-grid">
        <div class="stat-card victims">
          <div class="stat-icon"><i class="fas fa-users"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total_victims }}</div>
            <div class="stat-label">Victims</div>
          </div>
        </div>
        <div class="stat-card crimes">
          <div class="stat-icon"><i class="fas fa-exclamation-triangle"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total_incidents }}</div>
            <div class="stat-label">Incidents</div>
          </div>
        </div>
        <div class="stat-card borders">
          <div class="stat-icon"><i class="fas fa-map-marked-alt"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total_locations }}</div>
            <div class="stat-label">Locations</div>
          </div>
        </div>
        <div class="stat-card triples">
          <div class="stat-icon"><i class="fas fa-database"></i></div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total_triples.toLocaleString() }}</div>
            <div class="stat-label">Total Triples</div>
          </div>
        </div>
      </div>

      <!-- Data Controls -->
      <div class="data-controls">
        <button class="btn btn-primary" @click="loadData" :disabled="loading">
          <i :class="['fas', loading ? 'fa-spinner fa-spin' : 'fa-sync-alt']"></i>
          {{ loading ? 'Loading...' : 'Refresh Data' }}
        </button>
        <div class="pagination-controls">
          <label>
            <strong>Results per page:</strong>
            <select v-model.number="limit" @change="loadData" class="form-select">
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
              <option :value="200">200</option>
            </select>
          </label>
        </div>
      </div>

      <!-- Data Table -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Loading data...</p>
      </div>

      <div v-else-if="data.length > 0" class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Victim ID</th>
              <th>Age</th>
              <th>Gender</th>
              <th>Nationality</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in data" :key="index">
              <td><strong>{{ truncateUri(row.victim) }}</strong></td>
              <td>{{ cleanLiteral(row.age) }}</td>
              <td>{{ cleanLiteral(row.gender) }}</td>
              <td>{{ cleanLiteral(row.nationality) }}</td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div class="pagination">
          <button
            class="btn btn-secondary"
            @click="previousPage"
            :disabled="offset === 0"
          >
            <i class="fas fa-chevron-left"></i> Previous
          </button>
          <span class="page-info">
            Showing <strong>{{ offset + 1 }}</strong> - <strong>{{ Math.min(offset + limit, offset + data.length) }}</strong>
          </span>
          <button
            class="btn btn-secondary"
            @click="nextPage"
            :disabled="data.length < limit"
          >
            Next <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>

      <div v-else class="empty-state">
        <i class="fas fa-database"></i>
        <p>No data found in this repository.</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'DataViewer',

  components: {
  },

  props: {
    user: {
      type: Object,
      required: false
    }
  },

  data() {
    return {
      activeConnection: null,
      data: [],
      statistics: null,
      loading: false,
      limit: 50,
      offset: 0
    }
  },

  mounted() {
    this.loadActiveConnection()
  },

  methods: {
    async loadActiveConnection() {
      try {
        const response = await api.getActiveConnection()
        if (response.success) {
          this.activeConnection = response.connection
          this.loadData()
          this.loadStatistics()
        } else {
          // No active connection
          this.$router.push('/')
        }
      } catch (error) {
        console.error('Failed to load active connection:', error)
        this.$router.push('/')
      }
    },

    async loadData() {
      if (!this.activeConnection) return

      this.loading = true
      try {
        const response = await api.getData(
          this.activeConnection.id,
          this.limit,
          this.offset
        )
        if (response.success) {
          this.data = response.data
        }
      } catch (error) {
        console.error('Failed to load data:', error)
      } finally {
        this.loading = false
      }
    },

    async loadStatistics() {
      if (!this.activeConnection) return

      try {
        const response = await api.getStatistics(this.activeConnection.id)
        if (response.success) {
          this.statistics = response.statistics
        }
      } catch (error) {
        console.error('Failed to load statistics:', error)
      }
    },

    previousPage() {
      if (this.offset >= this.limit) {
        this.offset -= this.limit
        this.loadData()
      }
    },

    nextPage() {
      this.offset += this.limit
      this.loadData()
    },

    truncateUri(uri) {
      if (!uri) return 'N/A'
      // Remove angle brackets if present (e.g., <http://...>)
      const cleaned = uri.replace(/^<(.+)>$/, '$1')
      // Extract the last part after # or /
      const match = cleaned.match(/[#/]([^#/]+)$/)
      return match ? match[1] : cleaned
    },

    cleanLiteral(value) {
      if (!value) return 'N/A'
      // Remove RDF literal type annotations like ^^<http://www.w3.org/2001/XMLSchema#string>
      const cleaned = value.replace(/\^\^<[^>]+>$/, '')
      // Remove quotes
      return cleaned.replace(/^"(.*)"$/, '$1')
    }
  }
}
</script>

<style scoped>
.data-viewer {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 2rem;
}

.card-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.card-header h2 i {
  margin-right: 0.5rem;
}

.active-connection-info {
  background: linear-gradient(135deg, #e7f3ff 0%, #e1e9ff 100%);
  border: 1px solid #b3d9ff;
  border-radius: 8px;
  padding: 1rem 2rem;
  margin: 1.5rem 2rem;
  color: #004085;
  font-size: 0.95rem;
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin: 1.5rem 2rem 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-card.victims {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.crimes {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-card.borders {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-card.triples {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-icon {
  font-size: 2.5rem;
  margin-right: 1rem;
  opacity: 0.9;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  line-height: 1;
}

.stat-label {
  font-size: 1rem;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.data-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 1.5rem 2rem;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-controls label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.pagination-controls select {
  padding: 0.5rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.pagination-controls select:hover {
  border-color: #667eea;
}

.table-container {
  overflow-x: auto;
  margin: 0 2rem 1.5rem;
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 0.95rem;
}

.data-table th {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th:first-child {
  border-top-left-radius: 8px;
}

.data-table th:last-child {
  border-top-right-radius: 8px;
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  background: white;
  transition: background-color 0.2s;
}

.data-table tr:hover td {
  background: #f8f9fa;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:last-child td:first-child {
  border-bottom-left-radius: 8px;
}

.data-table tr:last-child td:last-child {
  border-bottom-right-radius: 8px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0 2rem 2rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.pagination button {
  padding: 0.5rem 1rem;
  min-width: 100px;
  transition: all 0.2s;
}

.pagination button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #495057;
  font-weight: 600;
  font-size: 1rem;
}

.page-info strong {
  color: #667eea;
  font-size: 1.1rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}
</style>
