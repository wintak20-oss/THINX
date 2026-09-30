<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <i class="fas fa-lock"></i>
        <h2>Login</h2>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">
            <i class="fas fa-user"></i> Username
          </label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Enter your username"
            required
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="password">
            <i class="fas fa-key"></i> Password
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter your password"
            required
            autocomplete="current-password"
          />
        </div>

        <div v-if="error" class="error-message">
          <i class="fas fa-exclamation-circle"></i> {{ error }}
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          <i class="fas fa-sign-in-alt"></i>
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <div class="login-footer">
        <p>
          Don't have an account?
          <router-link to="/register">Register here</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false
    };
  },
  methods: {
    async handleLogin() {
      this.error = '';
      this.loading = true;

      try {
        const response = await axios.post('http://localhost:5000/api/login', {
          username: this.username,
          password: this.password
        });

        if (response.data.success) {
          // Store user data in localStorage
          localStorage.setItem('user', JSON.stringify(response.data.user));
          
          // Emit login event to parent
          this.$emit('login', response.data.user);
          
          // Redirect to home
          this.$router.push('/');
        } else {
          this.error = response.data.error || 'Login failed';
        }
      } catch (err) {
        console.error('Login error:', err);
        if (err.response && err.response.data) {
          this.error = err.response.data.error || 'Login failed';
        } else {
          this.error = 'Unable to connect to server';
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 2rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 2.5rem;
  width: 100%;
  max-width: 450px;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header i {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.login-header h2 {
  margin: 0;
  font-size: 2rem;
  color: #333;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
  font-weight: 500;
  font-size: 0.95rem;
}

.form-group label i {
  margin-right: 0.5rem;
  color: #667eea;
}

.form-group input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 0.875rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  font-size: 0.95rem;
}

.error-message i {
  margin-right: 0.5rem;
}

.btn-block {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  margin-top: 0.5rem;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-footer {
  margin-top: 2rem;
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.login-footer p {
  margin: 0;
  color: #6c757d;
}

.login-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.login-footer a:hover {
  color: #764ba2;
  text-decoration: underline;
}
</style>
