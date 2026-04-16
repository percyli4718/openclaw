// Pinia Store - 内容生成状态管理
import { defineStore } from 'pinia'
import { ref } from 'vue'

interface Copywriting {
  id: string
  content: string
  hashtags: string[]
  score: number
  type: 'wechat' | 'video' | 'poster'
  createdAt: string
}

interface ContentGenState {
  copies: Copywriting[]
  generating: boolean
  state: 'idle' | 'loading' | 'success' | 'error' | 'partial'
  errorMessage: string | null
  partialItems: Array<{ name: string; success: boolean }>
}

export const useContentGenStore = defineStore('contentGen', () => {
  // State
  const copies = ref<Copywriting[]>([])
  const generating = ref(false)
  const state = ref<ContentGenState['state']>('idle')
  const errorMessage = ref<string | null>(null)
  const partialItems = ref<Array<{ name: string; success: boolean }>>([])

  // Actions
  const generateWechatCopywriting = async (params: {
    productName: string
    productType: string
    targetAudience?: string
    tone?: string
    count?: number
  }) => {
    generating.value = true
    state.value = 'loading'
    errorMessage.value = null

    try {
      // TODO: 调用后端 API
      // const res = await api.generateWechatCopywriting(params)
      // copies.value = res.data.copies
      // state.value = 'success'

      // Mock 生成
      await new Promise(resolve => setTimeout(resolve, 2000))

      copies.value = [
        {
          id: '1',
          content: `【${params.productName}】为您保驾护航！\n\n人生路上，风险难料。一份${params.productType}，给自己和家人最坚实的依靠。\n\n✅ 保障全面：覆盖 100+ 种重疾\n✅ 赔付灵活：可选多次赔付\n✅ 保费亲民：每天只需几块钱\n\n私信我，免费获取专属方案！`,
          hashtags: ['#保险规划', '#重疾险', '#家庭保障'],
          score: 0.92,
          type: 'wechat',
          createdAt: new Date().toISOString()
        },
        {
          id: '2',
          content: `30 岁后，这件事比买房更重要！🏠\n\n不是股票，不是基金\n而是一份能兜底的健康保障\n\n${params.productName}${params.productType}\n用少量杠杆，撬动百万保障\n\n⏰ 限时福利：前 10 名咨询免体检\n👇 扫码预约专业顾问`,
          hashtags: ['#保险科普', '#健康管理', '#${params.productType}'],
          score: 0.88,
          type: 'wechat',
          createdAt: new Date().toISOString()
        },
        {
          id: '3',
          content: `客户问我：${params.productType}真的有必要买吗？\n\n我的回答：\n❌ 不买，生病时自费 50 万\n✅ 买了，确诊即赔 50 万\n\n区别在于：\n一个动用存款，一个保险公司买单\n\n${params.productName}，让保障更简单`,
          hashtags: ['#保险问答', '#${params.productType}', '#保障规划'],
          score: 0.85,
          type: 'wechat',
          createdAt: new Date().toISOString()
        }
      ]
      state.value = 'success'
    } catch (error) {
      state.value = 'error'
      errorMessage.value = '生成失败，请重试'
      console.error('Generate failed:', error)
    } finally {
      generating.value = false
    }
  }

  const generateVideoScript = async (params: {
    topic: string
    duration?: '15s' | '30s' | '60s'
    style?: string
  }) => {
    generating.value = true
    state.value = 'loading'

    try {
      await new Promise(resolve => setTimeout(resolve, 3000))

      copies.value = [
        {
          id: 'v1',
          content: `[0-3s] 开场：你知道吗？90% 的人买保险都踩过这些坑！\n[3-10s] 痛点：保费贵、保障少、理赔难...\n[10-25s] 解决方案：${params.topic}，教你避开保险陷阱\n[25-30s] CTA：关注我，获取更多保险干货`,
          hashtags: ['#保险科普', '#避坑指南', params.topic],
          score: 0.90,
          type: 'video',
          createdAt: new Date().toISOString()
        }
      ]
      state.value = 'success'
    } catch (error) {
      state.value = 'error'
      errorMessage.value = '生成失败'
    } finally {
      generating.value = false
    }
  }

  const clearCopies = () => {
    copies.value = []
    state.value = 'idle'
    errorMessage.value = null
  }

  const likeCopy = (id: string) => {
    const copy = copies.value.find(c => c.id === id)
    if (copy) {
      // TODO: 上报点赞
      console.log('Liked copy:', id)
    }
  }

  return {
    // State
    copies,
    generating,
    state,
    errorMessage,
    partialItems,
    // Actions
    generateWechatCopywriting,
    generateVideoScript,
    clearCopies,
    likeCopy
  }
})
