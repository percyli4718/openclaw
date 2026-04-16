<!-- 客户管理页面 -->
<template>
  <view class="customer-page">
    <!-- 搜索和筛选栏 -->
    <view class="search-bar card">
      <view class="search-input-wrapper">
        <text class="search-icon">🔍</text>
        <input
          class="search-input"
          v-model="searchText"
          placeholder="搜索客户姓名/手机/标签"
          placeholder-class="input-placeholder"
          @confirm="handleSearch"
        />
      </view>
      <button class="add-btn" @click="handleAddCustomer">
        <text class="add-icon">+</text>
      </button>
    </view>

    <!-- 客户等级筛选 -->
    <view class="filter-bar">
      <scroll-view scroll-x class="filter-scroll">
        <view
          :class="['filter-chip', filterLevel === 'all' ? 'active' : '']"
          @click="filterLevel = 'all'"
        >
          全部
        </view>
        <view
          v-for="level in ['A', 'B', 'C', 'D']"
          :key="level"
          :class="['filter-chip', filterLevel === level ? 'active' : '']"
          @click="filterLevel = level"
        >
          {{ level }}类
        </view>
      </scroll-view>
    </view>

    <!-- 客户统计 -->
    <view class="stats-card card">
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-value">{{ store.customerStats.total }}</text>
          <text class="stat-label">总客户数</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value" style="color: #ef4444">{{ store.customerStats.needFollowup }}</text>
          <text class="stat-label">待跟进</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value" style="color: #16a34a">{{ store.customerStats.byLevel.A }}</text>
          <text class="stat-label">A 类客户</text>
        </view>
      </view>
    </view>

    <!-- UI 状态展示 -->
    <UiState
      :state="uiState"
      :loading-text="loadingText"
      :empty-title="emptyTitle"
      :empty-description="emptyDescription"
      :show-example="true"
      :example-text="例如：导入 Excel 客户名单，或手动添加客户信息"
      :action-text="actionText"
      :error-message="errorMessage"
      @action="handleImport"
      @retry="loadCustomers"
    >
      <template #content>
        <!-- 客户列表 -->
        <view class="customer-list">
          <view
            v-for="customer in store.filteredCustomers"
            :key="customer.id"
            class="customer-card card"
            @click="goToDetail(customer.id)"
          >
            <view class="customer-header">
              <view class="customer-avatar">
                <text>{{ customer.name.charAt(0) }}</text>
              </view>
              <view class="customer-info">
                <view class="customer-name-row">
                  <text class="customer-name">{{ customer.name }}</text>
                  <view :class="['level-badge', 'level-' + customer.level]">
                    {{ customer.level }}类
                  </view>
                </view>
                <text class="customer-phone">{{ customer.phone || '暂无手机' }}</text>
              </view>
              <view class="customer-arrow">›</view>
            </view>

            <view class="customer-tags">
              <text v-for="tag in customer.tags" :key="tag" class="tag">
                {{ tag }}
              </text>
            </view>

            <view class="customer-footer">
              <view class="customer-needs">
                <text class="needs-label">需求：</text>
                <text class="needs-text">{{ customer.needs.join(', ') }}</text>
              </view>
              <view v-if="customer.nextFollowupAt" class="followup-reminder">
                <text class="reminder-icon">⏰</text>
                <text class="reminder-text">{{ formatFollowupTime(customer.nextFollowupAt) }}</text>
              </view>
            </view>
          </view>
        </view>
      </template>
    </UiState>

    <!-- 底部占位 -->
    <view class="bottom-placeholder"></view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import UiState from '@/src/components/UiState.vue'
import { useCustomerStore } from '@/src/stores/customer'

const store = useCustomerStore()

// 搜索和筛选
const searchText = ref('')
const filterLevel = ref<string>('all')

// UI 状态
const uiState = computed(() => store.state)
const loadingText = ref('正在加载客户列表...')
const emptyTitle = ref('暂无客户数据')
const emptyDescription = ref('导入客户名单或手动添加客户，开始构建您的客户池')
const actionText = ref('导入客户')
const errorMessage = computed(() => store.errorMessage || '加载失败')

// 处理搜索
const handleSearch = () => {
  store.setSearchText(searchText.value)
}

// 添加客户
const handleAddCustomer = () => {
  uni.showToast({
    title: '添加客户功能即将上线',
    icon: 'none'
  })
}

// 导入客户
const handleImport = () => {
  uni.chooseMessageFile({
    count: 1,
    type: 'file',
    extension: ['xlsx', 'xls', 'csv'],
    success: (res) => {
      const file = res.tempFiles[0]
      // TODO: 调用导入 API
      console.log('Import file:', file)
      uni.showToast({
        title: '导入功能开发中',
        icon: 'none'
      })
    }
  })
}

// 加载客户
const loadCustomers = async () => {
  await store.loadCustomers()
}

// 格式化跟进时间
const formatFollowupTime = (time: string) => {
  const date = new Date(time)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))

  if (days <= 0) return '今日待跟进'
  if (days === 1) return '明天待跟进'
  if (days <= 7) return `${days}天后待跟进`
  return `${date.getMonth() + 1}/${date.getDate()}待跟进`
}

// 跳转详情
const goToDetail = (id: string) => {
  uni.showToast({
    title: '客户详情页开发中',
    icon: 'none'
  })
}

onMounted(() => {
  loadCustomers()
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';
@import '../../styles/mixins.scss';

.customer-page {
  min-height: 100vh;
  background: $bg-color-page;
  padding: $spacing-4;
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

// 搜索栏
.search-bar {
  @include flex(row, space-between, center);
  gap: $spacing-3;
  margin-bottom: $spacing-3;

  .search-input-wrapper {
    flex: 1;
    @include flex(row, flex-start, center);
    gap: $spacing-2;
    padding: 10px 16px;
    background: $bg-color-page;
    border: 1px solid $border-color;
    border-radius: $radius-md;

    .search-icon {
      font-size: 18px;
    }

    .search-input {
      flex: 1;
      font-size: $font-size-base;
      color: $text-color-primary;
    }
  }

  .add-btn {
    width: 44px;
    height: 44px;
    @include flex-center;
    background: $color-primary;
    border-radius: $radius-md;
    border: none;

    .add-icon {
      font-size: 24px;
      color: white;
    }
  }
}

// 筛选栏
.filter-bar {
  margin-bottom: $spacing-3;

  .filter-scroll {
    white-space: nowrap;
  }

  .filter-chip {
    display: inline-block;
    padding: 8px 16px;
    margin-right: $spacing-2;
    background: white;
    border: 1px solid $border-color;
    border-radius: $radius-full;
    font-size: $font-size-sm;
    color: $text-color-secondary;
    transition: all $transition-normal;

    &.active {
      background: $color-primary;
      color: white;
      border-color: $color-primary;
    }
  }
}

// 统计卡片
.stats-card {
  margin-bottom: $spacing-4;

  .stats-row {
    @include flex(row, space-between, center);
  }

  .stat-item {
    flex: 1;
    @include flex(column, center, center);
    gap: $spacing-1;

    .stat-value {
      font-size: 20px;
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

// 客户列表
.customer-list {
  @include flex(column, flex-start, stretch);
  gap: $spacing-3;
}

.customer-card {
  @include card;

  .customer-header {
    @include flex(row, flex-start, center);
    gap: $spacing-3;
    margin-bottom: $spacing-3;

    .customer-avatar {
      width: 48px;
      height: 48px;
      @include flex-center;
      background: $color-primary-bg;
      border-radius: 50%;
      font-size: 20px;
      font-weight: 600;
      color: $color-primary;
      flex-shrink: 0;
    }

    .customer-info {
      flex: 1;
      @include flex(column, flex-start, flex-start);
      gap: 4px;
    }

    .customer-name-row {
      @include flex(row, flex-start, center);
      gap: $spacing-2;

      .customer-name {
        font-size: $font-size-base;
        font-weight: 600;
        color: $text-color-primary;
      }

      .level-badge {
        padding: 2px 8px;
        border-radius: $radius-full;
        font-size: 11px;
        font-weight: 600;

        &.level-A { background: #fee2e2; color: #991b1b; }
        &.level-B { background: #fef3c7; color: #92400e; }
        &.level-C { background: #dbeafe; color: #1e40af; }
        &.level-D { background: #e2e8f0; color: #475569; }
      }
    }

    .customer-phone {
      font-size: $font-size-sm;
      color: $text-color-secondary;
    }

    .customer-arrow {
      font-size: 24px;
      color: $text-color-tertiary;
    }
  }

  .customer-tags {
    @include flex(row, flex-start, center);
    flex-wrap: wrap;
    gap: $spacing-2;
    margin-bottom: $spacing-3;
    padding-bottom: $spacing-3;
    border-bottom: 1px solid $border-color-light;

    .tag {
      font-size: $font-size-xs;
      color: $text-color-secondary;
      background: $bg-color-page;
      padding: 4px 10px;
      border-radius: $radius-full;
    }
  }

  .customer-footer {
    @include flex-between;

    .customer-needs {
      flex: 1;

      .needs-label {
        font-size: $font-size-xs;
        color: $text-color-tertiary;
      }

      .needs-text {
        font-size: $font-size-xs;
        color: $text-color-secondary;
      }
    }

    .followup-reminder {
      @include flex(row, flex-start, center);
      gap: $spacing-1;
      padding: 4px 10px;
      background: $color-warning-bg;
      border-radius: $radius-full;

      .reminder-icon {
        font-size: 12px;
      }

      .reminder-text {
        font-size: $font-size-xs;
        color: $color-warning-dark;
      }
    }
  }
}

// 底部占位
.bottom-placeholder {
  height: 80px;
}

// 输入框占位符
.input-placeholder {
  color: $text-color-placeholder;
}
</style>
