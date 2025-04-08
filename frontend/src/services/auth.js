import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth';
const USER_API_URL = 'http://localhost:8000/api'; // Route through Kong to match User_app.py endpoint

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
    try {
      const response = await axios.post(`${API_URL}/register`, userData);
      
      if (response.data.user && userData.email) {
        // Update user data with email from registration
        response.data.user.email = userData.email;
        if (response.data.token) {
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('user', JSON.stringify(response.data.user));
        }
      }
      
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async login(username, password) {
    try {
      const response = await axios.post(`${API_URL}/login`, {
        username,
        password
      });
    
      if (response.data.token) {
        // Store initial data
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Set Authorization header for future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
        
        // Verify token to get additional user info
        const verifyResponse = await axios.get(`${API_URL}/verify-token`);
        console.log('Verify token response:', verifyResponse.data);
        
        if (verifyResponse.data && verifyResponse.data.user) {
          // Update stored user data with additional info from token verification
          const updatedUser = {
            ...response.data.user,
            email: verifyResponse.data.user.email
          };
          localStorage.setItem('user', JSON.stringify(updatedUser));
        }
      }
    
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
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
      console.log('Verify token response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Token verification error:', error);
      this.logout();
      return null;
    }
  }

  // Add method to update first login status
  async updateFirstLoginStatus() {
    try {
      console.log('[DEBUG] Starting updateFirstLoginStatus');
      console.log('[DEBUG] Current token:', this.getToken());
      console.log('[DEBUG] Current user from localStorage:', this.getCurrentUser());
      
      // Get token info to verify what's in the JWT
      const tokenInfo = this.getTokenInfo();
      console.log('[DEBUG] Token payload:', tokenInfo);
      
      const response = await axios.post(`${API_URL}/update-first-login`);
      console.log('[DEBUG] API response:', response.data);
      
      if (response.data) {
        // Update the user in localStorage
        const user = this.getCurrentUser();
        console.log('[DEBUG] User before update:', user);
        
        if (user) {
          user.is_first_login = false;
          localStorage.setItem('user', JSON.stringify(user));
          console.log('[DEBUG] User after update:', this.getCurrentUser());
        } else {
          console.log('[DEBUG] No user found in localStorage to update');
        }
      }
      
      return response.data;
    } catch (error) {
      console.error('[DEBUG] Error updating first login status:', error);
      console.error('[DEBUG] Error response:', error.response?.data);
      return false;
    }
  }

  // Add method to create user profile
  async createUserProfile(preferences) {
    try {
      if (!preferences || Object.keys(preferences).length === 0) {
        throw new Error('No preferences provided');
      }

      // First get user data from verify-token endpoint
      const verifyResponse = await axios.get(`${API_URL}/verify-token`);
      console.log('Token verification response:', verifyResponse.data);

      if (!verifyResponse.data || !verifyResponse.data.user) {
        throw new Error('Could not verify user token');
      }

      // Get current stored data
      const stored = this.getCurrentUser();
      if (!stored) {
        throw new Error('Please log in again');
      }

      // Get verified user data
      const verifiedUser = verifyResponse.data.user;

      // Update stored user data with verified data
      const updatedUser = {
        ...stored,
        email: verifiedUser.email,
        id: verifiedUser.user_id || stored.id,
        username: verifiedUser.username || stored.username
      };

      // Store updated user data
      localStorage.setItem('user', JSON.stringify(updatedUser));
      console.log('Updated stored user data:', updatedUser);

      // Prepare data for user creation - no email needed
      const createData = {
        user_id: updatedUser.id,
        username: updatedUser.username,
        taste_preferences: preferences
      };

      console.log('Data for user creation:', createData);

      // Validate required fields
      const missing = [];
      if (!createData.user_id) missing.push('user_id');
      if (!createData.username) missing.push('username');
      if (missing.length > 0) {
        console.error('Missing required fields:', missing);
        throw new Error(`Missing required fields: ${missing.join(', ')}`);
      }

      // Create user through User microservice
      const response = await axios.post(`${USER_API_URL}/users/create`, createData);
      console.log('User creation response:', response.data);

      // Validate response
      if (!response.data) {
        throw new Error('Empty response from user service');
      }

      if (response.data.error) {
        throw new Error(`User service error: ${response.data.error}`);
      }

      // Return successful response
      return response.data;
    } catch (error) {
      // Log detailed error information
      console.error('Error in createUserProfile:', {
        error: error.message,
        response: error.response?.data,
        status: error.response?.status,
        user: this.getCurrentUser()
      });

      // Re-throw with more specific message
      if (error.response?.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      } else if (error.response?.status === 400) {
        throw new Error('Invalid data provided: ' + (error.response.data.error || error.message));
      } else {
        throw new Error('Failed to create user profile: ' + error.message);
      }
    }
  }
}

export default new AuthService();
