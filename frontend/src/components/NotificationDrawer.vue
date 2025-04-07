<template>
  <v-navigation-drawer
    v-model="isOpen"
    location="right"
    temporary
    width="320"
    @click:outside="emitClose"
  >
    <v-toolbar color="primary" dark>
      <v-toolbar-title>Notifications</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="emitClose">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-toolbar>

    <div v-if="isLoading" class="pa-4 text-center">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <v-alert type="error" v-else-if="error" class="ma-4">
      {{ error }}
    </v-alert>

    <v-list v-else-if="notifications.length === 0">
      <v-list-item>
        <v-list-item-title class="text-center">No notifications</v-list-item-title>
      </v-list-item>
    </v-list>

    <v-list v-else>
      <v-list-item
        v-for="notification in notifications"
        :key="notification.Id"
        @click="markAsRead(notification.Id)"
        :class="{ 'unread-notification': !notification.IsRead }"
      >
        <v-list-item-content>
          <v-list-item-title>{{ getTitle(notification) }}</v-list-item-title>
          <v-list-item-subtitle>{{ notification.Message }}</v-list-item-subtitle>
          <v-list-item-subtitle class="text-caption text-grey">
            {{ formatTime(notification.CreatedOn) }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </v-list>

    <v-divider v-if="unreadCount > 0" class="mt-2"></v-divider>
    <v-btn
      v-if="unreadCount > 0"
      block
      variant="text"
      color="primary"
      class="mt-2"
      @click="markAllAsRead"
    >
      Mark all as read
    </v-btn>
  </v-navigation-drawer>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue';
import notificationService from '@/services/notificationService';

const props = defineProps({ show: Boolean });
const emit = defineEmits(['close']);
const isOpen = ref(props.show);

watch(() => props.show, (val) => isOpen.value = val);

const emitClose = () => {
  isOpen.value = false;
  emit('close');
};

const isLoading = notificationService.isLoading;
const error = notificationService.error;
const notifications = notificationService.notifications;
const unreadCount = notificationService.unreadCount;

const markAsRead = async (id) => {
  await notificationService.markAsRead(id);
};

const markAllAsRead = async () => {
  await notificationService.markAllAsRead();
};

const getTitle = (n) => notificationService.getNotificationTitle(n);
const formatTime = (t) => notificationService.formatTime(t);
</script>

<style scoped>
.unread-notification {
  background-color: #f5f5f5;
  border-left: 3px solid #2196f3;
}
</style>
