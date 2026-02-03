// // src/utils/request.ts
// import axios from 'axios'
// import axiosRetry from 'axios-retry'
// import type { AxiosInstance, AxiosRequestConfig } from 'axios'
// import { message } from 'ant-design-vue'

// // 创建 axios 实例
// const request: AxiosInstance = axios.create({
//   baseURL: import.meta.env.VITE_API_BASE_URL || '/api',  // 基础URL
//   timeout: 120000,  // 120秒超时
//   headers: {
//     'Content-Type': 'application/json'
//   }
// })

// // ==================== 配置自动重试 ====================
// axiosRetry(request, {
//   retries: 2,  // 失败后重试2次（共3次请求）
//   retryDelay: axiosRetry.exponentialDelay,  // 指数退避：第一次等1秒，第二次等2秒
//   retryCondition: (error) => {
//     // 满足以下条件时重试：
//     return (
//       axiosRetry.isNetworkOrIdempotentRequestError(error) ||  // 网络错误或幂等请求（GET/HEAD/PUT/DELETE/OPTIONS）
//       error.response?.status === 503  // 服务不可用
//     )
//   }
// })

// // ==================== 请求拦截器 ====================
// request.interceptors.request.use(
//   (config) => {
//     // 在发送请求前可以做些什么
//     console.log('📤 发送请求:', config.url, config.data)
    
//     // 可以在这里添加 token
//     // const token = localStorage.getItem('token')
//     // if (token) {
//     //   config.headers.Authorization = `Bearer ${token}`
//     // }
    
//     return config
//   },
//   (error) => {
//     // 请求错误处理
//     console.error('❌ 请求错误:', error)
//     return Promise.reject(error)
//   }
// )

// // ==================== 响应拦截器 ====================
// request.interceptors.response.use(
//   (response) => {
//     // 对响应数据做点什么
//     console.log('📥 收到响应:', response.config.url, response.data)
//     return response.data  // 直接返回 data，调用时不用 .data
//   },
//   (error) => {
//     // 响应错误处理
//     console.error('❌ 响应错误:', error)
    
//     // 统一错误提示
//     if (error.response) {
//       // 服务器返回了响应
//       const status = error.response.status
//       const msg = error.response.data?.detail || error.response.data?.message
      
//       switch (status) {
//         case 400:
//           message.error(`❌ 参数错误: ${msg}`)
//           break
//         case 401:
//           message.error('❌ 未授权，请重新登录')
//           // 可以跳转到登录页
//           // router.push('/login')
//           break
//         case 403:
//           message.error('❌ 无权限访问')
//           break
//         case 404:
//           message.error('❌ 请求的资源不存在')
//           break
//         case 500:
//           message.error(`❌ 服务器错误: ${msg || '请稍后重试'}`)
//           break
//         default:
//           message.error(`❌ 请求失败 (${status}): ${msg}`)
//       }
//     } else if (error.request) {
//       // 请求已发送但没有收到响应（网络问题）
//       message.error('❌ 网络连接失败，请检查网络或后端服务')
//     } else {
//       // 其他错误
//       message.error(`❌ ${error.message}`)
//     }
    
//     return Promise.reject(error)
//   }
// )

// export default request