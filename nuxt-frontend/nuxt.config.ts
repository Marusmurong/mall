// https://nuxt.com/docs/api/configuration/nuxt-config
// @ts-nocheck
import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  devtools: { enabled: true },

  // 全局配置
  app: {
    baseURL: '/',
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

  // 实验性功能设置
  experimental: {
    appManifest: false, // 禁用 appManifest 解决无法找到 #app-manifest 的问题
  },

  // 基本模块
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/i18n',
  ],

  // 静态资源别名
  alias: {
    'images': '/assets/images',
    'styles': '/assets/styles',
    'fonts': '/assets/fonts',
  },

  // 运行时配置
  runtimeConfig: {
    // 仅服务器端的私有密钥
    apiSecret: process.env.NUXT_API_SECRET || 'default_secret',
    
    // 同时在客户端和服务器端可用的公共密钥
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
      debug: process.env.NODE_ENV !== 'production'
    }
  },

  // i18n配置
  i18n: {
    locales: [
      { code: 'en', name: 'English', file: 'en.json' },
      { code: 'ja', name: '日本語', file: 'ja.json' },
      { code: 'ko', name: '한국어', file: 'ko.json' },
      { code: 'es', name: 'Español', file: 'es.json' }
    ],
    lazy: true,
    langDir: 'locales',
    defaultLocale: 'en',
    strategy: 'no_prefix',
  },

  // Tailwind配置
  tailwindcss: {
    cssPath: '~/assets/css/tailwind.css',
    configPath: '~/tailwind.config.js',
  },

  // 明确设置开发服务器端口
  devServer: {
    port: 3003,
    host: '0.0.0.0'
  },

  // 配置Nitro，启用API代理
  nitro: {
    esbuild: {
      options: { target: 'es2020' }
    },
    sourcemap: true,
    compatibilityDate: '2025-05-03',
    // 简化API代理配置
    devProxy: {
      '/api/v1': {
        target: 'http://localhost:8000/api/v1',
        changeOrigin: true,
        prependPath: false
      }
    }
  },
})
