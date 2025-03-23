<!-- NotificationSystem.vue -->
<template>
    <div class="notification-system">
      <!-- Bell icon in the navigation bar -->
      <div class="notification-bell" @click="toggleNotificationPanel">
        <div class="bell-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
        </div>
        <!-- Notification count badge -->
        <div v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</div>
      </div>
  
      <!-- Notification sidebar panel -->
      <div class="notification-panel" :class="{ 'is-open': isPanelOpen }">
        <div class="panel-header">
          <h3>Notifications</h3>
          <button class="close-button" @click="toggleNotificationPanel">×</button>
        </div>
        
        <div v-if="notifications.length === 0" class="no-notifications">
          <p>You have no notifications</p>
        </div>
        
        <!-- List of notifications -->
        <div v-else class="notification-list">
          <div 
            v-for="notification in notifications" 
            :key="notification.id" 
            class="notification-item"
            :class="{ 'unread': !notification.read }"
            @click="markAsRead(notification.id)"
          >
            <div class="notification-content">
              <div class="notification-title">{{ notification.title }}</div>
              <div class="notification-message">{{ notification.message }}</div>
              <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
            </div>
          </div>
        </div>
        
        <div class="panel-footer">
          <button v-if="unreadCount > 0" @click="markAllAsRead" class="mark-all-read">
            Mark all as read
          </button>
        </div>
      </div>
      
      <!-- Overlay that closes the panel when clicked outside -->
      <div 
        v-if="isPanelOpen" 
        class="panel-overlay"
        @click="toggleNotificationPanel"
      ></div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  
  // Sample notifications data (replace with your actual data source)
  const notifications = ref([]);
  const isPanelOpen = ref(false);
  
  // You would typically fetch these from an API
  onMounted(() => {
    // Simulate fetching notifications from an API
    setTimeout(() => {
      notifications.value = [
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
  });
  
  // Calculate number of unread notifications
  const unreadCount = computed(() => {
    return notifications.value.filter(notification => !notification.read).length;
  });
  
  // Toggle notification panel
  const toggleNotificationPanel = () => {
    isPanelOpen.value = !isPanelOpen.value;
  };
  
  // Mark a notification as read
  const markAsRead = (id) => {
    const notification = notifications.value.find(n => n.id === id);
    if (notification && !notification.read) {
      notification.read = true;
      
      // Here you would typically call an API to update the read status
      // api.updateNotificationStatus(id, true)
      
      // You could also navigate to a detailed view of the notification
      // router.push(`/notifications/${id}`);
    }
  };
  
  // Mark all notifications as read
  const markAllAsRead = () => {
    notifications.value.forEach(notification => {
      notification.read = true;
    });
    
    // Here you would typically call an API to update all statuses
    // api.markAllNotificationsAsRead()
  };
  
  // Format the timestamp in a human-readable way
  const formatTime = (timestamp) => {
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
  };
  </script>
  
  <style scoped>
  .notification-system {
    position: relative;
  }
  
  .notification-bell {
    position: relative;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    transition: background-color 0.2s;
  }
  
  .notification-bell:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  .bell-icon {
    color: #333;
  }
  
  .notification-badge {
    position: absolute;
    top: -2px;
    right: -2px;
    background-color: #f44336;
    color: white;
    font-size: 12px;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
  }
  
  .notification-panel {
    position: fixed;
    top: 0;
    right: -320px;
    width: 300px;
    height: 100vh;
    background-color: white;
    box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    transition: right 0.3s ease;
    display: flex;
    flex-direction: column;
  }
  
  .notification-panel.is-open {
    right: 0;
  }
  
  .panel-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.3);
    z-index: 999;
  }
  
  .panel-header {
    padding: 16px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .panel-header h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
  
  .close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
  }
  
  .notification-list {
    flex: 1;
    overflow-y: auto;
  }
  
  .notification-item {
    padding: 16px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    transition: background-color 0.2s;
    background-color: #f9f9f9;
  }
  
  .notification-item.unread {
    background-color: white;
    border-left: 3px solid #2196f3;
  }
  
  .notification-item:hover {
    background-color: #f0f0f0;
  }
  
  .notification-title {
    font-weight: bold;
    margin-bottom: 4px;
  }
  
  .notification-message {
    color: #666;
    font-size: 14px;
    margin-bottom: 6px;
  }
  
  .notification-time {
    color: #999;
    font-size: 12px;
  }
  
  .no-notifications {
    padding: 24px 16px;
    text-align: center;
    color: #666;
  }
  
  .panel-footer {
    padding: 12px 16px;
    border-top: 1px solid #eee;
    text-align: center;
  }
  
  .mark-all-read {
    background: none;
    border: none;
    color: #2196f3;
    cursor: pointer;
    padding: 6px 12px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 4px;
    transition: background-color 0.2s;
  }
  
  .mark-all-read:hover {
    background-color: rgba(33, 150, 243, 0.1);
  }
  </style>