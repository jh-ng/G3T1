<template>
    <div class="home">
      <!-- You can add a Navbar component here if needed -->
      <div class="content">
        <!-- For simplicity, we’ll render just the Feed component -->
        <Feed />
      </div>
    </div>
  </template>
  
  <script>
  import Feed from '@/components/Feed.vue'
  
  export default {
    name: 'MyHome',
    components: {
      Feed
    }
  }
  </script>
  
  <style scoped>
  .home {
    display: flex;
    flex-direction: column;
  }
  
  .content {
    display: flex;
    flex-direction: column;
    margin-top: 60px; /* Leave space for a Navbar if added */
  }
  </style>
  