import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref(localStorage.getItem('library_token') || '')
  const userInfo = ref(null)

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isAdminOrLibrarian = computed(() => 
    ['admin', 'librarian'].includes(userInfo.value?.role)
  )
  const roleLabel = computed(() => {
    const map = { admin: '管理员', librarian: '图书管理员', reader: '读者' }
    return map[userInfo.value?.role] || ''
  })

  // Actions
  async function login(credentials) {
    const res = await loginApi(credentials)
    token.value = res.access_token
    localStorage.setItem('library_token', res.access_token)
    await fetchUserInfo()
    return true
  }

  async function fetchUserInfo() {
    try {
      userInfo.value = await getUserInfo()
      return userInfo.value
    } catch {
      logout()
      return null
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('library_token')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    isAdminOrLibrarian,
    roleLabel,
    login,
    fetchUserInfo,
    logout
  }
})
