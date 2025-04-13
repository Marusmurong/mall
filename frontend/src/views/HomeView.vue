<template>
  <div class="home">
    <!-- 轮播图 -->
    <alokai-carousel
      :items="siteConfig.banners"
      :interval="5000"
      :autoplay="true"
    ></alokai-carousel>

    <!-- 特色商品 -->
    <alokai-featured-products
      :products="featuredProducts"
      :title="'特色商品'"
      :columns="4"
    ></alokai-featured-products>

    <!-- 分类导航 -->
    <alokai-category-grid
      :categories="categories"
      :title="'商品分类'"
    ></alokai-category-grid>

    <!-- 促销活动 -->
    <alokai-promotions
      :promotions="promotions"
      :title="'促销活动'"
    ></alokai-promotions>

    <!-- 站点公告 -->
    <alokai-announcement
      :message="siteConfig.announcement"
    ></alokai-announcement>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  computed: {
    siteConfig() {
      return this.$store.state.site.config
    },
    featuredProducts() {
      return this.siteConfig?.featured_products || []
    },
    categories() {
      return this.siteConfig?.categories || []
    },
    promotions() {
      return this.siteConfig?.promotions || []
    }
  }
}
</script>

<style scoped>
.home {
  padding: 20px;
}
</style>
