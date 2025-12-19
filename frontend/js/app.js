// API基础URL
const API_BASE = '/api';

// 当前用户选择的选项
let currentOption = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initVoteButtons();
    initDanmaku();
    loadStats();
    loadMessages();

    // 定时刷新数据
    setInterval(loadStats, 10000); // 每10秒刷新统计
    setInterval(loadMessages, 5000); // 每5秒刷新弹幕
});

// 初始化投票按钮
function initVoteButtons() {
    const voteButtons = document.querySelectorAll('.vote-btn');

    voteButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const option = btn.dataset.option;
            await submitVote(option);
        });
    });
}

// 提交投票
async function submitVote(option) {
    try {
        const response = await fetch(`${API_BASE}/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ option })
        });

        const data = await response.json();

        if (data.success) {
            currentOption = option;
            alert('投票成功！感谢参与');
            loadStats();
        }
    } catch (error) {
        console.error('投票失败:', error);
        alert('投票失败，请稍后重试');
    }
}

// 加载统计数据
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();

        updateStatsDisplay(data);
        updateChart(data);
    } catch (error) {
        console.error('加载统计失败:', error);
    }
}

// 更新统计显示
function updateStatsDisplay(data) {
    document.getElementById('total-votes').textContent = data.total;

    const options = ['double', 'single', 'alternate'];
    options.forEach(option => {
        const stats = data.options[option];
        document.getElementById(`${option}-percent`).textContent = `${stats.percentage}%`;
        document.getElementById(`${option}-count`).textContent = `${stats.count}人`;
    });
}

// 更新图表
let chartInstance = null;

function updateChart(data) {
    const ctx = document.getElementById('statsChart').getContext('2d');

    const chartData = {
        labels: ['双休', '单休', '大小周'],
        datasets: [{
            label: '投票数量',
            data: [
                data.options.double.count,
                data.options.single.count,
                data.options.alternate.count
            ],
            backgroundColor: [
                'rgba(102, 126, 234, 0.8)',
                'rgba(237, 100, 166, 0.8)',
                'rgba(255, 159, 64, 0.8)'
            ],
            borderColor: [
                'rgba(102, 126, 234, 1)',
                'rgba(237, 100, 166, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 2
        }]
    };

    const config = {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: '各休息模式投票分布',
                    font: {
                        size: 18
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    };

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, config);
}

// 初始化弹幕功能
function initDanmaku() {
    const sendBtn = document.getElementById('send-danmaku-btn');
    const input = document.getElementById('danmaku-input');

    sendBtn.addEventListener('click', () => sendDanmaku());
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendDanmaku();
        }
    });
}

// 发送弹幕
async function sendDanmaku() {
    const input = document.getElementById('danmaku-input');
    const content = input.value.trim();

    if (!content) {
        alert('请输入内容');
        return;
    }

    if (!currentOption) {
        alert('请先选择你的休息模式');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content,
                option: currentOption
            })
        });

        const data = await response.json();

        if (data.success) {
            input.value = '';
            showDanmakuAnimation(content);
            loadMessages();
        }
    } catch (error) {
        console.error('发送弹幕失败:', error);
        alert('发送失败，请稍后重试');
    }
}

// 显示弹幕动画
function showDanmakuAnimation(content) {
    const display = document.getElementById('danmaku-display');
    const item = document.createElement('div');
    item.className = 'danmaku-item';
    item.textContent = content;
    item.style.top = `${Math.random() * 150}px`;

    display.appendChild(item);

    setTimeout(() => {
        item.remove();
    }, 10000);
}

// 加载弹幕列表
async function loadMessages() {
    try {
        const response = await fetch(`${API_BASE}/messages?limit=20`);
        const data = await response.json();

        updateMessagesList(data.messages);
    } catch (error) {
        console.error('加载弹幕失败:', error);
    }
}

// 更新弹幕列表
function updateMessagesList(messages) {
    const list = document.getElementById('danmaku-list');
    list.innerHTML = '';

    const optionLabels = {
        double: '双休',
        single: '单休',
        alternate: '大小周'
    };

    messages.forEach(msg => {
        const card = document.createElement('div');
        card.className = 'message-card';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = msg.content;

        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';

        const optionSpan = document.createElement('span');
        optionSpan.className = 'message-option';
        optionSpan.textContent = optionLabels[msg.option];

        const timeSpan = document.createElement('span');
        timeSpan.textContent = formatTime(msg.timestamp);

        metaDiv.appendChild(optionSpan);
        metaDiv.appendChild(timeSpan);

        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(metaDiv);

        const likeBtn = document.createElement('button');
        likeBtn.className = 'like-btn';
        likeBtn.textContent = `👍 ${msg.likes}`;
        likeBtn.addEventListener('click', () => likeMessage(msg.id));

        card.appendChild(contentDiv);
        card.appendChild(likeBtn);

        list.appendChild(card);
    });
}

// 点赞弹幕
async function likeMessage(messageId) {
    try {
        const response = await fetch(`${API_BASE}/messages/${messageId}/like`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            loadMessages();
        }
    } catch (error) {
        console.error('点赞失败:', error);
    }
}

// 格式化时间
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return '刚刚';
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}天前`;

    return date.toLocaleDateString('zh-CN');
}
