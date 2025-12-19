// API配置
// 默认使用相对路径（本地开发或与前端同域部署）
// 如果前端和后端分离部署，请修改为完整的后端API地址
const API_CONFIG = {
    // GitHub Pages部署时使用远程后端API
    baseURL: window.location.hostname === 'demouo.github.io'
        ? 'http://47.121.222.197:8000'  // GitHub Pages部署：使用远程后端
        : '',  // 本地开发：使用相对路径
};
