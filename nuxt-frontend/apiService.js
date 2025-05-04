// apiService.js

import { useFetch } from 'nuxt/app';

const apiService = {
  async get(url, options = {}) {
    return await useFetch(url, { ...options, method: 'GET' });
  },

  async post(url, options = {}) {
    return await useFetch(url, { ...options, method: 'POST' });
  },

  async put(url, options = {}) {
    return await useFetch(url, { ...options, method: 'PUT' });
  },

  async patch(url, options = {}) {
    return await useFetch(url, { ...options, method: 'PATCH' });
  },

  async delete(url, options = {}) {
    return await useFetch(url, { ...options, method: 'DELETE' });
  }
};

export default apiService;