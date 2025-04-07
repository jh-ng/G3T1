import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth';

// Add axios interceptor to add JWT token and Content-Type to all requests
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Add Content-Type header
    config.headers['Content-Type'] = 'application/json';
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

class AuthService {
  async register(userData) {
    const response = await axios.post(`${API_URL}/register`, userData);
    return response.data;
  }

  async login(username, password) {
    const response = await axios.post(`${API_URL}/login`, {
      username,
      password
    });
    
    if (response.data.token) {
      // Store token and user data
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      // Set Authorization header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
    }
    
    return response.data;
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
  }

  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  getToken() {
    return localStorage.getItem('token');
  }

  isAuthenticated() {
    const token = this.getToken();
    if (!token) return false;
    
    try {
      // Check if token is expired
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));

      const payload = JSON.parse(jsonPayload);
      const now = Date.now() / 1000;
      
      return payload.exp > now;
    } catch (err) {
      return false;
    }
  }

  // Add method to check if it's the user's first login
  isFirstLogin() {
    const user = this.getCurrentUser();
    return user ? user.is_first_login : false;
  }

  // Get information from the JWT token
  getTokenInfo() {
    const token = this.getToken();
    if (!token) return null;
    
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));

      return JSON.parse(jsonPayload);
    } catch (err) {
      return null;
    }
  }

  // Add method to verify token validity
  async verifyToken() {
    try {
      const response = await axios.get(`${API_URL}/verify-token`);
      return response.data.valid;
    } catch (error) {
      this.logout();
      return false;
    }
  }

  // Add method to update first login status
  async updateFirstLoginStatus() {
    try {
      const response = await axios.post(`${API_URL}/update-first-login`);
      
      if (response.data) {
        // Update the user in localStorage
        const user = this.getCurrentUser();
        if (user) {
          user.is_first_login = false;
          localStorage.setItem('user', JSON.stringify(user));
        }
      }
      
      return response.data;
    } catch (error) {
      console.error('Error updating first login status:', error);
      return false;
    }
  }
}

export default new AuthService();