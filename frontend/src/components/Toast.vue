<template>
  <div class="toast-container">
    <transition-group name="toast" tag="div">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
      >
        <div class="toast-icon">
          <i :class="getIcon(toast.type)"></i>
        </div>
        <div class="toast-content">
          <div class="toast-title" v-if="toast.title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button class="toast-close" @click="removeToast(toast.id)" aria-label="Close">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script>
export default {
  name: 'Toast',
  data() {
    return {
      toasts: []
    }
  },
  methods: {
    show(message, type = 'info', title = '', duration = 5000) {
      const id = Date.now() + Math.random()
      const toast = { id, message, type, title }
      
      this.toasts.push(toast)
      
      if (duration > 0) {
        setTimeout(() => {
          this.removeToast(id)
        }, duration)
      }
      
      return id
    },
    
    removeToast(id) {
      this.toasts = this.toasts.filter(t => t.id !== id)
    },
    
    success(message, title = 'Success') {
      return this.show(message, 'success', title)
    },
    
    error(message, title = 'Error') {
      return this.show(message, 'error', title, 7000) // Longer duration for errors
    },
    
    warning(message, title = 'Warning') {
      return this.show(message, 'warning', title)
    },
    
    info(message, title = 'Info') {
      return this.show(message, 'info', title)
    },
    
    getIcon(type) {
      const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
      }
      return icons[type] || icons.info
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  margin-bottom: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-left: 4px solid;
  animation: slideIn 0.3s ease-out;
}

.toast-success {
  border-left-color: #28a745;
}

.toast-error {
  border-left-color: #dc3545;
}

.toast-warning {
  border-left-color: #ffc107;
}

.toast-info {
  border-left-color: #17a2b8;
}

.toast-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.toast-success .toast-icon {
  color: #28a745;
}

.toast-error .toast-icon {
  color: #dc3545;
}

.toast-warning .toast-icon {
  color: #ffc107;
}

.toast-info .toast-icon {
  color: #17a2b8;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  margin-bottom: 4px;
  color: #333;
}

.toast-message {
  color: #666;
  font-size: 14px;
  word-wrap: break-word;
}

.toast-close {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0;
  font-size: 18px;
  flex-shrink: 0;
  transition: color 0.2s;
}

.toast-close:hover {
  color: #333;
}

/* Animations */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .toast-container {
    left: 20px;
    right: 20px;
    max-width: none;
  }
}
</style>
