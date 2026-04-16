<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useAppStore } from './src/stores/app'

const appStore = useAppStore()

onLaunch(() => {
  console.log('App Launch')
  // 初始化应用状态
  appStore.init()
  // 检查登录状态
  appStore.checkAuth()
})

onShow(() => {
  console.log('App Show')
  // 恢复会话
  appStore.resumeSession()
})

onHide(() => {
  console.log('App Hide')
  // 保存应用状态
  appStore.saveState()
})
</script>

<style lang="scss">
/* 全局样式 */
@import './src/styles/variables.scss';
@import './src/styles/mixins.scss';

/* 重置样式 */
page {
  background-color: $bg-color-page;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, 'Noto Sans SC', sans-serif;
  font-size: 15px;
  line-height: 1.5;
  color: $text-color-primary;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 通用容器 */
.container {
  padding: $spacing-4;
  min-height: 100vh;
  box-sizing: border-box;
}

/* 卡片通用样式 */
.card {
  background: #ffffff;
  border-radius: 12px;
  padding: $spacing-6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid $border-color;
  transition: all 0.2s;
}

/* 按钮通用样式 */
.btn-primary {
  background: $color-primary;
  color: #ffffff;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  border: none;
  transition: all 0.2s;

  &:active {
    background: $color-primary-dark;
    opacity: 0.9;
  }
}

.btn-secondary {
  background: #ffffff;
  color: $text-color-secondary;
  border: 1px solid $border-color;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s;

  &:active {
    background: $bg-color-page;
  }
}

/* 工具类 */
.text-center {
  text-align: center;
}

.text-primary {
  color: $color-primary;
}

.text-success {
  color: $color-success;
}

.text-warning {
  color: $color-warning;
}

.text-danger {
  color: $color-danger;
}

.mt-4 {
  margin-top: $spacing-4;
}

.mb-4 {
  margin-bottom: $spacing-4;
}

.flex {
  display: flex;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.flex-1 {
  flex: 1;
}
</style>
