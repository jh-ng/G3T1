const config = {
    // API configuration
    api: {
        // Base URL for the notification API
        notificationBaseUrl: 'https://personal-nrm7dwxa.outsystemscloud.com/NotificationService/rest/NotificationAPI',
        timeout: 10000
    },

    // Notification types
    notificationTypes: {
        REPLY: 'reply',
        COMMENT: 'comment',
        LIKE: 'like',
        SYSTEM: 'system'
    },

    // Notification Service Configuration
    notifications: {
        // Polling interval for real-time updates 
        pollingInterval: 60000,
        maxNotifications: 50,
        typeTitles: {
            'reply': 'New Reply',
            'comment': 'New Comment',
            'like': 'New Like',
            'system': 'System Update'
        }
    }
};

export default config;