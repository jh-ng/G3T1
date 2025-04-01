<template>
  <div class="home-container">
    <v-card class="mx-auto" max-width="800">
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="text-h5">Travel Posts</span>
        <v-btn
          color="primary"
          to="/create-post"
          v-if="isAuthenticated"
        >
          Create Post
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-progress-circular
          v-if="loading"
          indeterminate
          color="primary"
        ></v-progress-circular>

        <v-alert
          v-if="error"
          type="error"
        >
          {{ error }}
        </v-alert>

        <template v-if="!loading && !error">
          <v-list>
            <v-list-item
              v-for="post in posts"
              :key="post.id"
              class="mb-4"
            >
              <v-card width="100%">
                <v-card-title>{{ post.title }}</v-card-title>
                <v-card-text>{{ post.content }}</v-card-text>
                <v-card-actions>
                  <v-chip
                    size="small"
                    color="grey"
                    class="mr-2"
                  >
                    Posted by: {{ post.username }}
                  </v-chip>
                  <v-chip
                    size="small"
                    color="grey"
                  >
                    {{ formatDate(post.created_at) }}
                  </v-chip>
                </v-card-actions>
              </v-card>
            </v-list-item>
          </v-list>

          <v-alert
            v-if="posts.length === 0"
            type="info"
          >
            No posts yet. Be the first to create one!
          </v-alert>

          <div v-if="!isAuthenticated" class="text-center mt-4">
            <p class="text-body-2 mb-2">Want to create posts?</p>
            <v-btn
              color="primary"
              to="/login"
              class="mr-2"
            >
              Login
            </v-btn>
            <v-btn
              color="secondary"
              to="/register"
            >
              Register
            </v-btn>
          </div>
        </template>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import authService from '../services/auth';

export default {
  name: 'HomePage',
  data() {
    return {
      posts: [],
      loading: true,
      error: null,
      isAuthenticated: false
    };
  },
  async created() {
    this.isAuthenticated = authService.isAuthenticated();
    await this.fetchPosts();
  },
  methods: {
    async fetchPosts() {
      this.loading = true;
      this.error = null;

      try {
        const token = authService.getToken();
        if (!token) {
          this.$router.push('/login');
          return;
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
        this.posts = data.posts;

      } catch (err) {
        this.error = err.message;
        if (err.message.includes('token')) {
          this.$router.push('/login');
        }
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleString();
    }
  }
};
</script>

<style scoped>
.home-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}
</style>
  