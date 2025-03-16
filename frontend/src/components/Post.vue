<template>
    <div class="post">
      <div class="post-header">
        <img :src="post.userAvatar" alt="User Avatar" class="avatar" />
        <span class="username">{{ post.username }}</span>
      </div>
      <img :src="post.mediaUrl" alt="Post Image" class="post-image" />
      <div class="post-actions">
        <button @click="likePost">Like</button>
        <button @click="commentPost">Comment</button>
      </div>
      <div class="post-caption">
        <span class="username">{{ post.username }}</span>
        <span>{{ post.caption }}</span>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'MyPost',
    props: {
      post: {
        type: Object,
        required: true
      }
    },
    methods: {
      likePost() {
        // Implement like functionality
        console.log('Liked post', this.post.id)
      },
      commentPost() {
        // Implement comment functionality
        console.log('Comment on post', this.post.id)
      }
    }
  }
  </script>
  
  <style scoped>
  .post {
    border: 1px solid #e0e0e0;
    background-color: #fff;
    border-radius: 4px;
    overflow: hidden;
  }
  
  .post-header {
    display: flex;
    align-items: center;
    padding: 0.5rem;
  }
  
  .avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 0.5rem;
  }
  
  .post-image {
    width: 100%;
    display: block;
  }
  
  .post-actions {
    display: flex;
    gap: 1rem;
    padding: 0.5rem;
  }
  
  .post-caption {
    padding: 0.5rem;
  }
  
  .username {
    font-weight: bold;
    margin-right: 0.25rem;
  }
  </style>
  