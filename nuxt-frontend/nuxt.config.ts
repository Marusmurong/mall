// https://nuxt.com/docs/api/configuration/nuxt-config
// @ts-nocheck
import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  devtools: { enabled: true },

  // @ts-ignore - Set server port to 3003
  app: {
    baseURL: '/',
    // Global head configuration
    head: {
      title: 'Multi-site E-commerce System',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { hid: 'description', name: 'description', content: 'Multi-site E-commerce System - Based on Nuxt 3 and Tailwind CSS' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  // Add static resource handling
  alias: {
    'images': '/assets/images',
    'styles': '/assets/styles',
    'fonts': '/assets/fonts',
  },

  // Vite configuration
  vite: {
    optimizeDeps: {
      exclude: ['fsevents']
    },
    // Add Watchman configuration
    server: {
      watch: {
        // Use Watchman (if available)
        usePolling: false,
        // @ts-ignore
        useFsEvents: true,
        // @ts-ignore
        alwaysStat: false,
        // Exclude some directories that don't need to be watched
        ignored: [
          '**/node_modules/**',
          '**/.git/**',
          '**/dist/**',
          '**/public/goods/images/**' // Exclude product image directory
        ]
      },
      // Reduce filesystem overhead
      fs: {
        strict: false
      }
    }
  },

  nitro: {
    // @ts-ignore
    devServer: {
      port: 3003,
      host: 'localhost'
    }
  },

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/i18n',
  ],

  runtimeConfig: {
    public: {
      apiBase: 'http://127.0.0.1:8000/api/v1',
      authBase: 'http://127.0.0.1:8000/api/v1/auth',
      currentSite: 'default'
    }
  },

  i18n: {
    locales: [
      {
        code: 'en',
        name: 'English',
        file: 'en.json'
      },
      {
        code: 'ja',
        name: '日本語',
        file: 'ja.json'
      },
      {
        code: 'ko',
        name: '한국어',
        file: 'ko.json'
      },
      {
        code: 'es',
        name: 'Español',
        file: 'es.json'
      }
    ],
    lazy: true,
    langDir: 'locales',
    defaultLocale: 'en',
    strategy: 'no_prefix',
  },

  tailwindcss: {
    cssPath: '~/assets/css/tailwind.css',
    configPath: '~/tailwind.config.js',
  },

  compatibilityDate: '2025-04-13'
})
