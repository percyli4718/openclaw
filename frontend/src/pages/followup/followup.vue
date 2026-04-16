<!-- 跟进管理页面 -->
<template>
  <view class="followup-page">
    <!-- 今日概览 -->
    <view class="overview-card card">
      <view class="overview-header">
        <text class="overview-title">今日概览</text>
        <text class="overview-date">{{ todayDate }}</text>
      </view>
      <view class="overview-stats">
        <view class="stat-item">
          <text class="stat-value">{{ store.taskStats.total }}</text>
          <text class="stat-label">总任务</text>
        </view>
        <view class="stat-item">
          <text class="stat-value" style="color: #16a34a">{{ store.taskStats.completed }}</text>
          <text class="stat-label">已完成</text>
        </view>
        <view class="stat-item">
          <text class="stat-value" style="color: #d97706">{{ store.taskStats.pending }}</text>
          <text class="stat-label">待完成</text>
        </view>
        <view class="stat-item">
          <text class="stat-value" style="color: #ef4444">{{ store.taskStats.overdue }}</text>
          <text class="stat-label">已逾期</text>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-bar">
      <button class="action-btn btn-primary" @click="handleCreatePlan">
        <text class="btn-icon">+</text>
        创建跟进计划
      </button>
      <button class="action-btn btn-secondary" @click="handleGeneratePlan">
        <text class="btn-icon">✨</text>
        AI 生成计划
      </button>
    </view>

    <!-- 待办任务列表 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">今日待办</text>
      </view>

      <UiState
        :state="uiState"
        :loading-text="loadingText"
        :empty-title="emptyTitle"
        :empty-description="emptyDescription"
        :show-example="false"
        :action-text="actionText"
        @action="handleCreatePlan"
        @retry="loadPlans"
      >
        <template #content>
          <view class="task-list">
            <view
              v-for="task in store.upcomingTasks"
              :key="task.id"
              class="task-card card"
              :class="{ 'task-completed': task.status === 'completed' }"
            >
              <view class="task-header">
                <view :class="['task-icon', task.type]">
                  {{ getTaskIcon(task.type) }}
                </view>
                <view class="task-content">
                  <text class="task-text" :class="{ completed: task.status === 'completed' }">
                    {{ task.content }}
                  </text>
                  <text class="task-customer">{{ task.planId }}</text>
                </view>
                <view class="task-time">{{ formatTaskTime(task.scheduledAt) }}</view>
              </view>

              <view class="task-actions">
                <button
                  v-if="task.status !== 'completed'"
                  class="complete-btn btn-primary"
                  @click="handleCompleteTask(task)"
                >
                  完成
                </button>
                <button class="detail-btn btn-secondary" @click="handleViewDetail(task)">
                  详情
                </button>
              </view>
            </view>
          </view>
        </template>
      </UiState>
    </view>

    <!-- 跟进计划列表 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">跟进计划</text>
        <text class="section-action">查看全部 ›</text>
      </view>

      <view class="plan-list">
        <view
          v-for="plan in store.plans"
          :key="plan.id"
          class="plan-card card"
          @click="handleViewPlan(plan)"
        >
          <view class="plan-header">
            <view class="plan-customer">
              <text class="customer-name">{{ plan.customerName }}</text>
              <view :class="['status-badge', 'status-' + plan.status]">
                {{ getStatusText(plan.status) }}
              </view>
            </view>
            <text class="plan-arrow">›</text>
          </view>

          <view class="plan-tasks">
            <view v-for="task in plan.tasks.slice(0, 3)" :key="task.id" class="plan-task-item">
              <view :class="['task-dot', task.status]"></view>
              <text class="task-content">{{ task.content }}</text>
              <text class="task-date">{{ formatDate(task.scheduledAt) }}</text>
            </view>
            <view v-if="plan.tasks.length > 3" class="more-tasks">
              还有{{ plan.tasks.length - 3 }}项任务...
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部占位 -->
    <view class="bottom-placeholder"></view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import UiState from '@/src/components/UiState.vue'
import { useFollowupStore } from '@/src/stores/followup'

const store = useFollowupStore()

// 今日日期
const todayDate = computed(() => {
  const now = new Date()
  return `${now.getMonth() + 1}月${now.getDate()}日`
})

// UI 状态
const uiState = computed(() => store.state)
const loadingText = ref('正在加载跟进计划...')
const emptyTitle = ref('暂无跟进计划')
const emptyDescription = ref('创建跟进计划，AI 自动安排最佳跟进节奏')
const actionText = ref('创建计划')

// 加载计划
const loadPlans = async () => {
  await store.loadPlans()
}

// 创建计划
const handleCreatePlan = () => {
  uni.showToast({
    title: '创建计划功能开发中',
    icon: 'none'
  })
}

// AI 生成计划
const handleGeneratePlan = async () => {
  uni.showLoading({ title: 'AI 生成中...' })
  try {
    const result = await store.generateFollowupPlan('customer-1')
    console.log('Generated plan:', result)
    uni.hideLoading()
    uni.showToast({
      title: '计划生成成功',
      icon: 'success'
    })
  } catch (e) {
    uni.hideLoading()
    uni.showToast({
      title: '生成失败',
      icon: 'none'
    })
  }
}

// 完成任务
const handleCompleteTask = async (task: any) => {
  try {
    await store.completeTask(task.id, '已完成')
    uni.showToast({
      title: '任务已完成',
      icon: 'success'
    })
    await loadPlans()
  } catch (e) {
    uni.showToast({
      title: '完成失败',
      icon: 'none'
    })
  }
}

// 查看详情
const handleViewDetail = (task: any) => {
  uni.showToast({
    title: '任务详情开发中',
    icon: 'none'
  })
}

// 查看计划
const handleViewPlan = (plan: any) => {
  uni.showToast({
    title: '计划详情开发中',
    icon: 'none'
  })
}

// 获取任务图标
const getTaskIcon = (type: string) => {
  const icons: Record<string, string> = {
    message: '💬',
    call: '📞',
    meeting: '🤝',
    reminder: '⏰'
  }
  return icons[type] || '📌'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待开始',
    in_progress: '进行中',
    completed: '已完成',
    overdue: '已逾期'
  }
  return texts[status] || status
}

// 格式化任务时间
const formatTaskTime = (time: string) => {
  const date = new Date(time)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

// 格式化日期
const formatDate = (time: string) => {
  const date = new Date(time)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

onMounted(() => {
  loadPlans()
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';
@import '../../styles/mixins.scss';

.followup-page {
  min-height: 100vh;
  background: $bg-color-page;
  padding: $spacing-4;
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

// 概览卡片
.overview-card {
  @include card;
  margin-bottom: $spacing-4;

  .overview-header {
    @include flex-between;
    margin-bottom: $spacing-4;

    .overview-title {
      font-size: $font-size-lg;
      font-weight: 600;
      color: $text-color-primary;
    }

    .overview-date {
      font-size: $font-size-sm;
      color: $text-color-secondary;
    }
  }

  .overview-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: $spacing-2;

    .stat-item {
      @include flex(column, center, center);
      gap: $spacing-1;

      .stat-value {
        font-size: 18px;
        font-weight: 700;
      }

      .stat-label {
        font-size: 11px;
        color: $text-color-secondary;
      }
    }
  }
}

// 操作栏
.action-bar {
  @include flex(row, space-between, center);
  gap: $spacing-3;
  margin-bottom: $spacing-4;

  .action-btn {
    flex: 1;
    @include flex(row, center, center);
    gap: $spacing-2;
    padding: 12px;
    border-radius: $radius-md;
    font-size: $font-size-sm;
    font-weight: 500;
    border: none;

    .btn-icon {
      font-size: 18px;
    }
  }
}

// 区块
.section {
  margin-bottom: $spacing-4;

  .section-header {
    @include flex-between;
    margin-bottom: $spacing-3;

    .section-title {
      font-size: $font-size-md;
      font-weight: 600;
      color: $text-color-primary;
    }

    .section-action {
      font-size: $font-size-sm;
      color: $color-primary;
    }
  }
}

// 任务列表
.task-list {
  @include flex(column, flex-start, stretch);
  gap: $spacing-2;
}

.task-card {
  @include card;

  &.task-completed {
    opacity: 0.6;

    .task-text {
      text-decoration: line-through;
    }
  }

  .task-header {
    @include flex(row, flex-start, center);
    gap: $spacing-3;
    margin-bottom: $spacing-3;

    .task-icon {
      width: 40px;
      height: 40px;
      @include flex-center;
      font-size: 18px;
      border-radius: $radius-md;
      flex-shrink: 0;

      &.message { background: $color-primary-bg; }
      &.call { background: $color-success-bg; }
      &.meeting { background: $color-warning-bg; }
      &.reminder { background: $color-danger-bg; }
    }

    .task-content {
      flex: 1;
      @include flex(column, flex-start, flex-start);
      gap: 4px;

      .task-text {
        font-size: $font-size-base;
        color: $text-color-primary;

        &.completed {
          text-decoration: line-through;
          color: $text-color-tertiary;
        }
      }

      .task-customer {
        font-size: $font-size-xs;
        color: $text-color-secondary;
      }
    }

    .task-time {
      font-size: $font-size-sm;
      color: $text-color-tertiary;
    }
  }

  .task-actions {
    @include flex(row, flex-end, center);
    gap: $spacing-2;

    .complete-btn {
      padding: 8px 20px;
      font-size: $font-size-sm;
    }

    .detail-btn {
      padding: 8px 20px;
      font-size: $font-size-sm;
    }
  }
}

// 计划列表
.plan-list {
  @include flex(column, flex-start, stretch);
  gap: $spacing-2;
}

.plan-card {
  @include card;

  .plan-header {
    @include flex-between;
    margin-bottom: $spacing-3;

    .plan-customer {
      @include flex(row, flex-start, center);
      gap: $spacing-2;

      .customer-name {
        font-size: $font-size-base;
        font-weight: 600;
        color: $text-color-primary;
      }

      .status-badge {
        padding: 4px 10px;
        border-radius: $radius-full;
        font-size: 11px;
        font-weight: 500;

        &.status-pending { background: $color-primary-bg; color: $color-primary; }
        &.status-in_progress { background: $color-warning-bg; color: $color-warning; }
        &.status-completed { background: $color-success-bg; color: $color-success; }
        &.status-overdue { background: $color-danger-bg; color: $color-danger; }
      }
    }

    .plan-arrow {
      font-size: 24px;
      color: $text-color-tertiary;
    }
  }

  .plan-tasks {
    @include flex(column, flex-start, stretch);
    gap: $spacing-2;

    .plan-task-item {
      @include flex(row, flex-start, center);
      gap: $spacing-2;

      .task-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;

        &.pending { background: $color-primary; }
        &.completed { background: $color-success; }
        &.failed { background: $color-danger; }
      }

      .task-content {
        flex: 1;
        font-size: $font-size-sm;
        color: $text-color-secondary;
      }

      .task-date {
        font-size: $font-size-xs;
        color: $text-color-tertiary;
      }
    }

    .more-tasks {
      font-size: $font-size-xs;
      color: $text-color-tertiary;
      padding: $spacing-2 0;
    }
  }
}

// 底部占位
.bottom-placeholder {
  height: 80px;
}
</style>
