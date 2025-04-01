<template>
  <div class="post">
    <div class="post-header">
      <img :src="post.userAvatar" alt="User Avatar" class="avatar" />
      <span class="username">{{ post.username }}</span>
    </div>
    <img :src="post.mediaUrl" alt="Post Image" class="post-image" />
    <div class="post-actions">
      <button @click="likePost" class="action-button">
        <v-icon v-if="post.isLiked" color="red">mdi-heart</v-icon>
        <v-icon v-else>mdi-heart-outline</v-icon>
        <span v-if="post.likeCount" class="count">{{ post.likeCount }}</span>
      </button>
      <button @click="commentPost" class="action-button">
        <v-icon>mdi-comment-outline</v-icon>
        <span v-if="post.commentCount" class="count">{{ post.commentCount }}</span>
      </button>
      <button class="action-button">
        <v-icon>mdi-share-variant-outline</v-icon>
      </button>
      <v-spacer></v-spacer>
      <button class="action-button">
        <v-icon>mdi-bookmark-outline</v-icon>
      </button>
    </div>
    <div class="post-likes" v-if="post.likeCount">
      <span>{{ post.likeCount }} likes</span>
    </div>
    <div class="post-caption">
      <span class="username">{{ post.username }}</span>
      <span>{{ post.caption }}</span>
    </div>
  </div>
</template>

<script>
import opm from '@/assets/opm.jpg'; // Import for test avatar

export default {
  name: 'MyPost',
  props: {
    post: {
      type: Object,
      required: true,
      validator: function (obj) {
        return obj.post_id && obj.user_id !== undefined;
      },
    },
  },
  data() {
    return {
      username: 'User', // Replace with a method to get the username.
      userAvatar: opm, // Replace with a method to get the user avatar.
    };
  },
  methods: {
    likePost() {
      this.$emit('like-post', this.post.post_id);
      console.log('Liked post', this.post.post_id);
    },
    commentPost() {
      this.$emit('comment-post', this.post.post_id);
      console.log('Comment on post', this.post.post_id);
    },
  },
};
</script>

<style scoped>
.post {
  border: 1px solid #dbdbdb;
  background-color: #fff;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  width: calc(50% - 12px); /* Take up half the width minus some margin */
  display: inline-block;
  vertical-align: top;
  margin-right: 12px;
  margin-left: 12px;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .post {
    width: 100%; /* On smaller screens, posts take full width */
    margin-right: 0;
    margin-left: 0;
  }
}

.post-header {
  display: flex;
  align-items: center;
  padding: 12px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 10px;
  object-fit: cover;
}

.post-image {
  width: 100%;
  display: block;
  object-fit: cover;
  height: 300px; /* Fixed height for consistent layout */
}

.post-actions {
  display: flex;
  padding: 8px 12px;
  align-items: center;
}

.action-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  margin-right: 16px;
  display: flex;
  align-items: center;
  font-size: 14px;
}

.count {
  margin-left: 4px;
}

.post-likes {
  font-weight: 600;
  padding: 0 12px;
  font-size: 14px;
}

.post-caption {
  padding: 12px;
  font-size: 14px;
  line-height: 1.4;
  /* Add truncation for long captions */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.username {
  font-weight: 600;
  margin-right: 4px;
}
</style>