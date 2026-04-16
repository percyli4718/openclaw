<!-- 首页 - 保客通仪表板 -->
<template>
  <view class="index-page">
    <!-- 自定义导航栏 -->
    <view class="custom-navbar">
      <view class="navbar-content">
        <view class="brand">
          <text class="brand-name">保客通</text>
          <text class="brand-slogan">AI+ 保险获客系统</text>
        </view>
        <view class="user-info" @click="goToProfile">
          <image v-if="appStore.userAvatar" :src="appStore.userAvatar" class="avatar" />
          <view v-else class="avatar-placeholder">{{ userNameFirstChar }}</view>
          <text class="user-name">{{ appStore.userName }}</text>
        </view>
      </view>
    </view>

    <!-- 内容区域 -->
    <scroll-view scroll-y class="content">
      <!-- 欢迎卡片 -->
      <view class="welcome-card card">
        <view class="welcome-header">
          <text class="welcome-title">早上好，{{ appStore.userName }}！</text>
          <text class="welcome-date">{{ todayDate }}</text>
        </view>
        <view class="welcome-stats">
          <view class="stat-item">
            <text class="stat-value">{{ stats.totalCustomers }}</text>
            <text class="stat-label">总客户数</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">{{ stats.todayFollowups }}</text>
            <text class="stat-label">今日待跟进</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">{{ stats.generatedContent }}</text>
            <text class="stat-label">已生成内容</text>
          </view>
        </view>
      </view>

      <!-- 核心功能入口 -->
      <view class="feature-grid">
        <view class="feature-card card" @click="navigateTo('/src/pages/content-gen/content-gen')">
          <view class="feature-icon content-gen-icon">📝</view>
          <view class="feature-info">
            <text class="feature-title">内容生成</text>
            <text class="feature-desc">AI 生成朋友圈/短视频/海报文案</text>
          </view>
          <view class="feature-arrow">›</view>
        </view>

        <view class="feature-card card" @click="navigateTo('/src/pages/customer/customer')">
          <view class="feature-icon customer-icon">👥</view>
          <view class="feature-info">
            <text class="feature-title">客户管理</text>
            <text class="feature-desc">客户画像分析、分层、需求预测</text>
          </view>
          <view class="feature-arrow">›</view>
        </view>

        <view class="feature-card card" @click="navigateTo('/src/pages/followup/followup')">
          <view class="feature-icon followup-icon">📅</view>
          <view class="feature-info">
            <text class="feature-title">跟进管理</text>
            <text class="feature-desc">自动化跟进、定时消息推送</text>
          </view>
          <view class="feature-arrow">›</view>
        </view>

        <view class="feature-card card" @click="navigateToAnalytics">
          <view class="feature-icon analytics-icon">📊</view>
          <view class="feature-info">
            <text class="feature-title">数据分析</text>
            <text class="feature-desc">获客效果分析、策略优化</text>
          </view>
          <view class="feature-arrow">›</view>
        </view>
      </view>

      <!-- 今日待办 -->
      <view class="section">
        <view class="section-header">
          <text class="section-title">今日待办</text>
          <text class="section-action" @click="navigateTo('/src/pages/followup/followup')">查看全部 ›</text>
        </view>
        <view class="todo-list">
          <view v-if="loadingTodos" class="todo-loading">
            <view class="spinner"></view>
            <text>加载中...</text>
          </view>
          <view v-else-if="todos.length === 0" class="todo-empty">
            <text>🎉</text>
            <text>今日暂无待办事项</text>
          </view>
          <view v-else v-for="todo in todos" :key="todo.id" class="todo-item">
            <view class="todo-left">
              <view :class="['todo-icon', todo.type]">
                {{ getTodoIcon(todo.type) }}
              </view>
              <view class="todo-content">
                <text class="todo-text">{{ todo.content }}</text>
                <text class="todo-customer">{{ todo.customerName }}</text>
              </view>
            </view>
            <view class="todo-time">{{ formatTodoTime(todo.scheduledAt) }}</view>
          </view>
        </view>
      </view>

      <!-- 最近生成的内容 -->
      <view class="section">
        <view class="section-header">
          <text class="section-title">最近生成的内容</text>
          <text class="section-action" @click="navigateTo('/src/pages/content-gen/content-gen')">更多 ›</text>
        </view>
        <view class="recent-content">
          <view v-if="loadingContent" class="content-loading">
            <view class="skeleton-line"></view>
            <view class="skeleton-line"></view>
            <view class="skeleton-line"></view>
          </view>
          <view v-else-if="recentContents.length === 0" class="content-empty">
            <text>📭</text>
            <text>暂无生成的内容，去创作吧</text>
          </view>
          <view v-else v-for="content in recentContents" :key="content.id" class="content-item card">
            <view class="content-type">{{ content.type }}</view>
            <text class="content-preview">{{ content.preview }}</text>
            <view class="content-meta">
              <text class="content-score">评分：{{ (content.score * 100).toFixed(0) }}</text>
              <text class="content-time">{{ content.createdAt }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 底部占位 -->
      <view class="bottom-placeholder"></view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/src/stores/app'
import { useFollowupStore } from '@/src/stores/followup'

const appStore = useAppStore()
const followupStore = useFollowupStore()

// 计算用户名首字
const userNameFirstChar = computed(() => {
  const name = appStore.userName
  return name.charAt(0)
})

// 日期
const todayDate = computed(() => {
  const now = new Date()
  const month = now.getMonth() + 1
  const day = now.getDate()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${month}月${day}日 ${weekdays[now.getDay()]}`
})

// 统计数据
const stats = ref({
  totalCustomers: 128,
  todayFollowups: 5,
  generatedContent: 42
})

// 待办事项
const loadingTodos = ref(false)
const todos = ref<any[]>([])

// 最近内容
const loadingContent = ref(false)
const recentContents = ref<any[]>([])

// 初始化加载
onMounted(async () => {
  await loadData()
})

const loadData = async () => {
  // 加载待办
  loadingTodos.value = true
  try {
    await followupStore.loadPlans()
    todos.value = followupStore.todayTasks.slice(0, 5).map(task => ({
      id: task.id,
      type: task.type,
      content: task.content,
      customerName: '张先生',
      scheduledAt: task.scheduledAt
    }))
  } catch (e) {
    console.error('Load todos failed:', e)
  } finally {
    loadingTodos.value = false
  }

  // 加载最近内容 (Mock)
  loadingContent.value = true
  setTimeout(() => {
    recentContents.value = [
      {
        id: '1',
        type: '朋友圈文案',
        preview: '【健康保】为您保驾护航！人生路上，风险难料...',
        score: 0.92,
        createdAt: '10 分钟前'
      },
      {
        id: '2',
        type: '短视频脚本',
        preview: '[0-3s] 开场：你知道吗？90% 的人买保险都踩过这些坑！...',
        score: 0.88,
        createdAt: '1 小时前'
      }
    ]
    loadingContent.value = false
  }, 800)
}

// 导航方法
const navigateTo = (url: string) => {
  uni.navigateTo({ url })
}

const navigateToAnalytics = () => {
  uni.showToast({
    title: '数据分析即将上线',
    icon: 'none'
  })
}

const goToProfile = () => {
  uni.showToast({
    title: '个人中心即将上线',
    icon: 'none'
  })
}

// 工具方法
const getTodoIcon = (type: string) => {
  const icons: Record<string, string> = {
    message: '💬',
    call: '📞',
    meeting: '🤝',
    reminder: '⏰'
  }
  return icons[type] || '📌'
}

const formatTodoTime = (time: string) => {
  const date = new Date(time)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';
@import '../../styles/mixins.scss';

.index-page {
  min-height: 100vh;
  background: $bg-color-page;
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

// 自定义导航栏
.custom-navbar {
  @include gradient-navbar;
  padding: $spacing-4 $spacing-6;
  padding-top: constant(safe-area-inset-top);
  padding-top: env(safe-area-inset-top);

  .navbar-content {
    @include flex-between;
  }

  .brand {
    @include flex(column, flex-start, flex-start);
    gap: 2px;

    .brand-name {
      font-size: 20px;
      font-weight: 700;
      color: white;
    }

    .brand-slogan {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.8);
    }
  }

  .user-info {
    @include flex(row, flex-end, center);
    gap: $spacing-2;

    .avatar, .avatar-placeholder {
      width: 36px;
      height: 36px;
      border-radius: 50%;
    }

    .avatar-placeholder {
      @include flex-center;
      background: rgba(255, 255, 255, 0.3);
      color: white;
      font-size: 16px;
      font-weight: 600;
    }

    .user-name {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.9);
    }
  }
}

// 内容区域
.content {
  height: calc(100vh - 80px);
  padding: $spacing-4;
}

// 欢迎卡片
.welcome-card {
  @include gradient-card;
  margin-bottom: $spacing-4;

  .welcome-header {
    @include flex-between;
    margin-bottom: $spacing-4;

    .welcome-title {
      font-size: $font-size-lg;
      font-weight: 600;
      color: $text-color-primary;
    }

    .welcome-date {
      font-size: $font-size-sm;
      color: $text-color-secondary;
    }
  }

  .welcome-stats {
    @include flex(row, space-between, center);

    .stat-item {
      flex: 1;
      @include flex(column, center, center);
      gap: $spacing-1;

      .stat-value {
        font-size: 24px;
        font-weight: 700;
        color: $color-primary;
      }

      .stat-label {
        font-size: $font-size-xs;
        color: $text-color-secondary;
      }
    }

    .stat-divider {
      width: 1px;
      height: 40px;
      background: $border-color;
    }
  }
}

// 功能网格
.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-3;
  margin-bottom: $spacing-4;

  .feature-card {
    @include card;
    @include flex(row, flex-start, center);
    gap: $spacing-3;
    padding: $spacing-4;
    min-height: 100px;
    position: relative;

    &:active {
      transform: scale(0.98);
    }

    .feature-icon {
      font-size: 32px;
      width: 48px;
      height: 48px;
      @include flex-center;
      border-radius: $radius-lg;
    }

    .content-gen-icon { background: $color-primary-bg; }
    .customer-icon { background: $color-success-bg; }
    .followup-icon { background: $color-warning-bg; }
    .analytics-icon { background: $color-info-bg; }

    .feature-info {
      flex: 1;
      @include flex(column, flex-start, flex-start);
      gap: 4px;

      .feature-title {
        font-size: $font-size-md;
        font-weight: 600;
        color: $text-color-primary;
      }

      .feature-desc {
        font-size: $font-size-xs;
        color: $text-color-tertiary;
      }
    }

    .feature-arrow {
      font-size: 24px;
      color: $text-color-tertiary;
    }
  }
}

// 区块
.section {
  margin-bottom: $spacing-4;

  .section-header {
    @include flex-between;
    margin-bottom: $spacing-3;
    padding: 0 $spacing-2;

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

// 待办列表
.todo-list {
  @include flex(column, flex-start, stretch);
  gap: $spacing-2;

  .todo-loading, .todo-empty {
    @include flex-center;
    gap: $spacing-2;
    padding: $spacing-8;
    color: $text-color-secondary;
  }

  .todo-item {
    @include card;
    @include flex-between;
    padding: $spacing-3 $spacing-4;

    .todo-left {
      @include flex(row, flex-start, center);
      gap: $spacing-3;
    }

    .todo-icon {
      width: 36px;
      height: 36px;
      @include flex-center;
      font-size: 18px;
      border-radius: $radius-md;

      &.message { background: $color-primary-bg; }
      &.call { background: $color-success-bg; }
      &.meeting { background: $color-warning-bg; }
      &.reminder { background: $color-danger-bg; }
    }

    .todo-content {
      @include flex(column, flex-start, flex-start);
      gap: 4px;

      .todo-text {
        font-size: $font-size-md;
        color: $text-color-primary;
      }

      .todo-customer {
        font-size: $font-size-xs;
        color: $text-color-tertiary;
      }
    }

    .todo-time {
      font-size: $font-size-sm;
      color: $text-color-tertiary;
    }
  }
}

// 最近内容
.recent-content {
  @include flex(column, flex-start, stretch);
  gap: $spacing-2;

  .content-loading, .content-empty {
    @include flex-center;
    gap: $spacing-2;
    padding: $spacing-8;
    color: $text-color-secondary;
  }

  .content-loading .skeleton-line {
    height: 60px;
    background: $border-color;
    border-radius: $radius-md;
    margin-bottom: $spacing-2;
  }

  .content-item {
    @include card;
    padding: $spacing-4;

    .content-type {
      display: inline-block;
      padding: 4px 12px;
      background: $color-primary-bg;
      color: $color-primary;
      font-size: $font-size-xs;
      font-weight: 500;
      border-radius: $radius-full;
      margin-bottom: $spacing-2;
    }

    .content-preview {
      display: block;
      font-size: $font-size-md;
      color: $text-color-secondary;
      margin-bottom: $spacing-2;
      @include text-ellipsis-multi(2);
    }

    .content-meta {
      @include flex-between;

      .content-score {
        font-size: $font-size-xs;
        color: $color-success;
      }

      .content-time {
        font-size: $font-size-xs;
        color: $text-color-tertiary;
      }
    }
  }
}

// 底部占位
.bottom-placeholder {
  height: 100px;
}
</style>
