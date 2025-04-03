<template>
  <div class="create-post-container">
    <v-card class="mx-auto" max-width="800">
      <v-card-title class="text-h5 mb-4">Create New Post</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="handleSubmit" enctype="multipart/form-data">
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

          <v-file-input
            v-model="image"
            label="Upload Image"
            accept="image/*"
            prepend-icon="mdi-camera"
            class="mb-4"
          ></v-file-input>

          <v-img
            v-if="imagePreview"
            :src="imagePreview"
            max-height="200"
            contain
            class="mb-4"
          ></v-img>

          <v-btn
            color="primary"
            type="submit"
            :loading="loading"
            :disabled="loading"
            block
            class="mb-2"
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
      image: null,
      imagePreview: null,
      loading: false,
      error: null,
      success: false
    };
  },
  watch: {
    image(file) {
      if (file) {
        const reader = new FileReader();
        reader.onload = e => {
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      } else {
        this.imagePreview = null;
      }
    }
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

        // Create FormData object
        const formData = new FormData();
        formData.append('title', this.title);
        formData.append('content', this.content);
        if (this.image) {
          formData.append('image', this.image);
        }

        const response = await fetch('http://localhost:8000/api/posts', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
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
        this.image = null;
        this.imagePreview = null;
        
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