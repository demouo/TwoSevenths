// API配置
// 默认使用相对路径（本地开发或与前端同域部署）
// 如果前端和后端分离部署，请修改为完整的后端API地址
const API_CONFIG = {
    // 本地开发或Docker部署时使用相对路径
    baseURL: window.location.hostname === 'demouo.github.io'
        ? 'https://your-backend-api.com'  // GitHub Pages部署时，替换为你的后端API地址
        : '',  // 本地开发或同域部署使用相对路径

    // 或者直接设置为你的后端地址：
    // baseURL: 'https://your-backend-api.com'
};
