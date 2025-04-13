<template>
  <div id="app">
    <site-header v-if="siteConfig" :config="siteConfig" />
    <router-view v-if="siteConfig" :site-config="siteConfig" />
    <site-footer v-if="siteConfig" :config="siteConfig" />
  </div>
</template>

<script>
import SiteHeader from './components/SiteHeader.vue'
import SiteFooter from './components/SiteFooter.vue'

export default {
  name: 'App',
  components: {
    SiteHeader,
    SiteFooter
  },
  computed: {
    siteConfig() {
      return this.$store.state.site.config
    }
  }
}
</script>

<style>
@import url('https://cdn.alokai.com/styles/alokai-core.css');
@import url('https://cdn.alokai.com/styles/themes/default.css');

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
