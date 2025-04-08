<template>
  <div class="feed">
    <v-progress-circular
      v-if="loading"
      indeterminate
      color="primary"
      class="mx-auto d-block my-4"
    ></v-progress-circular>

    <v-alert
      v-if="error"
      type="error"
      class="mx-4"
    >
      {{ error }}
    </v-alert>

    <div v-if="!loading && !error">
      <div v-for="post in posts" :key="post.id" class="post-wrapper">
        <PostItem :post="post" @like-post="handleLike" @comment-post="handleComment" />
      </div>

      <v-alert
        v-if="posts.length === 0"
        type="info"
        class="mx-4"
      >
        No posts yet. Be the first to create one!
      </v-alert>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import PostItem from "@/components/Post.vue";
import authService from "@/services/auth";

export default {
  name: "MyFeed",
  components: {
    PostItem,
  },
  setup() {
    const posts = ref([]);
    const loading = ref(true);
    const error = ref(null);

    const fetchPosts = async () => {
      loading.value = true;
      error.value = null;

      try {
        const token = authService.getToken();
        if (!token) {
          throw new Error('Not authenticated');
        }

        const currentUser = authService.getCurrentUser();
        if (!currentUser) {
          throw new Error('User data not found');
        }

        const response = await fetch('http://localhost:8000/api/posts', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to fetch posts');
        }

        const data = await response.json();
        console.log('Posts data:', data.posts);
        posts.value = data.posts.map(post => ({
          ...post,
          username: post.username || currentUser.username
        }));
      } catch (err) {
        error.value = err.message;
        console.error("Error fetching posts:", err);
        if (err.message.includes('Not authenticated') || err.message.includes('User data not found')) {
          authService.logout();
        }
      } finally {
        loading.value = false;
      }
    };

    const handleLike = (postId) => {
      console.log('Liking post:', postId);
      // Implement like functionality
    };

    const handleComment = (postId) => {
      console.log('Commenting on post:', postId);
      // Implement comment functionality
    };

    onMounted(() => {
      fetchPosts();
    });

    return { 
      posts,
      loading,
      error,
      handleLike,
      handleComment
    };
  },
};
</script>

<style scoped>
.feed {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.post-wrapper {
  margin-bottom: 1rem;
}
</style>
