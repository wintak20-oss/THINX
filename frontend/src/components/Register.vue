<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <i class="fas fa-user-plus"></i>
        <h2>Create Account</h2>
      </div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">
            <i class="fas fa-user"></i> Username
          </label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Choose a username (min 3 characters)"
            required
            autocomplete="username"
            minlength="3"
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
            placeholder="Choose a password (min 6 characters)"
            required
            autocomplete="new-password"
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">
            <i class="fas fa-check-circle"></i> Confirm Password
          </label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            required
            autocomplete="new-password"
          />
        </div>

        <div v-if="error" class="error-message">
          <i class="fas fa-exclamation-circle"></i> {{ error }}
        </div>

        <div v-if="success" class="success-message">
          <i class="fas fa-check-circle"></i> {{ success }}
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          <i class="fas fa-user-plus"></i>
          {{ loading ? 'Creating account...' : 'Register' }}
        </button>
      </form>

      <div class="register-footer">
        <p>
          Already have an account?
          <router-link to="/login">Login here</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Register',
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      error: '',
      success: '',
      loading: false
    };
  },
  methods: {
    async handleRegister() {
      this.error = '';
      this.success = '';

      // Validate passwords match
      if (this.password !== this.confirmPassword) {
        this.error = 'Passwords do not match';
        return;
      }

      // Validate username length
      if (this.username.length < 3) {
        this.error = 'Username must be at least 3 characters';
        return;
      }

      // Validate password length
      if (this.password.length < 6) {
        this.error = 'Password must be at least 6 characters';
        return;
      }

      this.loading = true;

      try {
        const response = await axios.post('http://localhost:5000/api/register', {
          username: this.username,
          password: this.password
        });

        if (response.data.success) {
          this.success = 'Account created successfully! Redirecting to login...';
          
          // Redirect to login after 2 seconds
          setTimeout(() => {
            this.$router.push('/login');
          }, 2000);
        } else {
          this.error = response.data.error || 'Registration failed';
        }
      } catch (err) {
        console.error('Registration error:', err);
        if (err.response && err.response.data) {
          this.error = err.response.data.error || 'Registration failed';
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
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 2rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 2.5rem;
  width: 100%;
  max-width: 450px;
}

.register-header {
  text-align: center;
  margin-bottom: 2rem;
}

.register-header i {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.register-header h2 {
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

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 0.875rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  font-size: 0.95rem;
}

.success-message i {
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

.register-footer {
  margin-top: 2rem;
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.register-footer p {
  margin: 0;
  color: #6c757d;
}

.register-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.register-footer a:hover {
  color: #764ba2;
  text-decoration: underline;
}
</style>
