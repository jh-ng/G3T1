<template>
  <div class="feed">
    <v-progress-circular
      v-if="loading"
      indeterminate
      color="primary"
      class="mx-auto d-block my-4"
    ></v-progress-circular>

    <v-alert v-if="error" type="error" class="mx-4">
      {{ error }}
    </v-alert>

    <div v-if="!loading && !error">
      <v-container class="px-4 pt-4">
        <v-row align="center" justify="space-between">
          <v-col cols="12" md="8">
            <v-select
              v-model="selectedTags"
              :items="availableTags"
              label="Filter by tags"
              multiple
              chips
              clearable
            ></v-select>
          </v-col>
          <v-col cols="12" md="4" class="d-flex justify-end">
            <v-btn color="primary" @click="applyFilters"> Filter </v-btn>
            <v-btn
              color="secondary"
              @click="removeAllFilters"
              style="margin-left: 16px"
              >Reset</v-btn
            >
          </v-col>
        </v-row>
      </v-container>

      <div v-for="post in posts" :key="post.id" class="post-wrapper">
        <PostItem
          :post="post"
          @like-post="handleLike"
          @comment-post="handleComment"
          @tag-clicked="handleTagClick"
        />
      </div>

      <v-alert v-if="posts.length === 0" type="info" class="mx-4">
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
    const selectedTags = ref([]);
    const availableTags = [
      "Active",
      "Cultural",
      "Family",
      "Shopping",
      "Solo",
      "Nature Sites",
      "Cultural Sites",
      "Leisure Attractions",
      "Sports Activities",
      "Halal",
      "Vegetarian",
      "Kosher",
      "None",
      // Add more if needed
    ];

    const fetchPosts = async () => {
      loading.value = true;
      error.value = null;

      try {
        const token = authService.getToken();
        if (!token) {
          throw new Error("Not authenticated");
        }

        const currentUser = authService.getCurrentUser();
        if (!currentUser) {
          throw new Error("User data not found");
        }

        const query =
          selectedTags.value.length > 0
            ? `?tags=${selectedTags.value.join(",")}`
            : "";

        const response = await fetch(
          `http://localhost:8000/api/posts${query}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Failed to fetch posts");
        }

        const data = await response.json();
        console.log("Posts data:", data.posts);
        posts.value = data.posts.map((post) => ({
          ...post,
          username: post.username || currentUser.username,
          tags: post.preference || [],
        }));
      } catch (err) {
        error.value = err.message;
        console.error("Error fetching posts:", err);
        if (
          err.message.includes("Not authenticated") ||
          err.message.includes("User data not found")
        ) {
          authService.logout();
        }
      } finally {
        loading.value = false;
      }
    };

    const applyFilters = () => {
      fetchPosts(selectedTags.value);
    };

    const removeAllFilters = () => {
      selectedTags.value = [];
      fetchPosts();
    };

    const handleTagClick = (tag) => {
      if (!selectedTags.value.includes(tag)) {
        selectedTags.value.push(tag);
        fetchPosts();
      }
    };

    onMounted(() => {
      fetchPosts();
    });

    return {
      posts,
      loading,
      error,
      selectedTags,
      availableTags,
      applyFilters,
      removeAllFilters,
      handleTagClick
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
