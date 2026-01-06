// Глобальні змінні для графіків
let charts = {};
let currentYear = null;
let currentSemester = '1';
let currentClass = null;

// Ініціалізація при завантаженні сторінки
document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    setupEventListeners();
});

// Ініціалізація фільтрів
function initializeFilters() {
    const yearFilter = document.getElementById('yearFilter');
    const semesterFilter = document.getElementById('semesterFilter');
    
    // Автоматично вибрати перший рік якщо доступний
    if (yearFilter.options.length > 1) {
        yearFilter.selectedIndex = 1;
        currentYear = yearFilter.value;
    }
    
    currentSemester = semesterFilter.value;
    
    // Завантажити класи для вибраного року
    if (currentYear) {
        loadClasses(currentYear);
    }
}

// Налаштування обробників подій
function setupEventListeners() {
    document.getElementById('applyFilters').addEventListener('click', applyFilters);
    document.getElementById('resetFilters').addEventListener('click', resetFilters);
    document.getElementById('yearFilter').addEventListener('change', function() {
        loadClasses(this.value);
    });
}

// Завантажити список класів
async function loadClasses(year) {
    const classFilter = document.getElementById('classFilter');
    classFilter.innerHTML = '<option value="">Всі класи</option>';
    
    if (!year) return;
    
    try {
        const response = await fetch(`/get_classes/${year}`);
        const classes = await response.json();
        
        classes.forEach(className => {
            const option = document.createElement('option');
            option.value = className;
            option.textContent = className;
            classFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading classes:', error);
    }
}

// Застосувати фільтри
async function applyFilters() {
    const yearFilter = document.getElementById('yearFilter');
    const semesterFilter = document.getElementById('semesterFilter');
    const classFilter = document.getElementById('classFilter');
    
    currentYear = yearFilter.value;
    currentSemester = semesterFilter.value;
    currentClass = classFilter.value || null;
    
    if (!currentYear) {
        alert('Будь ласка, оберіть навчальний рік');
        return;
    }
    
    // Показати індикатор завантаження
    showLoading();
    
    try {
        // Завантажити всі дані паралельно
        await Promise.all([
            loadClassComparison(),
            loadLevelDistribution(),
            loadSubjectAnalysis(),
            loadSemesterComparison(),
            loadTopBottom()
        ]);
        
        // Показати графіки
        hideLoading();
        document.getElementById('chartsContainer').style.display = 'block';
    } catch (error) {
        console.error('Error loading data:', error);
        hideLoading();
        alert('Помилка завантаження даних. Спробуйте ще раз.');
    }
}

// Скинути фільтри
function resetFilters() {
    document.getElementById('yearFilter').selectedIndex = 0;
    document.getElementById('semesterFilter').selectedIndex = 0;
    document.getElementById('classFilter').selectedIndex = 0;
    document.getElementById('chartsContainer').style.display = 'none';
    
    // Знищити всі графіки
    Object.values(charts).forEach(chart => {
        if (chart) chart.destroy();
    });
    charts = {};
}

// Показати індикатор завантаження
function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('chartsContainer').style.display = 'none';
}

// Приховати індикатор завантаження
function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

// ==================== ГРАФІКИ ====================

// 1. Порівняння класів по середньому балу
async function loadClassComparison() {
    const response = await fetch(`/api/analytics/class-comparison/${currentYear}/${currentSemester}`);
    const data = await response.json();
    
    if (!data || data.length === 0) {
        console.warn('No class comparison data');
        return;
    }
    
    const ctx = document.getElementById('classComparisonChart').getContext('2d');
    
    // Знищити попередній графік якщо існує
    if (charts.classComparison) {
        charts.classComparison.destroy();
    }
    
    charts.classComparison = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.class),
            datasets: [{
                label: 'Середній бал',
                data: data.map(item => item.avg_score),
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Середній бал: ${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 12,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
    
    // Також використати ці дані для графіка КЯЗ та КР
    loadQualityChart(data);
}

// 2. Розподіл по рівнях (кругова діаграма)
async function loadLevelDistribution() {
    const url = currentClass 
        ? `/api/analytics/level-distribution/${currentYear}/${currentSemester}?class=${currentClass}`
        : `/api/analytics/level-distribution/${currentYear}/${currentSemester}`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    const ctx = document.getElementById('levelDistributionChart').getContext('2d');
    
    if (charts.levelDistribution) {
        charts.levelDistribution.destroy();
    }
    
    charts.levelDistribution = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Високий рівень', 'Достатній рівень', 'Середній рівень', 'Початковий рівень'],
            datasets: [{
                data: [
                    data.high,
                    data.sufficient,
                    data.average,
                    data.initial
                ],
                backgroundColor: [
                    'rgba(76, 175, 80, 0.8)',   // Зелений
                    'rgba(255, 193, 7, 0.8)',   // Жовтий
                    'rgba(255, 152, 0, 0.8)',   // Оранжевий
                    'rgba(244, 67, 54, 0.8)'    // Червоний
                ],
                borderColor: [
                    'rgba(76, 175, 80, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(255, 152, 0, 1)',
                    'rgba(244, 67, 54, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} учнів (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// 3. Аналіз по предметах (горизонтальна діаграма)
async function loadSubjectAnalysis() {
    const response = await fetch(`/api/analytics/subject-analysis/${currentYear}/${currentSemester}`);
    const data = await response.json();
    
    if (!data || data.length === 0) {
        console.warn('No subject analysis data');
        return;
    }
    
    // Взяти топ-15 предметів
    const topSubjects = data.slice(0, 15);
    
    const ctx = document.getElementById('subjectAnalysisChart').getContext('2d');
    
    if (charts.subjectAnalysis) {
        charts.subjectAnalysis.destroy();
    }
    
    charts.subjectAnalysis = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topSubjects.map(item => item.subject),
            datasets: [{
                label: 'Середній бал',
                data: topSubjects.map(item => item.avg_score),
                backgroundColor: 'rgba(156, 39, 176, 0.8)',
                borderColor: 'rgba(156, 39, 176, 1)',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Середній бал: ${context.parsed.x.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 12,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// 4. КЯЗ та КР по класах (лінійна діаграма)
function loadQualityChart(classData) {
    const ctx = document.getElementById('qualityChart').getContext('2d');
    
    if (charts.quality) {
        charts.quality.destroy();
    }
    
    charts.quality = new Chart(ctx, {
        type: 'line',
        data: {
            labels: classData.map(item => item.class),
            datasets: [
                {
                    label: 'КЯЗ (%)',
                    data: classData.map(item => item.avg_quality),
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'КР (%)',
                    data: classData.map(item => item.avg_result),
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 15,
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// 5. Порівняння семестрів
async function loadSemesterComparison() {
    const url = currentClass 
        ? `/api/analytics/semester-comparison/${currentYear}?class=${currentClass}`
        : `/api/analytics/semester-comparison/${currentYear}`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    const ctx = document.getElementById('semesterComparisonChart').getContext('2d');
    
    if (charts.semesterComparison) {
        charts.semesterComparison.destroy();
    }
    
    charts.semesterComparison = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['I семестр', 'II семестр'],
            datasets: [{
                label: 'Середній бал',
                data: [
                    data.semester1.avg_score,
                    data.semester2.avg_score
                ],
                backgroundColor: [
                    'rgba(33, 150, 243, 0.8)',
                    'rgba(76, 175, 80, 0.8)'
                ],
                borderColor: [
                    'rgba(33, 150, 243, 1)',
                    'rgba(76, 175, 80, 1)'
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label;
                            const value = context.parsed.y;
                            const recordsCount = label === 'I семестр' 
                                ? data.semester1.records_count 
                                : data.semester2.records_count;
                            return [
                                `Середній бал: ${value.toFixed(2)}`,
                                `Записів: ${recordsCount}`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 12,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// 6. Топ та аутсайдери
async function loadTopBottom() {
    const response = await fetch(`/api/analytics/top-bottom/${currentYear}/${currentSemester}?limit=5`);
    const data = await response.json();
    
    // Топ-5 класів
    const topList = document.getElementById('topClassesList');
    topList.innerHTML = '';
    
    if (data.top && data.top.length > 0) {
        data.top.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'stat-item';
            li.innerHTML = `
                <span class="stat-name">${index + 1}. ${item.class}</span>
                <span class="stat-value">${item.avg_score.toFixed(2)}</span>
            `;
            topList.appendChild(li);
        });
    } else {
        topList.innerHTML = '<li class="stat-item"><span class="stat-name">Немає даних</span></li>';
    }
    
    // Аутсайдери
    const bottomList = document.getElementById('bottomClassesList');
    bottomList.innerHTML = '';
    
    if (data.bottom && data.bottom.length > 0) {
        data.bottom.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'stat-item';
            
            // Визначити бейдж
            let badge = 'badge-warning';
            if (item.avg_score < 7) {
                badge = 'badge-danger';
            }
            
            li.innerHTML = `
                <span class="stat-name">${item.class}</span>
                <span class="stat-badge ${badge}">${item.avg_score.toFixed(2)}</span>
            `;
            bottomList.appendChild(li);
        });
    } else {
        bottomList.innerHTML = '<li class="stat-item"><span class="stat-name">Немає даних</span></li>';
    }
    
    // Загальна статистика
    if (data.top && data.top.length > 0) {
        const allClasses = [...data.top, ...data.bottom];
        const avgScore = allClasses.reduce((sum, item) => sum + item.avg_score, 0) / allClasses.length;
        const avgQuality = allClasses.reduce((sum, item) => sum + item.avg_quality, 0) / allClasses.length;
        const avgResult = allClasses.reduce((sum, item) => sum + item.avg_result, 0) / allClasses.length;
        
        document.getElementById('overallAvgScore').textContent = avgScore.toFixed(2);
        document.getElementById('overallQuality').textContent = avgQuality.toFixed(1) + '%';
        document.getElementById('overallResult').textContent = avgResult.toFixed(1) + '%';
    }
}

// ==================== ЕКСПОРТ ====================

function exportChart(chartId) {
    const canvas = document.getElementById(chartId);
    
    if (!canvas) {
        alert('Графік не знайдено');
        return;
    }
    
    // Конвертувати canvas в зображення
    const url = canvas.toDataURL('image/png');
    
    // Створити посилання для завантаження
    const link = document.createElement('a');
    link.download = `${chartId}_${currentYear}_${currentSemester}.png`;
    link.href = url;
    link.click();
}

// ==================== ДОПОМІЖНІ ФУНКЦІЇ ====================

function showMessage(message, type = 'info') {
    alert(message);
}