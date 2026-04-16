// Pinia Store - 跟进管理状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface FollowupPlan {
  id: string
  customerId: string
  customerName: string
  tasks: FollowupTask[]
  status: 'pending' | 'in_progress' | 'completed' | 'overdue'
  createdAt: string
}

interface FollowupTask {
  id: string
  planId: string
  type: 'message' | 'call' | 'meeting' | 'reminder'
  content: string
  scheduledAt: string
  status: 'pending' | 'completed' | 'skipped' | 'failed'
  result?: string
}

interface FollowupState {
  plans: FollowupPlan[]
  todayTasks: FollowupTask[]
  loading: boolean
  state: 'idle' | 'loading' | 'success' | 'error' | 'empty'
  errorMessage: string | null
}

export const useFollowupStore = defineStore('followup', () => {
  // State
  const plans = ref<FollowupPlan[]>([])
  const todayTasks = ref<FollowupTask[]>([])
  const loading = ref(false)
  const state = ref<FollowupState['state']>('idle')
  const errorMessage = ref<string | null>(null)

  // Getters
  const taskStats = computed(() => {
    const total = todayTasks.value.length
    const completed = todayTasks.value.filter(t => t.status === 'completed').length
    const pending = todayTasks.value.filter(t => t.status === 'pending').length
    const overdue = plans.value.filter(p => p.status === 'overdue').length

    return { total, completed, pending, overdue }
  })

  const upcomingTasks = computed(() => {
    return todayTasks.value
      .filter(t => t.status === 'pending')
      .sort((a, b) => new Date(a.scheduledAt).getTime() - new Date(b.scheduledAt).getTime())
  })

  // Actions
  const loadPlans = async () => {
    loading.value = true
    state.value = 'loading'

    try {
      // TODO: 调用后端 API
      // const res = await api.getFollowupPlans()
      // plans.value = res.data

      // Mock 数据
      await new Promise(resolve => setTimeout(resolve, 1000))

      plans.value = [
        {
          id: '1',
          customerId: '1',
          customerName: '张先生',
          tasks: [
            {
              id: 't1',
              planId: '1',
              type: 'message',
              content: '发送重疾险产品介绍',
              scheduledAt: '2026-04-16T10:00:00Z',
              status: 'pending'
            },
            {
              id: 't2',
              planId: '1',
              type: 'call',
              content: '电话跟进，了解需求',
              scheduledAt: '2026-04-18T15:00:00Z',
              status: 'pending'
            }
          ],
          status: 'in_progress',
          createdAt: '2026-04-15T09:00:00Z'
        },
        {
          id: '2',
          customerId: '2',
          customerName: '李女士',
          tasks: [
            {
              id: 't3',
              planId: '2',
              type: 'message',
              content: '发送意外险方案',
              scheduledAt: '2026-04-16T14:00:00Z',
              status: 'pending'
            }
          ],
          status: 'pending',
          createdAt: '2026-04-15T11:00:00Z'
        }
      ]

      todayTasks.value = plans.value.flatMap(p =>
        p.tasks.filter(t => {
          const today = new Date().toDateString()
          return new Date(t.scheduledAt).toDateString() === today
        })
      )

      state.value = 'success'
    } catch (error) {
      state.value = 'error'
      errorMessage.value = '加载跟进计划失败'
      console.error('Load plans failed:', error)
    } finally {
      loading.value = false
    }
  }

  const createFollowupPlan = async (params: {
    customerId: string
    customerName: string
    tasks: Array<{
      type: FollowupTask['type']
      content: string
      scheduledAt: string
    }>
  }) => {
    loading.value = true

    try {
      // TODO: 调用后端 API
      // await api.createFollowupPlan(params)

      await new Promise(resolve => setTimeout(resolve, 1500))

      const newPlan: FollowupPlan = {
        id: Date.now().toString(),
        customerId: params.customerId,
        customerName: params.customerName,
        tasks: params.tasks.map((t, i) => ({
          id: `t${Date.now()}-${i}`,
          planId: Date.now().toString(),
          ...t,
          status: 'pending'
        })),
        status: 'pending',
        createdAt: new Date().toISOString()
      }

      plans.value.unshift(newPlan)
      return newPlan
    } catch (error) {
      console.error('Create plan failed:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const completeTask = async (taskId: string, result?: string) => {
    try {
      // TODO: 调用后端 API
      // await api.completeTask(taskId, result)

      const task = todayTasks.value.find(t => t.id === taskId)
      if (task) {
        task.status = 'completed'
        task.result = result
      }
    } catch (error) {
      console.error('Complete task failed:', error)
      throw error
    }
  }

  const scheduleMessage = async (params: {
    customerId: string
    content: string
    scheduledAt: string
  }) => {
    try {
      // TODO: 调用后端 API
      // await api.scheduleMessage(params)

      console.log('Message scheduled:', params)
      return { success: true }
    } catch (error) {
      console.error('Schedule message failed:', error)
      throw error
    }
  }

  const generateFollowupPlan = async (customerId: string) => {
    loading.value = true

    try {
      // TODO: 调用后端 AI API 生成跟进计划
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Mock AI 生成的计划
      return {
        tasks: [
          { type: 'message', content: '发送产品介绍', scheduledAt: '2026-04-16T10:00:00Z' },
          { type: 'call', content: '电话跟进', scheduledAt: '2026-04-18T15:00:00Z' }
        ]
      }
    } finally {
      loading.value = false
    }
  }

  const getOverduePlans = () => {
    return plans.value.filter(p => p.status === 'overdue')
  }

  return {
    // State
    plans,
    todayTasks,
    loading,
    state,
    errorMessage,
    // Getters
    taskStats,
    upcomingTasks,
    // Actions
    loadPlans,
    createFollowupPlan,
    completeTask,
    scheduleMessage,
    generateFollowupPlan,
    getOverduePlans
  }
})
