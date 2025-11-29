// متغيرات عامة
let charts = {};
let autoRefreshInterval;

// التهيئة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    startAutoRefresh();
    updateServerTime();
});

// تهيئة اللوحة
function initializeDashboard() {
    // إضافة active للنقر على القوائم
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href').substring(1);
            
            // تحديد القسم النشط
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });
    
    // تحميل البيانات الأولية
    refreshAll();
}

// تحديث جميع البيانات
async function refreshAll() {
    showLoading();
    
    try {
        await Promise.all([
            updateStats(),
            fetchRooms(),
            fetchLogs(),
            updateCharts()
        ]);
        
        updateStatusIndicator(true);
    } catch (error) {
        console.error('Error refreshing data:', error);
        updateStatusIndicator(false);
    } finally {
        hideLoading();
    }
}

// تحديث الإحصائيات
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        document.getElementById('uptime').textContent = formatUptime(data.uptime);
        document.getElementById('activeRooms').textContent = data.active_rooms;
        document.getElementById('totalRequests').textContent = data.total_requests;
        document.getElementById('memoryUsage').textContent = data.memory_usage.toFixed(2) + ' MB';
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// جلب الغرف
async function fetchRooms() {
    try {
        const response = await fetch('/room/all');
        const data = await response.json();
        
        const roomsList = document.getElementById('roomsList');
        roomsList.innerHTML = '';
        
        if (data.rooms && Object.keys(data.rooms).length > 0) {
            for (const [roomName, players] of Object.entries(data.rooms)) {
                const roomCard = document.createElement('div');
                roomCard.className = 'room-card';
                roomCard.innerHTML = `
                    <div class="room-header">
                        <h4>${roomName}</h4>
                        <span class="room-status">${players}</span>
                    </div>
                    <div class="room-actions">
                        <button class="btn btn-sm" onclick="joinRoom('${roomName}')">انضم</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteRoom('${roomName}')">حذف</button>
                    </div>
                `;
                roomsList.appendChild(roomCard);
            }
        } else {
            roomsList.innerHTML = '<p class="no-data">لا توجد غرف نشطة</p>';
        }
    } catch (error) {
        console.error('Error fetching rooms:', error);
    }
}

// جلب السجلات
async function fetchLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        const logsTable = document.getElementById('logsTable');
        logsTable.innerHTML = '';
        
        data.logs.slice().reverse().forEach(log => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${formatDate(log.timestamp)}</td>
                <td><span class="method-badge method-${log.method.toLowerCase()}">${log.method}</span></td>
                <td>${log.path}</td>
                <td>${log.ip}</td>
                <td><span class="status-badge">✓</span></td>
            `;
            logsTable.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching logs:', error);
    }
}

// تحديث المخططات
async function updateCharts() {
    // مخطط الطلبات
    const requestsCtx = document.getElementById('requestsChart').getContext('2d');
    
    if (charts.requests) {
        charts.requests.destroy();
    }
    
    charts.requests = new Chart(requestsCtx, {
        type: 'line',
        data: {
            labels: generateTimeLabels(),
            datasets: [{
                label: 'الطلبات',
                data: generateSampleData(),
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// دوال مساعدة
function formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours} س ${minutes} د`;
}

function formatDate(timestamp) {
    return new Date(timestamp).toLocaleString('ar-EG');
}

function generateTimeLabels() {
    return Array.from({length: 12}, (_, i) => `${i * 2}:00`);
}

function generateSampleData() {
    return Array.from({length: 12}, () => Math.floor(Math.random() * 100) + 20);
}

function updateServerTime() {
    const now = new Date();
    document.getElementById('serverTime').textContent = now.toLocaleString('ar-EG');
    setTimeout(updateServerTime, 1000);
}

function updateStatusIndicator(connected) {
    const indicator = document.getElementById('statusIndicator');
    if (connected) {
        indicator.classList.add('connected');
        indicator.title = 'متصل بالسيرفر';
    } else {
        indicator.classList.remove('connected');
        indicator.title = 'غير متصل';
    }
}

function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function startAutoRefresh() {
    autoRefreshInterval = setInterval(refreshAll, 30000); // كل 30 ثانية
}

// دوال MCS
async function updatePopup() {
    const popupData = {
        image_path: document.getElementById('popupImage').value,
        text: document.getElementById('popupText').value,
        status: document.getElementById('popupStatus').value
    };
    
    try {
        const response = await fetch('/mcs/popup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(popupData)
        });
        
        if (response.ok) {
            alert('تم تحديث النافذة المنبثقة بنجاح');
        }
    } catch (error) {
        console.error('Error updating popup:', error);
        alert('حدث خطأ أثناء التحديث');
    }
}

// دوال إدارة الغرف
async function deleteRoom(roomName) {
    if (confirm(`هل أنت متأكد من حذف الغرفة "${roomName}"؟`)) {
        try {
            const response = await fetch('/room/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'delete',
                    room_name: roomName
                })
            });
            
            if (response.ok) {
                fetchRooms();
            }
        } catch (error) {
            console.error('Error deleting room:', error);
        }
    }
}

async function createSampleRoom() {
    try {
        const roomName = `room_${Date.now()}`;
        const response = await fetch('/room/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'create',
                room_name: roomName,
                players: '6/1'
            })
        });
        
        if (response.ok) {
            fetchRooms();
        }
    } catch (error) {
        console.error('Error creating room:', error);
    }
}

async function clearAllRooms() {
    if (confirm('هل أنت متأكد من مسح جميع الغرف؟')) {
        try {
            const response = await fetch('/room/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'delete'
                })
            });
            
            if (response.ok) {
                fetchRooms();
            }
        } catch (error) {
            console.error('Error clearing rooms:', error);
        }
    }
}

// دوال التبويبات
function openMcTab(tabName) {
    // إخفاء جميع المحتويات
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // إزالة active من جميع الأزرار
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // إظهار المحتوى المحدد
    document.getElementById(tabName).classList.add('active');
    
    // إضافة active للزر المحدد
    event.target.classList.add('active');
}