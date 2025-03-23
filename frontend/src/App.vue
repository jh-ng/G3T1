<template>
  <v-app style="height: 100vh; width: 100vw">
    <v-app-bar color="primary">
      <v-app-bar-nav-icon variant="text" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>

      <v-toolbar-title>App name</v-toolbar-title>

      <v-spacer></v-spacer>

      <template v-if="$vuetify.display.mdAndUp">
        <v-btn icon="mdi-magnify" variant="text"></v-btn>

        <v-btn icon="mdi-filter" variant="text"></v-btn>
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
        <v-list-item to="/itinerary" title="itinerary planner"></v-list-item>
      </v-list>
      <v-divider></v-divider>
      <v-spacer></v-spacer>
      <div class="pa-4">
        <v-btn rounded block color="primary"> Create Post </v-btn>
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
export default {
  name: "App",
  data() {
    return {
      drawer: false,
      notificationDrawer: false,
      notifications: []
    }
  },
  computed: {
    unreadCount() {
      return this.notifications.filter(notification => !notification.read).length;
    }
  },
  mounted() {
    // Simulate fetching notifications (to be replace with actual API call)
    setTimeout(() => {
      this.notifications = [
        {
          id: 1,
          title: 'New Message',
          message: 'You have received a new message from Alex',
          timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
          read: false
        },
        {
          id: 2,
          title: 'System Update',
          message: 'The system has been updated to version 2.0',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
          read: false
        },
        {
          id: 3,
          title: 'Task Completed',
          message: 'Your scheduled task has been completed successfully',
          timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1 day ago
          read: true
        },
        {
          id: 4,
          title: 'Welcome',
          message: 'Welcome to our application! Get started by exploring the dashboard',
          timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
          read: true
        }
      ];
    }, 1000);
  },
  methods: {
    toggleNotificationPanel() {
      this.notificationDrawer = !this.notificationDrawer;
      if (this.drawer && this.notificationDrawer) {
        this.drawer = false;
      }
    },
    markAsRead(id) {
      const notification = this.notifications.find(n => n.id === id);
      if (notification && !notification.read) {
        notification.read = true;
        
        // call an API to update the read status
      
      }
    },
    markAllAsRead() {
      this.notifications.forEach(notification => {
        notification.read = true;
      });
      
      // Here call an API to update all statuses
      
    },
    formatTime(timestamp) {
      const now = new Date();
      const diff = now - timestamp;
      
      // Less than a minute
      if (diff < 60 * 1000) {
        return 'Just now';
      }
      
      // Less than an hour
      if (diff < 60 * 60 * 1000) {
        const minutes = Math.floor(diff / (60 * 1000));
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
      }
      
      // Less than a day
      if (diff < 24 * 60 * 60 * 1000) {
        const hours = Math.floor(diff / (60 * 60 * 1000));
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
      }
      
      // Less than a week
      if (diff < 7 * 24 * 60 * 60 * 1000) {
        const days = Math.floor(diff / (24 * 60 * 60 * 1000));
        return `${days} day${days > 1 ? 's' : ''} ago`;
      }
      
      // Otherwise format as a date
      return timestamp.toLocaleDateString();
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
</style>
