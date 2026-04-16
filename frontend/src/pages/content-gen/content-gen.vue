<!-- 内容生成页面 - 获客内容生成 -->
<template>
  <view class="content-gen-page">
    <!-- 顶部生成器 -->
    <view class="generator-card card">
      <view class="generator-header">
        <text class="generator-title">AI 内容生成</text>
        <text class="generator-desc">选择内容类型，输入产品信息，AI 自动生成高质量获客内容</text>
      </view>

      <!-- 内容类型选择 -->
      <view class="form-section">
        <text class="form-label">内容类型</text>
        <view class="type-selector">
          <view
            v-for="type in contentTypes"
            :key="type.value"
            :class="['type-option', selectedType === type.value ? 'active' : '']"
            @click="selectedType = type.value"
          >
            <text class="type-icon">{{ type.icon }}</text>
            <text class="type-name">{{ type.label }}</text>
          </view>
        </view>
      </view>

      <!-- 产品信息输入 -->
      <view class="form-section">
        <text class="form-label">产品名称 <text class="required">*</text></text>
        <input
          class="form-input"
          v-model="form.productName"
          placeholder="请输入保险产品名称"
          placeholder-class="input-placeholder"
        />
      </view>

      <view class="form-section">
        <text class="form-label">产品类型 <text class="required">*</text></text>
        <picker :range="productTypes" @change="onProductTypeChange" :value="productTypeIndex">
          <view class="form-input form-picker">
            <text>{{ productTypes[productTypeIndex] || '请选择产品类型' }}</text>
            <text class="picker-arrow">›</text>
          </view>
        </picker>
      </view>

      <view class="form-section">
        <text class="form-label">目标客户</text>
        <input
          class="form-input"
          v-model="form.targetAudience"
          placeholder="例如：30-40 岁企业主"
          placeholder-class="input-placeholder"
        />
      </view>

      <view class="form-section">
        <text class="form-label">文案风格</text>
        <view class="tone-selector">
          <view
            v-for="tone in tones"
            :key="tone.value"
            :class="['tone-option', form.tone === tone.value ? 'active' : '']"
            @click="form.tone = tone.value"
          >
            {{ tone.label }}
          </view>
        </view>
      </view>

      <!-- 生成按钮 -->
      <button
        class="generate-btn btn-primary"
        :disabled="generating || !canGenerate"
        @click="handleGenerate"
      >
        <text v-if="generating" class="btn-loading">
          <text class="spinner"></text>
          生成中...
        </text>
        <text v-else>立即生成</text>
      </button>
    </view>

    <!-- UI 状态展示 -->
    <UiState
      :state="uiState"
      :loading-text="loadingText"
      :show-progress="showProgress"
      :progress="progress"
      :empty-title="emptyTitle"
      :empty-description="emptyDescription"
      :show-example="showExample"
      :example-text="exampleText"
      :action-text="actionText"
      :error-title="errorTitle"
      :error-message="errorMessage"
      @action="handleGenerate"
      @retry="handleGenerate"
    >
      <template #content>
        <!-- 生成结果 -->
        <view class="results-section">
          <view class="results-header">
            <text class="results-title">生成结果</text>
            <button class="regenerate-btn" @click="handleGenerate">重新生成</button>
          </view>

          <!-- 文案卡片列表 -->
          <view class="copy-list">
            <view
              v-for="(copy, index) in store.copies"
              :key="copy.id"
              :class="['copy-card', 'card', 'copy-card-' + index]"
            >
              <view class="copy-header">
                <view class="copy-score">
                  <text class="score-icon">⭐</text>
                  <text class="score-value">{{ (copy.score * 100).toFixed(0) }}分</text>
                </view>
                <view class="copy-actions">
                  <button class="action-btn" @click="handleLike(copy.id)">👍</button>
                  <button class="action-btn" @click="handleCopy(copy.content)">📋</button>
                </view>
              </view>

              <view class="copy-content">
                <text class="copy-text">{{ copy.content }}</text>
              </view>

              <view class="copy-footer">
                <view class="hashtags">
                  <text v-for="tag in copy.hashtags" :key="tag" class="hashtag">
                    #{{ tag }}
                  </text>
                </view>
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
import { useContentGenStore } from '@/src/stores/contentGen'

const store = useContentGenStore()

// 内容类型选项
const contentTypes = [
  { value: 'wechat', label: '朋友圈文案', icon: '📱' },
  { value: 'video', label: '短视频脚本', icon: '🎬' },
  { value: 'poster', label: '海报文案', icon: '🖼️' }
]

// 产品类型
const productTypes = ['重疾险', '医疗险', '寿险', '意外险', '年金险', '终身寿险']

// 文案风格
const tones = [
  { value: '专业', label: '专业' },
  { value: '亲和', label: '亲和' },
  { value: '幽默', label: '幽默' },
  { value: '紧迫', label: '紧迫' }
]

// 表单数据
const selectedType = ref<'wechat' | 'video' | 'poster'>('wechat')
const productTypeIndex = ref(0)
const form = ref({
  productName: '',
  targetAudience: '',
  tone: '专业'
})

// UI 状态
const uiState = computed(() => store.state)
const generating = computed(() => store.generating)
const loadingText = ref('AI 正在创作中，预计需要 5-10 秒...')
const showProgress = ref(true)
const progress = ref(0)
const emptyTitle = ref('还没有生成过内容')
const emptyDescription = ref('输入产品信息，AI 自动生成高质量获客内容')
const showExample = ref(true)
const exampleText = ref('例如：输入「健康保」「重疾险」，生成 3 条朋友圈文案')
const actionText = ref('立即生成')
const errorTitle = ref('生成失败')
const errorMessage = computed(() => store.errorMessage || '请稍后重试')

// 是否可以生成
const canGenerate = computed(() => {
  return form.value.productName.trim() !== ''
})

// 模拟进度条
let progressTimer: any = null
const startProgress = () => {
  progress.value = 0
  progressTimer = setInterval(() => {
    progress.value = Math.min(progress.value + 10, 90)
  }, 500)
}

const stopProgress = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
  progress.value = 100
}

// 处理生成
const handleGenerate = async () => {
  if (!canGenerate.value) {
    uni.showToast({
      title: '请填写产品名称',
      icon: 'none'
    })
    return
  }

  startProgress()

  try {
    if (selectedType.value === 'wechat') {
      await store.generateWechatCopywriting({
        productName: form.value.productName,
        productType: productTypes[productTypeIndex.value],
        targetAudience: form.value.targetAudience || undefined,
        tone: form.value.tone,
        count: 3
      })
    } else if (selectedType.value === 'video') {
      await store.generateVideoScript({
        topic: form.value.productName,
        duration: '30s'
      })
    }
    stopProgress()
  } catch (e) {
    stopProgress()
    console.error('Generate failed:', e)
  }
}

// 处理点赞
const handleLike = (id: string) => {
  store.likeCopy(id)
  uni.showToast({
    title: '已点赞',
    icon: 'success'
  })
}

// 处理复制
const handleCopy = (content: string) => {
  uni.setClipboardData({
    data: content,
    success: () => {
      uni.showToast({
        title: '已复制到剪贴板',
        icon: 'success'
      })
    }
  })
}

// 选择产品类型
const onProductTypeChange = (e: any) => {
  productTypeIndex.value = e.detail.value
}

onMounted(() => {
  // 初始化
})
</script>

<style lang="scss" scoped>
@import '../../styles/variables.scss';
@import '../../styles/mixins.scss';

.content-gen-page {
  min-height: 100vh;
  background: $bg-color-page;
  padding: $spacing-4;
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

// 生成器卡片
.generator-card {
  @include card;
  margin-bottom: $spacing-4;

  .generator-header {
    margin-bottom: $spacing-6;

    .generator-title {
      display: block;
      font-size: $font-size-lg;
      font-weight: 600;
      color: $text-color-primary;
      margin-bottom: $spacing-2;
    }

    .generator-desc {
      font-size: $font-size-sm;
      color: $text-color-secondary;
    }
  }
}

// 表单区域
.form-section {
  margin-bottom: $spacing-4;

  .form-label {
    display: block;
    font-size: $font-size-md;
    font-weight: 500;
    color: $text-color-primary;
    margin-bottom: $spacing-2;

    .required {
      color: $color-danger;
    }
  }

  .form-input {
    width: 100%;
    padding: 12px 16px;
    background: $bg-color-page;
    border: 1px solid $border-color;
    border-radius: $radius-md;
    font-size: $font-size-base;
    transition: all $transition-normal;

    &:focus {
      border-color: $color-primary;
      background: $color-white;
    }
  }

  .form-picker {
    @include flex-between;

    .picker-arrow {
      font-size: 18px;
      color: $text-color-tertiary;
    }
  }
}

// 类型选择器
.type-selector {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-2;

  .type-option {
    @include flex(column, center, center);
    gap: $spacing-2;
    padding: $spacing-3;
    background: $bg-color-page;
    border: 1px solid $border-color;
    border-radius: $radius-md;
    transition: all $transition-normal;

    &.active {
      background: $color-primary-bg;
      border-color: $color-primary;
    }

    .type-icon {
      font-size: 24px;
    }

    .type-name {
      font-size: $font-size-xs;
      color: $text-color-secondary;
    }
  }
}

// 风格选择器
.tone-selector {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-2;

  .tone-option {
    padding: 8px 16px;
    background: $bg-color-page;
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

// 生成按钮
.generate-btn {
  width: 100%;
  padding: 14px;
  font-size: $font-size-base;
  font-weight: 600;
  margin-top: $spacing-2;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-loading {
  @include flex(row, center, center);
  gap: $spacing-2;

  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// 结果区域
.results-section {
  margin-top: $spacing-4;

  .results-header {
    @include flex-between;
    margin-bottom: $spacing-4;

    .results-title {
      font-size: $font-size-lg;
      font-weight: 600;
      color: $text-color-primary;
    }

    .regenerate-btn {
      font-size: $font-size-sm;
      color: $color-primary;
      background: transparent;
      border: none;
      padding: 8px 16px;
    }
  }
}

// 文案列表
.copy-list {
  @include flex(column, flex-start, stretch);
  gap: $spacing-3;
}

.copy-card {
  @include card;
  @include fade-in;

  .copy-header {
    @include flex-between;
    margin-bottom: $spacing-3;
    padding-bottom: $spacing-3;
    border-bottom: 1px solid $border-color-light;

    .copy-score {
      @include flex(row, flex-start, center);
      gap: $spacing-1;

      .score-icon {
        font-size: 16px;
      }

      .score-value {
        font-size: $font-size-sm;
        font-weight: 600;
        color: $color-warning;
      }
    }

    .copy-actions {
      @include flex(row, flex-start, center);
      gap: $spacing-2;

      .action-btn {
        font-size: 18px;
        background: transparent;
        border: none;
        padding: 4px;
        opacity: 0.6;
        transition: opacity $transition-normal;

        &:active {
          opacity: 1;
        }
      }
    }
  }

  .copy-content {
    margin-bottom: $spacing-3;

    .copy-text {
      font-size: $font-size-base;
      color: $text-color-primary;
      line-height: 1.6;
      white-space: pre-wrap;
    }
  }

  .copy-footer {
    .hashtags {
      @include flex(row, flex-start, center);
      flex-wrap: wrap;
      gap: $spacing-2;

      .hashtag {
        font-size: $font-size-xs;
        color: $color-primary;
        background: $color-primary-bg;
        padding: 4px 10px;
        border-radius: $radius-full;
      }
    }
  }
}

// 底部占位
.bottom-placeholder {
  height: 80px;
}

// 输入框占位符样式
.input-placeholder {
  color: $text-color-placeholder;
}
</style>
