// 工具函数 - 日期格式化
export function formatDate(date: Date | string | number, format?: string): string {
  const d = new Date(date)

  const year = d.getFullYear()
  const month = (d.getMonth() + 1).toString().padStart(2, '0')
  const day = d.getDate().toString().padStart(2, '0')
  const hours = d.getHours().toString().padStart(2, '0')
  const minutes = d.getMinutes().toString().padStart(2, '0')
  const seconds = d.getSeconds().toString().padStart(2, '0')

  if (!format) {
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  return format
    .replace('YYYY', year.toString())
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

// 相对时间格式化
export function formatRelativeTime(date: Date | string | number): string {
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()

  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day
  const month = 30 * day

  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    return `${Math.floor(diff / minute)}分钟前`
  } else if (diff < day) {
    return `${Math.floor(diff / hour)}小时前`
  } else if (diff < week) {
    return `${Math.floor(diff / day)}天前`
  } else if (diff < month) {
    return `${Math.floor(diff / week)}周前`
  } else {
    return formatDate(d, 'MM-DD')
  }
}

// 未来时间格式化（用于跟进提醒）
export function formatFutureTime(date: Date | string | number): string {
  const d = new Date(date)
  const now = new Date()
  const diff = d.getTime() - now.getTime()

  const day = 24 * 60 * 60 * 1000

  if (diff < 0) {
    return '已逾期'
  } else if (diff < day) {
    return '今日'
  } else if (diff < 2 * day) {
    return '明天'
  } else if (diff < 7 * day) {
    return `${Math.floor(diff / day)}天后`
  } else {
    return formatDate(d, 'MM-DD')
  }
}

// 格式化跟进时间
export function formatFollowupTime(date: Date | string | number): string {
  const d = new Date(date)
  const hours = d.getHours().toString().padStart(2, '0')
  const minutes = d.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}
