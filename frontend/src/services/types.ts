// HTTP 请求类型定义

export interface RequestConfig {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'UPLOAD' | 'DOWNLOAD'
  data?: any
  params?: any
  header?: Record<string, string>
  timeout?: number
  dataType?: string
  responseType?: 'text' | 'arraybuffer'
  validateStatus?: (status: number) => boolean
}

export interface UploadFileConfig {
  url: string
  name: string
  filePath: string
  formData?: Record<string, any>
  header?: Record<string, string>
}

export interface DownloadFileConfig {
  url: string
  filePath?: string
  header?: Record<string, string>
}

// 通用 API 响应
export interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
  timestamp?: number
}

// 分页参数
export interface PageParams {
  page: number
  pageSize: number
}

// 分页响应
export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}
