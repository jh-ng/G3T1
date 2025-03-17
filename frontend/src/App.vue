<template>
  <v-app style="height: 100vh; width: 100vw">
    <v-app-bar color="primary">
      <v-app-bar-nav-icon
        variant="text"
        @click.stop="drawer = !drawer"
      ></v-app-bar-nav-icon>

      <v-toolbar-title>App name</v-toolbar-title>

      <v-spacer></v-spacer>

      <template v-if="$vuetify.display.mdAndUp">
        <v-btn icon="mdi-magnify" variant="text"></v-btn>

        <v-btn icon="mdi-filter" variant="text"></v-btn>
      </template>

      <v-btn icon="mdi-dots-vertical" variant="text"></v-btn>
    </v-app-bar>
    <v-navigation-drawer
      v-model="drawer"
      temporary
      style="height: 100vh; display: flex; flex-direction: column"
    >
      <v-list>
        <v-list-item to="/" title="Home"></v-list-item>
        <v-list-item to="/itinerary" title="itinerary planner"></v-list-item>
      </v-list>
      <v-divider></v-divider>
      <v-spacer></v-spacer>
      <div class="pa-4">
        <v-btn rounded block color="primary"> Create Post </v-btn>
      </div>
    </v-navigation-drawer>
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      drawer: false
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
