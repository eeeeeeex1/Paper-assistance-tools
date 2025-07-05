// store/auth.ts
import { defineStore } from 'pinia';
import { getToken, setToken, removeToken } from '../utils/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken()
  }),
  actions: {
    login(token: string) {
      setToken(token);
      this.token = token;
    },
    logout() {
      removeToken();
      this.token = null;
    }
  }
});