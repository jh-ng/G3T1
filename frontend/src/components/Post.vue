<template>
  <div class="post">
    <div class="post-header">
      <router-link 
        :to="'/user/' + post.user_id" 
        class="username"
      >
        {{ displayUsername }}
      </router-link>
    </div>
    <img v-if="post.image_url" :src="post.image_url" alt="Post Image" class="post-image" />
    <div class="post-content">
      <div class="post-text">{{ post.title }}</div>
      <div class="post-description">{{ post.content }}</div>
      <div class="post-footer">
        <span class="post-timestamp">{{ formatDate(post.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MyPost',
  props: {
    post: {
      type: Object,
      required: true,
      validator: function (obj) {
        console.log('Post data:', obj); // Debug log
        return obj.id && obj.user_id !== undefined;
      },
    },
  },
  computed: {
    displayUsername() {
      console.log('Username:', this.post.username); // Debug log
      return this.post.username;
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  },
};
</script>

<style scoped>
.post {
  background-color: #fff;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 600px;
  margin: 0 auto 32px;
}

.post-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.post-image {
  width: 100%;
  display: block;
  object-fit: cover;
  max-height: 500px;
}

.post-content {
  padding: 20px;
}

.post-text {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 12px;
}

.post-description {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 16px;
  color: #333;
}

.post-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.username {
  font-size: 15px;
  font-weight: 600;
  color: #262626;
  text-decoration: none;
}

.username:hover {
  text-decoration: underline;
}

.post-timestamp {
  font-size: 14px;
  color: #666;
}
</style>