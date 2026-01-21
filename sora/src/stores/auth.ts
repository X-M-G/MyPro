import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'
// import router from '@/router' // Circular dependency avoidance

export const useAuthStore = defineStore('auth', () => {
    const user = ref<any>(null)
    const isAuthenticated = ref(false)
    const loading = ref(false)
    const error = ref<string | null>(null)
    const token = ref(localStorage.getItem('auth_token'))

    async function login(params: any) {
        loading.value = true
        error.value = null
        try {
            const response = await api.post('auth/login/', params)
            const { user: userData, token: userToken } = response.data
            user.value = userData
            token.value = userToken
            localStorage.setItem('auth_token', userToken)
            isAuthenticated.value = true
            return true
        } catch (e: any) {
            error.value = e.response?.data?.error || 'Login failed'
            return false
        } finally {
            loading.value = false
        }
    }

    async function register(params: any) {
        loading.value = true
        error.value = null
        try {
            await api.post('auth/register/', params)
            // Do not auto-login
            // const { user: userData, token: userToken } = response.data
            // user.value = userData
            // token.value = userToken
            // localStorage.setItem('auth_token', userToken)
            // isAuthenticated.value = true
            return true
        } catch (e: any) {
            error.value = e.response?.data?.error || 'Registration failed'
            return false
        } finally {
            loading.value = false
        }
    }

    async function fetchUser() {
        if (!token.value) return
        try {
            const response = await api.get('auth/me/')
            user.value = response.data
            isAuthenticated.value = true
        } catch (e) {
            // If fetch fails, we just ensure state is cleared.
            // Router guard will handle redirection.
            logout(false)
        }
    }

    async function logout(redirect = true) {
        try {
            // We don't necessarily need a backend call if we clear the token locally,
            // but for good measure we can send it.
            await api.post('auth/logout/')
        } catch (e) {
            // ignore
        } finally {
            user.value = null
            token.value = null
            localStorage.removeItem('auth_token')
            isAuthenticated.value = false
            isAuthenticated.value = false
            if (redirect) {
                window.location.href = '/' // Use window location to ensure full reset and avoid circular dep
            }
        }
    }

    async function fetchCreditHistory(page = 1, days = null) {
        try {
            let url = `auth/credits/history/?page=${page}`
            if (days) url += `&days=${days}`

            const response = await api.get(url)
            return response.data
        } catch (e) {
            console.error(e)
            return { results: [], count: 0 }
        }
    }

    return { user, isAuthenticated, loading, error, login, register, fetchUser, logout, fetchCreditHistory }
})
