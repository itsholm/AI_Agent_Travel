// 引入Vue核心库
// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css' // 👈 必须有这一行！

const app = createApp(App)
app.use(Antd)
// 挂载到#app元素
app.mount('#app')
// 创建Vue应用实例
// const app = createApp({
//   // 应用的根组件
//   template: `
//     <div>
//       <h2>🚀 第一步成功！</h2>
//       <p>当前时间: {{ currentTime }}</p>
//     </div>
//   `,
//   data() {
//     return {
//       currentTime: new Date().toLocaleTimeString()
//     }
//   }
// })