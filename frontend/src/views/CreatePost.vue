<template>
  <div class="create-post-container">
    <v-card class="mx-auto" max-width="800">
      <v-card-title class="text-h5 mb-4">Create New Post</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="handleSubmit">
          <v-text-field
            v-model="title"
            label="Title"
            :rules="[v => !!v || 'Title is required']"
            required
            class="mb-4"
          ></v-text-field>

          <v-textarea
            v-model="content"
            label="Content"
            :rules="[v => !!v || 'Content is required']"
            required
            rows="6"
            class="mb-4"
          ></v-textarea>

          <v-btn
            color="primary"
            type="submit"
            :loading="loading"
            :disabled="loading"
            block
          >
            {{ loading ? 'Creating Post...' : 'Create Post' }}
          </v-btn>

          <v-alert
            v-if="error"
            type="error"
            class="mt-4"
          >
            {{ error }}
          </v-alert>

          <v-alert
            v-if="success"
            type="success"
            class="mt-4"
          >
            Post created successfully!
          </v-alert>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import authService from '../services/auth';

export default {
  name: 'CreatePost',
  data() {
    return {
      title: '',
      content: '',
      loading: false,
      error: null,
      success: false
    };
  },
  methods: {
    async handleSubmit() {
      this.loading = true;
      this.error = null;
      this.success = false;

      try {
        const token = authService.getToken();
        if (!token) {
          this.$router.push('/login');
          return;
        }

        const response = await fetch('http://localhost:8000/api/posts', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            title: this.title,
            content: this.content
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to create post');
        }

        await response.json();
        this.success = true;
        
        // Clear form
        this.title = '';
        this.content = '';
        
        // Redirect to home page after a short delay
        setTimeout(() => {
          this.$router.push('/');
        }, 1500);

      } catch (err) {
        this.error = err.message;
        if (err.message.includes('token')) {
          // If token is invalid, redirect to login
          this.$router.push('/login');
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.create-post-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}
</style> 