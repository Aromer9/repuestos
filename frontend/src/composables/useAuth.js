import { ref, computed } from 'vue'

const TOKEN_KEY = 'argparts_token'
const USER_KEY = 'argparts_user'

const token = ref(localStorage.getItem(TOKEN_KEY) || null)
const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))
const loading = ref(false)
const error = ref(null)

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const login = async (username, password) => {
    loading.value = true
    error.value = null
    try {
      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)

      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form,
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || 'Credenciales incorrectas')
      }

      const data = await res.json()
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem(TOKEN_KEY, data.access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(data.user))
      return true
    } catch (e) {
      error.value = e.message
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  const authFetch = async (url, options = {}) => {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token.value}`,
        ...options.headers,
      },
    })
    if (res.status === 401) {
      logout()
      window.location.href = '/admin/login'
      return null
    }
    return res
  }

  return { token, user, loading, error, isAuthenticated, isAdmin, login, logout, authFetch }
}
