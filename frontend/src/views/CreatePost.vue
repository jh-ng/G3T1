<template>
  <div class="create-post-container">
    <v-card class="mx-auto" max-width="800">
      <v-card-title class="text-h5 mb-4">Create New Post</v-card-title>
      <v-card-text>
        <v-form
          ref="postForm"
          @submit.prevent="handleSubmit"
          enctype="multipart/form-data"
        >
          <v-text-field
            v-model="title"
            label="Title"
            :rules="[(v) => !!v || 'Title is required']"
            required
            class="mb-4"
          ></v-text-field>

          <v-textarea
            v-model="content"
            label="Content"
            :rules="[(v) => !!v || 'Content is required']"
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
          <v-select
            v-model="selectedPreferences"
            :items="preferences"
            label="Select Tags"
            multiple
            chips
            clearable
            class="mb-4"
          />
          <v-text-field
            v-model="location"
            label="Location"
            placeholder="e.g., Tokyo, Japan"
            class="mb-4"
          />
          <v-btn
            color="primary"
            type="submit"
            :loading="loading"
            :disabled="loading"
            block
            class="mb-2"
          >
            {{ loading ? "Creating Post..." : "Create Post" }}
          </v-btn>

          <v-alert v-if="error" type="error" class="mt-4">
            {{ error }}
          </v-alert>

          <v-alert v-if="success" type="success" class="mt-4">
            Post created successfully!
          </v-alert>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import authService from "../services/auth";

export default {
  name: "CreatePost",
  data() {
    return {
      title: "",
      content: "",
      image: null,
      imagePreview: null,
      loading: false,
      error: null,
      success: false,
      preferences: [],
      selectedPreferences: [],
      location: "",
    };
  },
  created() {
    this.fetchPreferences();
  },
  watch: {
    image(file) {
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      } else {
        this.imagePreview = null;
      }
    },
  },
  methods: {
    async fetchPreferences() {
      try {
        const token = authService.getToken();
        if (!token) {
          this.$router.push("/login");
          return;
        }

        const response = await fetch(`http://localhost:5005/api/user/taste-preferences`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch preferences");
        }

        const data = await response.json();
        const tastePreferences = data.taste_preferences || {};
        // Collect all array values from the taste_preferences object and flatten them
        this.preferences = [];
        for (const key in tastePreferences) {
          if (key === 'startTime' || key === 'endTime') {
            continue; // Skip 'startTime' and 'endTime'
          }
          const value = tastePreferences[key];
          if (Array.isArray(value)) {
            this.preferences = this.preferences.concat(value);
          } else if (typeof value === 'string') {
            this.preferences.push(value);
          }
        }
      } catch (err) {
        console.error("Failed to load preferences:", err.message);
        this.preferences = []; // fallback to empty list
      }
    },

    async handleSubmit() {
      this.loading = true;
      this.error = null;
      this.success = false;

      try {
        const token = authService.getToken();
        if (!token) {
          this.$router.push("/login");
          return;
        }

        // Create FormData object
        const formData = new FormData();
        formData.append("title", this.title);
        formData.append("content", this.content);
        formData.append(
          "selected_preferences",
          this.selectedPreferences.join(",")
        );
        formData.append('location', this.location);
        if (this.image) {
          formData.append("image", this.image);
        }

        const response = await fetch("http://localhost:5005/api/posts", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Failed to create post");
        }

        this.success = true;

        // Clear form
        this.title = "";
        this.content = "";
        this.image = null;
        this.imagePreview = null;

        this.$nextTick(() => {
          this.$refs.postForm.resetValidation();
        });

        // Redirect to home page after a short delay
        setTimeout(() => {
          this.$router.push("/");
        }, 500);
      } catch (err) {
        this.error = err.message;
        if (err.message.includes("token")) {
          // If token is invalid, redirect to login
          this.$router.push("/login");
        }
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.create-post-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}
</style>
