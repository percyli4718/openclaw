<!-- UI 状态矩阵组件 - 统一处理 Loading/Empty/Success/Error/Partial 状态 -->
<template>
  <view class="ui-state-container">
    <!-- Loading 状态 -->
    <view v-if="state === 'loading'" class="state-loading">
      <view class="loading-content">
        <view class="loading-spinner">
          <view class="spinner-circle"></view>
        </view>
        <text class="loading-text">{{ loadingText || '加载中...' }}</text>
        <view v-if="showProgress" class="loading-progress">
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: progress + '%' }"></view>
          </view>
          <text class="progress-text">{{ progress }}%</text>
        </view>
      </view>
    </view>

    <!-- Empty 状态 -->
    <view v-else-if="state === 'empty'" class="state-empty">
      <view class="empty-content">
        <view class="empty-icon">
          <text class="icon-placeholder">{{ emptyIcon || '📭' }}</text>
        </view>
        <text class="empty-title">{{ emptyTitle || '暂无内容' }}</text>
        <text class="empty-description">{{ emptyDescription || '点击按钮开始创建吧' }}</text>
        <view v-if="showExample" class="empty-example">
          <text class="example-title">示例：</text>
          <text class="example-text">{{ exampleText }}</text>
        </view>
        <slot name="action">
          <button v-if="showAction" class="empty-action btn-primary" @click="handleAction">
            {{ actionText || '立即体验' }}
          </button>
        </slot>
      </view>
    </view>

    <!-- Error 状态 -->
    <view v-else-if="state === 'error'" class="state-error">
      <view class="error-content">
        <view class="error-icon">
          <text class="icon-placeholder">⚠️</text>
        </view>
        <text class="error-title">{{ errorTitle || '出错了' }}</text>
        <text class="error-description">{{ errorMessage || '请稍后重试' }}</text>
        <button class="error-action btn-primary" @click="handleRetry">
          重试
        </button>
      </view>
    </view>

    <!-- Partial 状态 -->
    <view v-else-if="state === 'partial'" class="state-partial">
      <view class="partial-content">
        <view class="partial-header">
          <text class="partial-title">部分完成</text>
          <text class="partial-description">{{ partialDescription || '部分内容生成失败，可重试失败项' }}</text>
        </view>
        <view class="partial-list">
          <view v-for="(item, index) in partialItems" :key="index" class="partial-item">
            <text class="item-status" :class="item.success ? 'success' : 'failed'">
              {{ item.success ? '✓' : '✕' }}
            </text>
            <text class="item-name">{{ item.name }}</text>
            <button v-if="!item.success" class="item-retry" @click="handleRetryItem(index)">
              重试
            </button>
          </view>
        </view>
      </view>
    </view>

    <!-- Success 状态 - 内容通过 slot 传入 -->
    <view v-else-if="state === 'success'" class="state-success">
      <slot name="content"></slot>
    </view>
  </view>
</template>

<script setup lang="ts">
interface Props {
  state: 'loading' | 'empty' | 'success' | 'error' | 'partial'
  loadingText?: string
  showProgress?: boolean
  progress?: number
  emptyIcon?: string
  emptyTitle?: string
  emptyDescription?: string
  showExample?: boolean
  exampleText?: string
  showAction?: boolean
  actionText?: string
  errorTitle?: string
  errorMessage?: string
  partialDescription?: string
  partialItems?: Array<{ name: string; success: boolean }>
}

const props = withDefaults(defineProps<Props>(), {
  state: 'loading',
  loadingText: '加载中...',
  showProgress: false,
  progress: 0,
  emptyTitle: '暂无内容',
  emptyDescription: '点击按钮开始创建吧',
  showExample: false,
  showAction: true,
  actionText: '立即体验',
  errorTitle: '出错了',
  errorMessage: '请稍后重试',
  partialDescription: '部分内容生成失败，可重试失败项',
  partialItems: () => []
})

const emit = defineEmits<{
  action: []
  retry: []
  retryItem: [index: number]
}>()

const handleAction = () => {
  emit('action')
}

const handleRetry = () => {
  emit('retry')
}

const handleRetryItem = (index: number) => {
  emit('retryItem', index)
}
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';
@import '../../styles/mixins.scss';

.ui-state-container {
  min-height: 400px;
  @include flex-center;
}

// Loading 状态
.state-loading {
  @include flex-center;

  .loading-content {
    @include flex(column, center, center);
    gap: $spacing-4;
  }

  .loading-spinner {
    width: 48px;
    height: 48px;
    position: relative;
  }

  .spinner-circle {
    width: 100%;
    height: 100%;
    border: 3px solid $border-color;
    border-top-color: $color-primary;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .loading-text {
    font-size: $font-size-md;
    color: $text-color-secondary;
  }

  .loading-progress {
    @include flex(column, center, center);
    gap: $spacing-2;
    margin-top: $spacing-2;
  }

  .progress-bar {
    width: 200px;
    height: 4px;
    background: $border-color;
    border-radius: $radius-full;
    overflow: hidden;

    .progress-fill {
      height: 100%;
      background: $color-primary;
      transition: width $transition-slow;
    }
  }

  .progress-text {
    font-size: $font-size-xs;
    color: $text-color-tertiary;
  }
}

// Empty 状态
.state-empty {
  @include flex-center;

  .empty-content {
    @include flex(column, center, center);
    gap: $spacing-4;
    padding: $spacing-8;
  }

  .empty-icon {
    font-size: 64px;

    .icon-placeholder {
      font-size: 64px;
    }
  }

  .empty-title {
    font-size: $font-size-lg;
    font-weight: $font-weight-semibold;
    color: $text-color-primary;
  }

  .empty-description {
    font-size: $font-size-md;
    color: $text-color-tertiary;
    text-align: center;
  }

  .empty-example {
    background: $bg-color-page;
    padding: $spacing-4;
    border-radius: $radius-md;
    margin-top: $spacing-2;

    .example-title {
      font-weight: $font-weight-medium;
      color: $text-color-secondary;
    }

    .example-text {
      color: $text-color-tertiary;
      font-size: $font-size-sm;
    }
  }

  .empty-action {
    margin-top: $spacing-4;
    min-width: 120px;
  }
}

// Error 状态
.state-error {
  @include flex-center;

  .error-content {
    @include flex(column, center, center);
    gap: $spacing-4;
    padding: $spacing-8;
  }

  .error-icon {
    font-size: 48px;

    .icon-placeholder {
      font-size: 48px;
    }
  }

  .error-title {
    font-size: $font-size-lg;
    font-weight: $font-weight-semibold;
    color: $color-danger;
  }

  .error-description {
    font-size: $font-size-md;
    color: $text-color-tertiary;
    text-align: center;
  }

  .error-action {
    margin-top: $spacing-4;
    min-width: 120px;
  }
}

// Partial 状态
.state-partial {
  width: 100%;

  .partial-content {
    padding: $spacing-6;
  }

  .partial-header {
    @include flex(column, flex-start, flex-start);
    gap: $spacing-2;
    margin-bottom: $spacing-4;

    .partial-title {
      font-size: $font-size-lg;
      font-weight: $font-weight-semibold;
      color: $color-warning;
    }

    .partial-description {
      font-size: $font-size-md;
      color: $text-color-secondary;
    }
  }

  .partial-list {
    @include flex(column, flex-start, stretch);
    gap: $spacing-3;

    .partial-item {
      @include flex-between;
      padding: $spacing-3 $spacing-4;
      background: $bg-color-page;
      border-radius: $radius-md;

      .item-status {
        font-size: $font-size-lg;
        margin-right: $spacing-2;

        &.success {
          color: $color-success;
        }

        &.failed {
          color: $color-danger;
        }
      }

      .item-name {
        flex: 1;
        font-size: $font-size-md;
        color: $text-color-secondary;
      }

      .item-retry {
        font-size: $font-size-sm;
        padding: 4px 12px;
        background: $color-primary;
        color: white;
        border: none;
        border-radius: $radius-sm;
      }
    }
  }
}

// Success 状态 - 内容由 slot 提供
.state-success {
  width: 100%;
}
</style>
