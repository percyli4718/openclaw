<!-- 骨架屏组件 - 用于 Loading 状态 -->
<template>
  <view class="skeleton-container" :style="{ width: width, height: height }">
    <!-- 文本骨架 -->
    <view v-if="type === 'text'" class="skeleton-text" :class="`skeleton-text-${rows}`">
      <view v-for="i in rows" :key="i" class="skeleton-line"></view>
    </view>

    <!-- 头像骨架 -->
    <view v-else-if="type === 'avatar'" class="skeleton-avatar" :class="`skeleton-avatar-${size}`">
      <view class="skeleton-circle"></view>
    </view>

    <!-- 卡片骨架 -->
    <view v-else-if="type === 'card'" class="skeleton-card">
      <view class="skeleton-card-image"></view>
      <view class="skeleton-card-content">
        <view class="skeleton-line skeleton-line-title"></view>
        <view class="skeleton-line skeleton-line-subtitle"></view>
        <view class="skeleton-line skeleton-line-body"></view>
      </view>
    </view>

    <!-- 列表骨架 -->
    <view v-else-if="type === 'list'" class="skeleton-list">
      <view v-for="i in count" :key="i" class="skeleton-list-item">
        <view class="skeleton-circle skeleton-avatar-small"></view>
        <view class="skeleton-list-content">
          <view class="skeleton-line skeleton-line-short"></view>
          <view class="skeleton-line"></view>
        </view>
      </view>
    </view>

    <!-- 表格骨架 -->
    <view v-else-if="type === 'table'" class="skeleton-table">
      <view v-for="i in count" :key="i" class="skeleton-table-row">
        <view v-for="j in columns" :key="j" class="skeleton-table-cell" :class="`skeleton-cell-${j === 1 ? 'wide' : 'narrow'}`"></view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
interface Props {
  type?: 'text' | 'avatar' | 'card' | 'list' | 'table'
  width?: string
  height?: string
  rows?: number
  size?: 'small' | 'medium' | 'large'
  count?: number
  columns?: number
}

withDefaults(defineProps<Props>(), {
  type: 'text',
  width: '100%',
  height: 'auto',
  rows: 1,
  size: 'medium',
  count: 3,
  columns: 3
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';
@import '../../styles/mixins.scss';

.skeleton-container {
  @include skeleton-loading;
  border-radius: $radius-md;
}

// 文本骨架
.skeleton-text {
  display: flex;
  flex-direction: column;
  gap: $spacing-2;
}

.skeleton-line {
  height: 16px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: $radius-sm;

  &.skeleton-line-title {
    height: 20px;
    width: 60%;
  }

  &.skeleton-line-subtitle {
    height: 16px;
    width: 80%;
  }

  &.skeleton-line-body {
    height: 14px;
  }

  &.skeleton-line-short {
    width: 40%;
  }
}

.skeleton-text-1 .skeleton-line { width: 100%; }
.skeleton-text-2 .skeleton-line:nth-child(2) { width: 80%; }
.skeleton-text-3 .skeleton-line:nth-child(3) { width: 60%; }

// 头像骨架
.skeleton-avatar {
  display: inline-flex;

  .skeleton-circle {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.1);
  }
}

.skeleton-avatar-small .skeleton-circle {
  width: 32px;
  height: 32px;
}

.skeleton-avatar-large .skeleton-circle {
  width: 64px;
  height: 64px;
}

// 卡片骨架
.skeleton-card {
  @include card;
  padding: 0;
  overflow: hidden;

  .skeleton-card-image {
    height: 160px;
    background: rgba(0, 0, 0, 0.15);
  }

  .skeleton-card-content {
    padding: $spacing-4;
    display: flex;
    flex-direction: column;
    gap: $spacing-2;
  }
}

// 列表骨架
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-3;

  .skeleton-list-item {
    display: flex;
    align-items: center;
    gap: $spacing-3;
    padding: $spacing-3;
    background: $bg-color-card;
    border-radius: $radius-md;
  }

  .skeleton-avatar-small {
    width: 40px;
    height: 40px;
    flex-shrink: 0;
  }

  .skeleton-list-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: $spacing-2;
  }
}

// 表格骨架
.skeleton-table {
  display: flex;
  flex-direction: column;
  gap: $spacing-2;

  .skeleton-table-row {
    display: flex;
    gap: $spacing-2;
    padding: $spacing-3;
    background: $bg-color-card;
    border-radius: $radius-md;
  }

  .skeleton-table-cell {
    height: 20px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: $radius-sm;

    &.skeleton-cell-wide {
      flex: 2;
    }

    &.skeleton-cell-narrow {
      flex: 1;
    }
  }
}
</style>
