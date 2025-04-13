const app = Vue.createApp({
  data() {
    return {
      siteConfig: null,
      loading: true,
      error: null
    }
  },
  async mounted() {
    try {
      const response = await fetch('/api/v1/sites/config', {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      this.siteConfig = await response.json();
      console.log('站点配置:', this.siteConfig); 
      this.error = null;
    } catch (error) {
      console.error('获取站点配置失败:', error);
      this.error = error.message || '加载站点配置失败，请稍后重试';
    } finally {
      this.loading = false;
    }
  }
});

app.component('site-header', {
  props: ['config'],
  template: `
    <header class="site-header">
      <nav>
        <div class="logo">{{ config?.name || 'Alokai 商城' }}</div>
        <div class="nav-items">
          <a href="/">首页</a>
          <a href="/categories">分类</a>
          <a href="/cart">购物车</a>
          <a href="/wishlist">心愿单</a>
        </div>
      </nav>
    </header>
  `
});

app.component('home-view', {
  props: ['config'],
  template: `
    <div class="main-content">
      <div v-if="error" class="error-message" style="color: red; padding: 1rem;">
        {{ error }}
      </div>
      
      <div v-if="loading" class="loading" style="text-align: center; padding: 2rem;">
        <div style="font-size: 2rem; animation: pulse 1s infinite;">加载中...</div>
      </div>
      
      <template v-if="!loading && !error">
        <div class="carousel">
          <div v-for="banner in config.banners" :key="banner.id" class="banner">
            <img :src="banner.image" :alt="banner.title">
          </div>
        </div>
        
        <div class="featured-products">
          <h2>特色商品</h2>
          <div class="product-grid">
            <div v-for="product in config.featured_products" :key="product.id" class="product-card">
              <img :src="product.image" :alt="product.name">
              <h3>{{ product.name }}</h3>
              <p>{{ product.price }}</p>
            </div>
          </div>
        </div>
      </template>
    </div>
  `
});

app.mount('#app');
