// 工具函数 - 验证
import { formatDate } from './date'

// 验证手机号
export function validatePhone(phone: string): boolean {
  return /^1[3-9]\d{9}$/.test(phone)
}

// 验证邮箱
export function validateEmail(email: string): boolean {
  return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)
}

// 验证身份证
export function validateIdCard(idCard: string): boolean {
  return /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/.test(idCard)
}

// 验证必填
export function validateRequired(value: any): boolean {
  if (typeof value === 'string') {
    return value.trim() !== ''
  }
  return value !== null && value !== undefined
}

// 验证长度范围
export function validateLength(value: string, min: number, max: number): boolean {
  const len = value.length
  return len >= min && len <= max
}

// 验证表单
export interface ValidateRule {
  required?: boolean
  pattern?: RegExp
  minLength?: number
  maxLength?: number
  validator?: (value: any) => boolean
  message: string
}

export function validateField(value: any, rules: ValidateRule[]): string | null {
  for (const rule of rules) {
    if (rule.required && !validateRequired(value)) {
      return rule.message
    }

    if (rule.pattern && !rule.pattern.test(value)) {
      return rule.message
    }

    if (rule.minLength && value.length < rule.minLength) {
      return rule.message
    }

    if (rule.maxLength && value.length > rule.maxLength) {
      return rule.message
    }

    if (rule.validator && !rule.validator(value)) {
      return rule.message
    }
  }

  return null
}

// 验证登录表单
export function validateLoginForm(email: string, password: string): { valid: boolean; message: string } {
  if (!validateRequired(email)) {
    return { valid: false, message: '请输入邮箱' }
  }
  if (!validateEmail(email)) {
    return { valid: false, message: '邮箱格式不正确' }
  }
  if (!validateRequired(password)) {
    return { valid: false, message: '请输入密码' }
  }
  if (password.length < 6) {
    return { valid: false, message: '密码至少 6 位' }
  }
  return { valid: true, message: '' }
}

// 验证客户表单
export function validateCustomerForm(data: any): { valid: boolean; message: string } {
  if (!validateRequired(data.name)) {
    return { valid: false, message: '请输入客户姓名' }
  }
  if (data.phone && !validatePhone(data.phone)) {
    return { valid: false, message: '手机号格式不正确' }
  }
  if (data.idCard && !validateIdCard(data.idCard)) {
    return { valid: false, message: '身份证号格式不正确' }
  }
  return { valid: true, message: '' }
}
