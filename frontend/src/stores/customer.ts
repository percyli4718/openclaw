// Pinia Store - 客户管理状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Customer {
  id: string
  name: string
  phone?: string
  tags: string[]
  level: 'A' | 'B' | 'C' | 'D'
  source: string
  needs: string[]
  lastFollowupAt?: string
  nextFollowupAt?: string
  createdAt: string
}

interface CustomerState {
  customers: Customer[]
  loading: boolean
  state: 'idle' | 'loading' | 'success' | 'error' | 'empty'
  errorMessage: string | null
  filterLevel?: string
  searchText: string
}

export const useCustomerStore = defineStore('customer', () => {
  // State
  const customers = ref<Customer[]>([])
  const loading = ref(false)
  const state = ref<CustomerState['state']>('idle')
  const errorMessage = ref<string | null>(null)
  const filterLevel = ref<string>()
  const searchText = ref('')

  // Getters
  const filteredCustomers = computed(() => {
    let result = customers.value

    // 按等级筛选
    if (filterLevel.value) {
      result = result.filter(c => c.level === filterLevel.value)
    }

    // 按搜索词筛选
    if (searchText.value) {
      const keyword = searchText.value.toLowerCase()
      result = result.filter(c =>
        c.name.toLowerCase().includes(keyword) ||
        c.phone?.includes(keyword) ||
        c.tags.some(t => t.toLowerCase().includes(keyword))
      )
    }

    return result
  })

  const customerStats = computed(() => {
    const total = customers.value.length
    const byLevel = {
      A: customers.value.filter(c => c.level === 'A').length,
      B: customers.value.filter(c => c.level === 'B').length,
      C: customers.value.filter(c => c.level === 'C').length,
      D: customers.value.filter(c => c.level === 'D').length
    }
    const needFollowup = customers.value.filter(c => {
      if (!c.nextFollowupAt) return false
      return new Date(c.nextFollowupAt) <= new Date()
    }).length

    return { total, byLevel, needFollowup }
  })

  // Actions
  const loadCustomers = async () => {
    loading.value = true
    state.value = 'loading'

    try {
      // TODO: 调用后端 API
      // const res = await api.getCustomers()
      // customers.value = res.data

      // Mock 数据
      await new Promise(resolve => setTimeout(resolve, 1000))

      customers.value = [
        {
          id: '1',
          name: '张先生',
          phone: '138****1234',
          tags: ['30-40 岁', '企业主', '已婚'],
          level: 'A',
          source: '朋友圈',
          needs: ['重疾险', '医疗险'],
          nextFollowupAt: '2026-04-17T10:00:00Z',
          createdAt: '2026-04-10T08:00:00Z'
        },
        {
          id: '2',
          name: '李女士',
          phone: '139****5678',
          tags: ['25-30 岁', '白领', '单身'],
          level: 'B',
          source: '转介绍',
          needs: ['意外险', '寿险'],
          lastFollowupAt: '2026-04-14T15:00:00Z',
          nextFollowupAt: '2026-04-20T10:00:00Z',
          createdAt: '2026-04-08T10:00:00Z'
        },
        {
          id: '3',
          name: '王先生',
          phone: '136****9012',
          tags: ['40-50 岁', '高管', '已婚有孩'],
          level: 'A',
          source: '线下活动',
          needs: ['年金险', '传承规划'],
          nextFollowupAt: '2026-04-16T14:00:00Z',
          createdAt: '2026-04-05T09:00:00Z'
        }
      ]
      state.value = 'success'
    } catch (error) {
      state.value = 'error'
      errorMessage.value = '加载客户列表失败'
      console.error('Load customers failed:', error)
    } finally {
      loading.value = false
    }
  }

  const addCustomer = async (customer: Omit<Customer, 'id' | 'createdAt'>) => {
    try {
      // TODO: 调用后端 API
      // await api.addCustomer(customer)

      const newCustomer: Customer = {
        ...customer,
        id: Date.now().toString(),
        createdAt: new Date().toISOString()
      }
      customers.value.unshift(newCustomer)
    } catch (error) {
      console.error('Add customer failed:', error)
      throw error
    }
  }

  const updateCustomer = async (id: string, updates: Partial<Customer>) => {
    try {
      // TODO: 调用后端 API
      // await api.updateCustomer(id, updates)

      const index = customers.value.findIndex(c => c.id === id)
      if (index !== -1) {
        customers.value[index] = { ...customers.value[index], ...updates }
      }
    } catch (error) {
      console.error('Update customer failed:', error)
      throw error
    }
  }

  const deleteCustomer = async (id: string) => {
    try {
      // TODO: 调用后端 API
      // await api.deleteCustomer(id)

      customers.value = customers.value.filter(c => c.id !== id)
    } catch (error) {
      console.error('Delete customer failed:', error)
      throw error
    }
  }

  const importCustomers = async (file: File) => {
    loading.value = true
    state.value = 'loading'

    try {
      // TODO: 调用后端 API 导入 Excel
      // const res = await api.importCustomers(file)

      await new Promise(resolve => setTimeout(resolve, 2000))

      // Mock 导入成功
      state.value = 'success'
      return { success: true, count: 10 }
    } catch (error) {
      state.value = 'error'
      errorMessage.value = '导入失败，请检查文件格式'
      throw error
    } finally {
      loading.value = false
    }
  }

  const analyzeCustomers = async () => {
    loading.value = true

    try {
      // TODO: 调用后端 AI 分析 API
      await new Promise(resolve => setTimeout(resolve, 3000))

      // Mock 分析完成
      return {
        analyzedCount: customers.value.length,
        insights: ['30% 客户关注重疾险', 'A 类客户转化率最高']
      }
    } finally {
      loading.value = false
    }
  }

  const setFilterLevel = (level: string) => {
    filterLevel.value = level === 'all' ? undefined : level
  }

  const setSearchText = (text: string) => {
    searchText.value = text
  }

  return {
    // State
    customers,
    loading,
    state,
    errorMessage,
    filterLevel,
    searchText,
    // Getters
    filteredCustomers,
    customerStats,
    // Actions
    loadCustomers,
    addCustomer,
    updateCustomer,
    deleteCustomer,
    importCustomers,
    analyzeCustomers,
    setFilterLevel,
    setSearchText
  }
})
