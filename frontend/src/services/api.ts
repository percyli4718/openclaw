// API 服务层 - HTTP 请求封装
import { RequestConfig } from './types'

// 后端 API 基础 URL
// H5 开发模式使用相对路径（通过 Vite 代理转发）
// 小程序/APP 需要替换为完整 URL
const BASE_URL = typeof process !== 'undefined' && process.env?.VITE_API_BASE_URL
  ? process.env.VITE_API_BASE_URL
  : '/api'

// 通用响应结构 — 后端返回格式: { status: "success"|"error", data: {...}, ... }
export interface ApiResponse<T = any> {
  status: string
  data: T
  error?: string
  error_code?: string
  duration_ms?: number
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

  // 后端返回格式: { status: "success"|"error", data: {...}, error?: string }
  if (res.status === 'error') {
    const statusCode = response.statusCode
    if (statusCode === 401) {
      uni.removeStorageSync('token')
      uni.navigateTo({ url: '/src/pages/login/login' })
      throw new Error(res.error || '请先登录')
    }
    if (statusCode === 403) {
      throw new Error('无访问权限')
    }
    if (statusCode === 429) {
      throw new Error('请求过于频繁，请稍后重试')
    }
    throw new Error(res.error || res.error_code || '请求失败')
  }

  return res
}

// API 方法封装
export const api = {
  // ========== 认证相关 ==========
  login: (data: { username: string; password: string }) => {
    return request<ApiResponse<{ access_token: string; token_type: string; expires_in: number }>>({
      url: `${BASE_URL}/auth/token`,
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

  // ========== 内容生成相关 ==========
  generateWechatCopywriting: (data: {
    product_name: string
    product_type: string
    target_audience?: string
    tone?: string
    count?: number
  }) => {
    return request<ApiResponse<{ copies: any[]; review_results?: any[] }>>({
      url: `${BASE_URL}/content/generate`,
      method: 'POST',
      data
    })
  },

  generateVideoScript: (data: {
    topic: string
    duration?: number
    style?: string
  }) => {
    return request<ApiResponse<{ script: any }>>({
      url: `${BASE_URL}/content/video-script`,
      method: 'POST',
      data
    })
  },

  generatePoster: (data: {
    product_name: string
    selling_point: string
    cta?: string
  }) => {
    return request<ApiResponse<{ poster: { title: string; subtitle: string; cta: string } }>>({
      url: `${BASE_URL}/content/poster`,
      method: 'POST',
      data
    })
  },

  // ========== 客户分析相关 ==========
  analyzeCustomer: (data: {
    customer_id: string
    basic_info: Record<string, any>
  }) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/customer/analyze`,
      method: 'POST',
      data
    })
  },

  segmentCustomers: (data: {
    customer_ids: string[]
    profiles?: Record<string, any>
  }) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/customer/segment`,
      method: 'POST',
      data
    })
  },

  predictNeeds: (data: {
    customer_id: string
    profile: Record<string, any>
  }) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/customer/needs`,
      method: 'POST',
      data
    })
  },

  searchSimilarCustomers: (data: {
    customer_id: string
    limit?: number
  }) => {
    return request<ApiResponse<{ similar_customers: any[] }>>({
      url: `${BASE_URL}/customer/search-similar`,
      method: 'POST',
      data
    })
  },

  // ========== 跟进管理相关 ==========
  createFollowupPlan: (data: {
    customer_id: string
    plan_duration?: number
    frequency?: string
  }) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/followup/create`,
      method: 'POST',
      data
    })
  },

  scheduleMessage: (data: {
    customer_id: string
    message_content: string
    send_time: string
  }) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/followup/schedule`,
      method: 'POST',
      data
    })
  },

  logFollowup: (data: {
    customer_id: string
    followup_type: string
    content: string
    feedback?: string
  }) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/followup/log`,
      method: 'POST',
      data
    })
  },

  // ========== 合规审核相关 ==========
  reviewContent: (data: {
    content: string
    content_type?: string
    product_name?: string
  }) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/compliance/review`,
      method: 'POST',
      data
    })
  },

  getAuditLogs: (data?: {
    user_id?: string
    action?: string
    review_status?: string
    start_time?: string
    end_time?: string
    limit?: number
  }) => {
    return request<ApiResponse<{ logs: any[]; total: number }>>({
      url: `${BASE_URL}/compliance/audit-logs`,
      method: 'POST',
      data: data || {}
    })
  },

  listSensitiveWords: () => {
    return request<ApiResponse<{ words: string[]; total: number }>>({
      url: `${BASE_URL}/compliance/sensitive-words`,
      method: 'GET'
    })
  },

  addSensitiveWord: (word: string) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/compliance/sensitive-words/add`,
      method: 'POST',
      data: { word }
    })
  },

  removeSensitiveWord: (word: string) => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/compliance/sensitive-words/remove`,
      method: 'POST',
      data: { word }
    })
  },

  // ========== 健康检查 ==========
  healthCheck: () => {
    return request<ApiResponse<any>>({
      url: `${BASE_URL}/health`,
      method: 'GET'
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
