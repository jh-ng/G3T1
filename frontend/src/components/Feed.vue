<template>
  <div class="feed">
    <div v-for="post in posts" :key="post.id" class="post-wrapper">
      <Post :post="post" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import axios from "axios";
import Post from "@/components/Post.vue";
import Paris from "@/assets/paris.jpg";
import Japan from "@/assets/japan.jpg";
import opm from "@/assets/opm.jpg";

export default {
  name: "MyFeed",
  components: {
    Post,
  },
  setup() {
    const posts = ref([]);

    const fetchPosts = async () => {
      try {
        // Replace this with your backend endpoint or use dummy data
        const response = await axios.get("http://localhost:5000");
        if (response.data.code === 200) {
          posts.value = response.data.data;
        } else {
          console.error("Error fetching posts:", response.data);
        }
      } catch (error) {
        console.error("Error fetching posts:", error);
        // For testing, you can set dummy posts:
        posts.value = [
          {
            id: 1,
            username: "john_doe",
            userAvatar: opm,
            mediaUrl: Paris,
            caption: "Exploring the Eiffel Tower!",
          },
          {
            id: 2,
            username: "jane_smith",
            userAvatar: opm,
            mediaUrl: Japan,
            caption: "Beautiful sunset in Bali.",
          },
        ];
      }
    };

    onMounted(() => {
      fetchPosts();
    });

    return { posts };
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
/* .post-wrapper {
  } */
</style>
