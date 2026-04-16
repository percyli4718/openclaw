// Pinia Store - 应用全局状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface UserInfo {
  id: string
  name: string
  email: string
  avatar?: string
  tenantId: string
}

interface AppState {
  userInfo: UserInfo | null
  token: string | null
  isLoggedIn: boolean
  loading: boolean
}

export const useAppStore = defineStore('app', () => {
  // State
  const userInfo = ref<UserInfo | null>(null)
  const token = ref<string | null>(null)
  const isLoggedIn = ref(false)
  const loading = ref(false)

  // Getters
  const userName = computed(() => userInfo.value?.name || '未登录')
  const userAvatar = computed(() => userInfo.value?.avatar || '')
  const tenantId = computed(() => userInfo.value?.tenantId || '')

  // Actions
  const init = async () => {
    console.log('App store initialized')
    // 从本地存储恢复状态
    try {
      const savedToken = uni.getStorageSync('token')
      const savedUser = uni.getStorageSync('userInfo')
      if (savedToken && savedUser) {
        token.value = savedToken
        userInfo.value = JSON.parse(savedUser)
        isLoggedIn.value = true
      }
    } catch (e) {
      console.error('Failed to restore session:', e)
    }
  }

  const checkAuth = async () => {
    // 验证 token 是否有效
    if (token.value) {
      try {
        // TODO: 调用后端验证 token
        // await api.validateToken(token.value)
        isLoggedIn.value = true
      } catch (e) {
        // Token 失效，清除登录状态
        await logout()
      }
    }
  }

  const resumeSession = async () => {
    // 恢复会话
    if (isLoggedIn.value && userInfo.value) {
      // 可以在此处刷新 session
    }
  }

  const saveState = () => {
    // 保存状态到本地存储
    if (token.value) {
      uni.setStorageSync('token', token.value)
    }
    if (userInfo.value) {
      uni.setStorageSync('userInfo', JSON.stringify(userInfo.value))
    }
  }

  const login = async (email: string, password: string) => {
    loading.value = true
    try {
      // TODO: 调用后端登录 API
      // const res = await api.login({ email, password })
      // token.value = res.token
      // userInfo.value = res.user
      // isLoggedIn.value = true
      // saveState()

      // Mock 登录
      token.value = 'mock-token-' + Date.now()
      userInfo.value = {
        id: '1',
        name: '测试用户',
        email: email,
        tenantId: 'tenant-1'
      }
      isLoggedIn.value = true
      saveState()
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      // TODO: 调用后端登出 API
      // await api.logout()
    } catch (e) {
      console.error('Logout failed:', e)
    } finally {
      // 清除本地状态
      token.value = null
      userInfo.value = null
      isLoggedIn.value = false
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
    }
  }

  const updateUserInfo = (info: Partial<UserInfo>) => {
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...info }
      saveState()
    }
  }

  return {
    // State
    userInfo,
    token,
    isLoggedIn,
    loading,
    // Getters
    userName,
    userAvatar,
    tenantId,
    // Actions
    init,
    checkAuth,
    resumeSession,
    saveState,
    login,
    logout,
    updateUserInfo
  }
})
