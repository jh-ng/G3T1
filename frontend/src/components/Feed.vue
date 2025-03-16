<template>
    <div class="feed">
      <div v-for="post in posts" :key="post.id" class="post-wrapper">
        <Post :post="post" />
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  import Post from '@/components/Post.vue'
  
  export default {
    name: 'MyFeed',
    components: {
      Post
    },
    setup() {
      const posts = ref([])
  
      const fetchPosts = async () => {
        try {
          // Replace this with your backend endpoint or use dummy data
          const response = await axios.get('/api/posts')
          posts.value = response.data.posts
        } catch (error) {
          console.error('Error fetching posts:', error)
          // For testing, you can set dummy posts:
          posts.value = [
            {
              id: 1,
              username: "john_doe",
              userAvatar: "https://via.placeholder.com/40",
              mediaUrl: "https://via.placeholder.com/500",
              caption: "Exploring the Eiffel Tower!"
            },
            {
              id: 2,
              username: "jane_smith",
              userAvatar: "https://via.placeholder.com/40",
              mediaUrl: "https://via.placeholder.com/500",
              caption: "Beautiful sunset in Bali."
            }
          ]
        }
      }
  
      onMounted(() => {
        fetchPosts()
      })
  
      return { posts }
    }
  }
  </script>
  
  <style scoped>
  .feed {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  /* .post-wrapper {
  } */
  </style>
  