<template>
  <div class="connection-list">
    <div v-if="connections.length === 0" class="empty-state">
      <p>📭 No connections yet. Add your first connection to get started!</p>
    </div>

    <div v-else class="connections-grid">
      <div
        v-for="conn in connections"
        :key="conn.id"
        :class="['connection-card', { active: conn.is_active }]"
      >
        <div class="connection-header">
          <h3>{{ conn.name }}</h3>
          <span v-if="conn.is_active" class="badge active">Active</span>
        </div>

        <div class="connection-details">
          <div class="detail-row">
            <span class="label">🖥️ Host:</span>
            <span class="value">{{ conn.host }}:{{ conn.port }}</span>
          </div>
          <div class="detail-row">
            <span class="label">📦 Repository:</span>
            <span class="value">{{ conn.repository }}</span>
          </div>
          <div class="detail-row">
            <span class="label">👤 Username:</span>
            <span class="value">{{ conn.username }}</span>
          </div>
          
          <!-- FAIR Data Point catalog metadata -->
          <div v-if="conn.catalog_title" class="catalog-metadata">
            <div class="catalog-badge">📚 FAIR Catalog</div>
            <div class="detail-row">
              <span class="label">Catalog:</span>
              <span class="value">{{ conn.catalog_title }}</span>
            </div>
            <div v-if="conn.catalog_publisher" class="detail-row">
              <span class="label">Publisher:</span>
              <span class="value">{{ conn.catalog_publisher }}</span>
            </div>
            <div v-if="conn.catalog_contact" class="detail-row">
              <span class="label">Contact:</span>
              <span class="value">{{ conn.catalog_contact }}</span>
            </div>
            <div v-if="conn.dataset_count" class="detail-row">
              <span class="label">Datasets:</span>
              <span class="value">{{ conn.dataset_count }}</span>
            </div>
          </div>
        </div>

        <div class="connection-actions">
          <button
            v-if="!conn.is_active"
            class="secondary small"
            @click="$emit('activate', conn)"
          >
            ✓ Activate
          </button>
          <button class="primary small" @click="$emit('view-data', conn)">
            📊 View Data
          </button>
          <button class="secondary small" @click="$emit('edit', conn)">
            ✏️ Edit
          </button>
          <button class="danger small" @click="$emit('delete', conn)">
            🗑️ Delete
          </button>
        </div>

        <div class="connection-meta">
          <small>Created: {{ formatDate(conn.created_at) }}</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConnectionList',

  props: {
    connections: {
      type: Array,
      required: true
    }
  },

  emits: ['activate', 'edit', 'delete', 'view-data'],

  methods: {
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
  }
}
</script>

<style scoped>
.connection-list {
  margin-top: 2rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #6c757d;
}

.empty-state p {
  font-size: 1.1rem;
}

.connections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.connection-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.connection-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.connection-card.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.connection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.connection-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.connection-details {
  margin-bottom: 1rem;
}

.catalog-metadata {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 2px solid #e8f5e9;
}

.catalog-badge {
  display: inline-block;
  background: #4caf50;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  font-weight: 500;
  color: #495057;
}

.detail-row .value {
  color: #6c757d;
  text-align: right;
  word-break: break-all;
}

.connection-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.connection-actions button.small {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.connection-meta {
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
  color: #6c757d;
}

@media (max-width: 768px) {
  .connections-grid {
    grid-template-columns: 1fr;
  }
}
</style>
