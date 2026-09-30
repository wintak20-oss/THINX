<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <div class="header-content">
          <div class="header-left">
            <h1>🧠 Thinx</h1>
            <p class="subtitle">Human Trafficking Research Platform</p>
            <p class="tagline">Analyze interview data without coding skills</p>
          </div>
          <div v-if="user" class="header-right">
            <button class="btn btn-help" @click="showHelp = !showHelp" :title="showHelp ? 'Hide help' : 'Show help'">
              <i class="fas fa-question-circle"></i>
              <span class="btn-text">Help</span>
            </button>
            <span class="user-info" :title="'Logged in as ' + user.username">
              <i class="fas fa-user-circle"></i> 
              <span class="username">{{ user.username }}</span>
            </span>
            <button class="btn btn-logout" @click="handleLogout" title="Sign out of your account">
              <i class="fas fa-sign-out-alt"></i> 
              <span class="btn-text">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Help Panel -->
    <transition name="slide-down">
      <div v-if="showHelp && user" class="help-panel">
        <div class="container">
          <div class="help-content">
            <h3><i class="fas fa-life-ring"></i> Quick Help</h3>
            <div class="help-grid">
              <div class="help-card">
                <div class="help-icon">🔌</div>
                <h4>Database Connection</h4>
                <p>Connect to your AllegroGraph database to store and query research data. You'll need the server address, repository name, and credentials from your admin.</p>
              </div>
              <div class="help-card">
                <div class="help-icon">📊</div>
                <h4>Data Workflow</h4>
                <p>Upload interview data (Excel/JSON), map columns to standard format, and automatically process into structured data ready for analysis.</p>
              </div>
              <div class="help-card">
                <div class="help-icon">🤖</div>
                <h4>AI Smart Mapper</h4>
                <p>Let AI automatically suggest how your data columns match our standard format. Download a model like "llama3.2" to get started.</p>
              </div>
              <div class="help-card">
                <div class="help-icon">📈</div>
                <h4>View Data</h4>
                <p>Explore your processed data with interactive tables and visualizations. Run queries to find patterns and generate insights.</p>
              </div>
            </div>
            <div class="help-footer">
              <p><strong>Need more help?</strong> Check the <a href="https://github.com/Justin2280/DataScienceInPractice" target="_blank">documentation</a> or contact your system administrator.</p>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <main class="app-main">
      <div class="container">
        <router-view @login="handleLogin" :user="user" />
      </div>
    </main>

    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2025 Leiden University - Thinx (Data Science in Practice)</p>
        <p class="footer-links">
          <a href="https://github.com/Justin2280/DataScienceInPractice" target="_blank">Documentation</a> • 
          <a href="https://github.com/Justin2280/DataScienceInPractice/blob/main/README.md" target="_blank">User Guide</a> • 
          <a href="mailto:support@example.com">Contact Support</a>
        </p>
      </div>
    </footer>

    <!-- Toast Notifications -->
    <Toast ref="toast" />
  </div>
</template>

<script>
import Toast from './components/Toast.vue'

export default {
  name: 'App',
  components: {
    Toast
  },
  data() {
    return {
      user: null,
      showHelp: false
    };
  },
  provide() {
    return {
      toast: this.$refs.toast
    }
  },
  mounted() {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        this.user = JSON.parse(storedUser);
      } catch (e) {
        // Invalid stored user data, clear it
        if (import.meta.env.MODE === 'development') {
          console.error('Error parsing stored user:', e);
        }
        localStorage.removeItem('user');
      }
    }
    
    // Redirect to login if not logged in and not on auth pages
    if (!this.user && !['Login', 'Register'].includes(this.$route.name)) {
      this.$router.push('/login');
    }
  },
  methods: {
    handleLogin(userData) {
      this.user = userData;
      this.showHelp = false;
    },
    handleLogout() {
      if (confirm('Are you sure you want to logout?')) {
        this.user = null;
        this.showHelp = false;
        localStorage.removeItem('user');
        this.$router.push('/login');
      }
    }
  },
  watch: {
    $route(to) {
      // Redirect to login if user is not logged in and trying to access protected routes
      if (!this.user && !['Login', 'Register'].includes(to.name)) {
        this.$router.push('/login');
      }
      // Hide help when navigating
      this.showHelp = false;
    }
  }
}
</script>

<style>
/* === HEADER === */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  font-size: 2rem;
  margin-bottom: 0.3rem;
}

.header-left .subtitle {
  font-size: 1rem;
  opacity: 0.95;
  margin: 0 0 0.2rem 0;
  font-weight: 500;
}

.header-left .tagline {
  font-size: 0.85rem;
  opacity: 0.85;
  margin: 0;
  font-style: italic;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-info {
  font-size: 0.95rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.15);
  padding: 0.5rem 1rem;
  border-radius: 6px;
}

.user-info i {
  font-size: 1.3rem;
}

.username {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-help,
.btn-logout {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-help:hover,
.btn-logout:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.btn-text {
  display: inline;
}

@media (max-width: 768px) {
  .btn-text {
    display: none;
  }
  .header-content {
    justify-content: center;
    text-align: center;
  }
  .header-left {
    width: 100%;
  }
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.app-main {
  min-height: calc(100vh - 200px);
  padding: 2rem 0;
}

/* === HELP PANEL === */
.help-panel {
  background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
  border-bottom: 2px solid #dee2e6;
  padding: 2rem 0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.help-content h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.help-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.help-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.help-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.help-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.help-card h4 {
  color: #667eea;
  margin: 0.5rem 0;
  font-size: 1.1rem;
}

.help-card p {
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.help-footer {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.help-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.help-footer a:hover {
  text-decoration: underline;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-20px);
}

/* === FOOTER === */
.app-footer {
  background-color: #2c3e50;
  color: white;
  text-align: center;
  padding: 1.5rem 0;
  margin-top: 2rem;
}

.app-footer p {
  margin: 0.3rem 0;
  font-size: 0.9rem;
}

.footer-links {
  opacity: 0.8;
  font-size: 0.85rem;
}

.footer-links a {
  color: #a8b7c7;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: white;
}

/* Global button styles */
button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

button.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

button.secondary {
  background-color: #6c757d;
  color: white;
}

button.secondary:hover {
  background-color: #5a6268;
}

button.danger {
  background-color: #dc3545;
  color: white;
}

button.danger:hover {
  background-color: #c82333;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Global card styles */
.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.card-header {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* Form styles */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Table styles */
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.data-table tr:hover {
  background-color: #f8f9fa;
}

/* Alert styles */
.alert {
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.alert.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert.info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

/* Loading spinner */
.loading {
  text-align: center;
  padding: 2rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
