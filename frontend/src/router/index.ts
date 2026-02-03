// // src/router/index.ts
// import { createRouter, createWebHistory } from 'vue-router';
// import type { RouteRecordRaw } from 'vue-router';

// const routes: RouteRecordRaw[] = [
//   { 
//     path: '/', 
//     name: 'Home',
//     component: () => import('../App.vue') 
//   },
//   { 
//     path: '/history', 
//     name: 'History',
//     component: () => import('../views/HistoryPage.vue') 
//   },
//   { 
//     path: '/detail/:id', 
//     name: 'Detail',
//     component: () => import('../views/DetailPage.vue') 
//   }
// ];

// const router = createRouter({
//   history: createWebHistory(),  // 使用 HTML5 History 模式（无 # 号）
//   routes
// });

// export default router;