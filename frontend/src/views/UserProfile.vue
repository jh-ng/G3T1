<template>
  <div class="user-profile">
    <v-container>
      <v-row>
        <v-col cols="12" class="text-center">
          <h2 class="text-h4 mb-2">{{ username || `User ${userId}` }}</h2>
          <p class="text-subtitle-1">{{ posts.length }} {{ posts.length === 1 ? 'post' : 'posts' }}</p>
        </v-col>
      </v-row>

      <v-row v-if="loading">
        <v-col cols="12" class="text-center">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </v-col>
      </v-row>

      <v-row v-else-if="error">
        <v-col cols="12" class="text-center">
          <v-alert type="error">{{ error }}</v-alert>
        </v-col>
      </v-row>

      <v-row v-else-if="posts.length === 0">
        <v-col cols="12" class="text-center">
          <v-alert type="info">No posts yet</v-alert>
        </v-col>
      </v-row>

      <v-row v-else>
        <v-col cols="12" v-for="post in posts" :key="post.id">
          <post :post="post" @like-post="handleLike" @comment-post="handleComment" />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Post from '@/components/Post.vue';
import authService from '@/services/auth';
import defaultAvatar from '@/assets/opm.jpg';

export default {
  name: 'UserProfile',
  components: {
    Post
  },
  data() {
    return {
      userId: null,
      username: '',
      posts: [],
      loading: false,
      error: null,
      userAvatar: defaultAvatar
    };
  },
  created() {
    this.userId = this.$route.params.id;
    this.fetchUserPosts();
  },
  watch: {
    '$route.params.id': function(newId) {
      this.userId = newId;
      this.fetchUserPosts();
    }
  },
  methods: {
    async fetchUserPosts() {
      this.loading = true;
      this.error = null;
      
      try {
        const token = authService.getToken();
        if (!token) {
          this.$router.push('/login');
          return;
        }

        const response = await fetch(`http://localhost:8000/api/posts/user/${this.userId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch user posts');
        }

        const data = await response.json();
        this.posts = data.posts;
        this.username = data.username;

        // If viewing own profile, update avatar if available
        const currentUser = authService.getCurrentUser();
        if (currentUser && currentUser.id === parseInt(this.userId)) {
          this.userAvatar = currentUser.avatar || defaultAvatar;
        }
      } catch (err) {
        this.error = err.message;
        if (err.message.includes('token')) {
          this.$router.push('/login');
        }
      } finally {
        this.loading = false;
      }
    },
    handleLike(postId) {
      // Implement like functionality
      console.log('Liking post:', postId);
    },
    handleComment(postId) {
      // Implement comment functionality
      console.log('Commenting on post:', postId);
    }
  }
};
</script>

<style scoped>
.user-profile {
  padding: 2rem 0;
  max-width: 800px;
  margin: 0 auto;
}

.v-avatar {
  border: 3px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.post-grid {
  display: grid;
  gap: 2rem;
  padding: 2rem 0;
}
</style> 