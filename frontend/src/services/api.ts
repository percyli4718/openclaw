// API 服务层 - HTTP 请求封装
import { RequestConfig } from './request'

// 后端 API 基础 URL
const BASE_URL = '/api'

// 通用响应结构
export interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

// 请求拦截器
const requestInterceptor = (config: RequestConfig) => {
  // 添加 token
  const token = uni.getStorageSync('token')
  if (token) {
    config.header = {
      ...config.header,
      'Authorization': `Bearer ${token}`
    }
  }

  // 添加租户 ID
  const tenantId = uni.getStorageSync('tenantId')
  if (tenantId) {
    config.header = {
      ...config.header,
      'X-Tenant-ID': tenantId
    }
  }

  return config
}

// 响应拦截器
const responseInterceptor = <T>(response: any): ApiResponse<T> => {
  const res = response.data

  // 统一处理错误码
  if (res.code !== 200) {
    // 401: 未授权
    if (res.code === 401) {
      uni.removeStorageSync('token')
      uni.navigateTo({ url: '/src/pages/login/login' })
      throw new Error('请先登录')
    }

    // 403: 无权限
    if (res.code === 403) {
      throw new Error('无访问权限')
    }

    // 500: 服务器错误
    if (res.code >= 500) {
      throw new Error('服务器错误，请稍后重试')
    }

    throw new Error(res.message || '请求失败')
  }

  return res
}

// API 方法封装
export const api = {
  // ========== 认证相关 ==========
  login: (data: { email: string; password: string }) => {
    return request<ApiResponse<{ token: string; user: any }>>({
      url: `${BASE_URL}/auth/login`,
      method: 'POST',
      data
    })
  },

  logout: () => {
    return request<ApiResponse>({
      url: `${BASE_URL}/auth/logout`,
      method: 'POST'
    })
  },

  refreshToken: () => {
    return request<ApiResponse<{ token: string }>>({
      url: `${BASE_URL}/auth/refresh`,
      method: 'POST'
    })
  },

  // ========== 内容生成相关 ==========
  generateWechatCopywriting: (data: {
    productName: string
    productType: string
    targetAudience?: string
    tone?: string
    count?: number
  }) => {
    return request<ApiResponse<{ copies: any[] }>>({
      url: `${BASE_URL}/content/generate-wechat`,
      method: 'POST',
      data
    })
  },

  generateVideoScript: (data: {
    topic: string
    duration?: string
    style?: string
  }) => {
    return request<ApiResponse<{ scripts: any[] }>>({
      url: `${BASE_URL}/content/generate-video`,
      method: 'POST',
      data
    })
  },

  generatePosterCopywriting: (data: {
    productName: string
    theme?: string
  }) => {
    return request<ApiResponse<{ copies: any[] }>>({
      url: `${BASE_URL}/content/generate-poster`,
      method: 'POST',
      data
    })
  },

  getSalesScriptTemplates: (params?: {
    type?: string
    page?: number
    pageSize?: number
  }) => {
    return request<ApiResponse<PaginatedResponse<any>>>({
      url: `${BASE_URL}/content/templates`,
      method: 'GET',
      params
    })
  },

  // ========== 客户管理相关 ==========
  getCustomers: (params?: {
    level?: string
    source?: string
    searchText?: string
    page?: number
    pageSize?: number
  }) => {
    return request<ApiResponse<PaginatedResponse<any>>>({
      url: `${BASE_URL}/customers`,
      method: 'GET',
      params
    })
  },

  getCustomerDetail: (id: string) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/customers/${id}`,
      method: 'GET'
    })
  },

  addCustomer: (data: any) => {
    return request<ApiResponse<{ id: string }>>({
      url: `${BASE_URL}/customers`,
      method: 'POST',
      data
    })
  },

  updateCustomer: (id: string, data: any) => {
    return request<ApiResponse>({
      url: `${BASE_URL}/customers/${id}`,
      method: 'PUT',
      data
    })
  },

  deleteCustomer: (id: string) => {
    return request<ApiResponse>({
      url: `${BASE_URL}/customers/${id}`,
      method: 'DELETE'
    })
  },

  importCustomers: (file: any) => {
    return request<ApiResponse<{ count: number }>>({
      url: `${BASE_URL}/customers/import`,
      method: 'POST',
      data: file,
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  analyzeCustomers: (ids?: string[]) => {
    return request<ApiResponse<{ insights: string[] }>>({
      url: `${BASE_URL}/customers/analyze`,
      method: 'POST',
      data: { ids }
    })
  },

  // ========== 跟进管理相关 ==========
  getFollowupPlans: (params?: {
    status?: string
    page?: number
    pageSize?: number
  }) => {
    return request<ApiResponse<PaginatedResponse<any>>>({
      url: `${BASE_URL}/followup/plans`,
      method: 'GET',
      params
    })
  },

  createFollowupPlan: (data: {
    customerId: string
    tasks: Array<{
      type: string
      content: string
      scheduledAt: string
    }>
  }) => {
    return request<ApiResponse<{ id: string }>>({
      url: `${BASE_URL}/followup/plans`,
      method: 'POST',
      data
    })
  },

  generateFollowupPlan: (customerId: string) => {
    return request<ApiResponse<{ tasks: any[] }>>({
      url: `${BASE_URL}/followup/generate`,
      method: 'POST',
      data: { customerId }
    })
  },

  completeTask: (taskId: string, data: { result?: string }) => {
    return request<ApiResponse>({
      url: `${BASE_URL}/followup/tasks/${taskId}/complete`,
      method: 'POST',
      data
    })
  },

  scheduleMessage: (data: {
    customerId: string
    content: string
    scheduledAt: string
  }) => {
    return request<ApiResponse>({
      url: `${BASE_URL}/followup/schedule`,
      method: 'POST',
      data
    })
  },

  getTodayTasks: () => {
    return request<ApiResponse<any[]>>({
      url: `${BASE_URL}/followup/today`,
      method: 'GET'
    })
  },

  // ========== 数据分析相关 ==========
  getDashboard: () => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/dashboard`,
      method: 'GET'
    })
  },

  getContentStats: (params?: {
    startDate?: string
    endDate?: string
  }) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/stats/content`,
      method: 'GET',
      params
    })
  },

  getCustomerStats: (params?: {
    startDate?: string
    endDate?: string
  }) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/stats/customer`,
      method: 'GET',
      params
    })
  },

  getFollowupStats: (params?: {
    startDate?: string
    endDate?: string
  }) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/stats/followup`,
      method: 'GET',
      params
    })
  }
}

// 封装 uni.request
function request<T>(config: RequestConfig): Promise<T> {
  // 应用拦截器
  config = requestInterceptor(config)

  return new Promise((resolve, reject) => {
    uni.request({
      ...config,
      success: (res) => {
        try {
          const data = responseInterceptor<T>(res)
          resolve(data)
        } catch (error) {
          reject(error)
        }
      },
      fail: (err) => {
        // 网络错误
        if (err.errMsg.includes('timeout')) {
          reject(new Error('请求超时，请检查网络连接'))
        } else if (err.errMsg.includes('fail')) {
          reject(new Error('网络错误，请稍后重试'))
        } else {
          reject(err)
        }
      }
    })
  })
}

export default api
