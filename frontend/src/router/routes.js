import Home from '../views/HomeView.vue'
import Product from '../views/ProductView.vue'
import Category from '../views/CategoryView.vue'
import Cart from '../views/CartView.vue'
import Wishlist from '../views/WishlistView.vue'

export default [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/category/:slug',
    name: 'category',
    component: Category
  },
  {
    path: '/product/:id',
    name: 'product',
    component: Product
  },
  {
    path: '/cart',
    name: 'cart',
    component: Cart
  },
  {
    path: '/wishlist',
    name: 'wishlist',
    component: Wishlist
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue')
  }
]
