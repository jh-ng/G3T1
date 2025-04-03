<template>
  <v-app style="height: 100vh; width: 100vw">
    <v-app-bar color="primary">
      <v-app-bar-nav-icon variant="text" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>

      <v-toolbar-title>Travel Planner</v-toolbar-title>

      <v-spacer></v-spacer>

      <template v-if="!isAuthenticated">
        <v-btn to="/login" variant="text">Login</v-btn>
        <v-btn to="/register" variant="text">Register</v-btn>
      </template>
      <template v-else>
        <span class="mr-4">Welcome, {{ currentUser?.username }}</span>
        <v-btn @click="handleLogout" variant="text">Logout</v-btn>
      </template>
      <!-- Notification Bell Icon -->
      <v-btn icon variant="text" @click="toggleNotificationPanel" class="notification-bell">
        <v-badge :content="unreadCount" :model-value="unreadCount > 0" color="error">
          <v-icon>mdi-bell</v-icon>
        </v-badge>
      </v-btn>

      <v-btn icon="mdi-dots-vertical" variant="text"></v-btn>
    </v-app-bar>
    <v-navigation-drawer v-model="drawer" temporary style="height: 100vh; display: flex; flex-direction: column">
      <v-list>
        <v-list-item to="/" title="Home"></v-list-item>
        <v-list-item to="/itinerary" title="Itinerary Planner"></v-list-item>
      </v-list>
      <v-divider></v-divider>
      <v-spacer></v-spacer>
      <div class="pa-4">
        <v-btn rounded block color="primary">Create Post</v-btn>
      </div>
    </v-navigation-drawer>
    <!-- Notification Drawer -->
    <v-navigation-drawer v-model="notificationDrawer" temporary location="right" width="320">
      <v-toolbar color="primary" dark>
        <v-toolbar-title>Notifications</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon @click="notificationDrawer = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>

      <v-list v-if="notifications.length === 0">
        <v-list-item>
          <v-list-item-title class="text-center py-4">
            You have no notifications
          </v-list-item-title>
        </v-list-item>
      </v-list>

      <v-list v-else>
        <v-list-item v-for="notification in notifications" :key="notification.id" @click="markAsRead(notification.id)"
          :class="{ 'unread-notification': !notification.read }">
          <v-list-item-title>{{ notification.title }}</v-list-item-title>
          <v-list-item-subtitle>{{ notification.message }}</v-list-item-subtitle>
          <v-list-item-subtitle class="text-caption text-grey">
            {{ formatTime(notification.timestamp) }}
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>

      <template v-if="unreadCount > 0">
        <v-divider></v-divider>
        <div class="pa-2">
          <v-btn block variant="text" color="primary" @click="markAllAsRead">
            Mark all as read
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
import authService from './services/auth';

export default {
  name: "App",
  data() {
    return {
      drawer: false,
      isAuthenticated: false,
      currentUser: null
    }
  },
  created() {
    this.checkAuth();
    // Add event listener for storage changes
    window.addEventListener('storage', this.checkAuth);
  },
  beforeUnmount() {
    // Remove event listener
    window.removeEventListener('storage', this.checkAuth);
  },
  methods: {
    async checkAuth() {
      this.isAuthenticated = authService.isAuthenticated();
      if (this.isAuthenticated) {
        this.currentUser = authService.getCurrentUser();
        if (!this.currentUser) {
          this.handleLogout();
          return;
        }
        // Verify token validity
        const isValid = await authService.verifyToken();
        if (!isValid) {
          this.handleLogout();
        }
      } else {
        this.currentUser = null;
      }
    },
    handleLogout() {
      authService.logout();
      this.isAuthenticated = false;
      this.currentUser = null;
      this.$router.push('/login');
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
.unread-notification {
  background-color: #f5f5f5;
  border-left: 4px solid var(--v-primary-base);
}

.notification-bell {
  position: relative;
}

.navbar {
  background-color: #ffffff;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-brand a {
  font-size: 1.5rem;
  font-weight: bold;
  color: #4CAF50;
  text-decoration: none;
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-link {
  color: #666;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: #f5f5f5;
  color: #4CAF50;
}

.welcome-text {
  color: #666;
  margin-right: 1rem;
}

.router-link-active {
  color: #4CAF50;
  font-weight: bold;
}
</style>
