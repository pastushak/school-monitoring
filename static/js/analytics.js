// Глобальні змінні для графіків
let charts = {};
let classComparisonChart = null;
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
    
    showLoading();
    
    try {
        if (currentClass) {
            // ✅ РЕЖИМ: Конкретний клас
            await loadClassDetailedView();
        } else {
            // ✅ РЕЖИМ: Всі класи
            await loadSchoolOverview();
        }
        
        hideLoading();
        document.getElementById('chartsContainer').style.display = 'block';
    } catch (error) {
        console.error('Error loading data:', error);
        hideLoading();
        alert('Помилка завантаження даних. Спробуйте ще раз.');
    }
}

// Завантажити огляд по школі (всі класи)
async function loadSchoolOverview() {
    // Приховати графіки для конкретного класу
    document.getElementById('classSpecificCharts').style.display = 'none';
    
    // Завантажити загальні графіки
    await Promise.all([
        loadClassComparison(),
        loadLevelDistribution(),
        loadSubjectAnalysis(),
        loadSemesterComparison(),
        loadTopBottom()
    ]);
}

// Завантажити детальну аналітику для конкретного класу
async function loadClassDetailedView() {
    // Показати секцію для конкретного класу
    document.getElementById('classSpecificCharts').style.display = 'block';
    document.getElementById('selectedClassName').textContent = currentClass;
    
    // Завантажити загальні графіки (але з даними тільки цього класу)
    await Promise.all([
        loadClassComparison(),           // Середній бал по класах (буде тільки 1 клас)
        loadLevelDistribution(),          // Розподіл рівнів цього класу
        loadClassSubjects(),              // ✅ НОВИЙ: Предмети класу
        loadClassQuality(),               // ✅ НОВИЙ: КЯЗ по предметах
        loadClassResult(),                // ✅ НОВИЙ: КР по предметах
        loadClassTeachers(),              // ✅ НОВИЙ: Порівняння вчителів
        loadClassDynamics(),              // ✅ НОВИЙ: Динаміка класу
        loadParallelClasses(),            // ✅ НОВИЙ: Порівняння з паралелями
        loadClassTopBottom(),             // ✅ НОВИЙ: Топ предметів
        loadClassDetailedTable()          // ✅ НОВИЙ: Детальна таблиця
    ]);
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
    try {
        const response = await fetch(`/api/analytics/class-comparison/${currentYear}/${currentSemester}`);
        const data = await response.json();
        
        if (!data || data.length === 0) {
            document.getElementById('classComparisonChart').style.display = 'none';
            return;
        }
        
        // ✅ Розрахувати середній бал по ліцею
        const averageScore = data.reduce((sum, item) => sum + item.avg_score, 0) / data.length;
        
        const ctx = document.getElementById('classComparisonChart').getContext('2d');
        
        // ✅ Визначити колір для кожного класу
        const backgroundColors = data.map(item => 
            item.avg_score >= averageScore 
                ? 'rgba(34, 197, 94, 0.8)'    // Зелений - вище середнього
                : 'rgba(251, 146, 60, 0.8)'   // Помаранчевий - нижче середнього
        );
        
        const borderColors = data.map(item => 
            item.avg_score >= averageScore 
                ? 'rgba(34, 197, 94, 1)'
                : 'rgba(251, 146, 60, 1)'
        );
        
        // Знищити попередній графік
        if (classComparisonChart) {
            classComparisonChart.destroy();
        }
        
        classComparisonChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.class),
                datasets: [
                    {
                        label: 'Середній бал',
                        data: data.map(item => item.avg_score),
                        backgroundColor: backgroundColors,
                        borderColor: borderColors,
                        borderWidth: 2
                    }
                    // ❌ БЕЗ лінійного датасету - малюємо вручну
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            generateLabels: function(chart) {
                                // ✅ Створити custom legend
                                return [
                                    {
                                        text: `Середній по ліцею: ${averageScore.toFixed(2)}`,
                                        fillStyle: 'rgb(220, 38, 38)',
                                        strokeStyle: 'rgb(220, 38, 38)',
                                        lineWidth: 1,
                                        lineDash: [10, 5],
                                        hidden: false
                                    }
                                ];
                            },
                            usePointStyle: true,
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y.toFixed(2);
                                const diff = (context.parsed.y - averageScore).toFixed(2);
                                const sign = diff >= 0 ? '+' : '';
                                return [
                                    `Середній бал: ${value}`,
                                    `Відхилення: ${sign}${diff}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 12,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Середній бал'
                        }
                    },
                    x: {
                        offset: true,
                        grid: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Класи'
                        }
                    }
                }
            },
            plugins: [{
                // ✅ ДОДАТИ: Малювати червону лінію вручну
                id: 'averageScoreLine',
                afterDatasetsDraw: function(chart) {
                    const ctx = chart.ctx;
                    const xAxis = chart.scales.x;
                    const yAxis = chart.scales.y;
                    
                    // Розрахувати Y позицію для середнього балу
                    const yPos = yAxis.getPixelForValue(averageScore);
                    
                    // Малювати червону пунктирну лінію
                    ctx.save();
                    ctx.strokeStyle = 'rgb(220, 38, 38)';
                    ctx.lineWidth = 1;
                    ctx.setLineDash([10, 5]);
                    
                    ctx.beginPath();
                    ctx.moveTo(xAxis.left, yPos);   // ✅ Від самого лівого краю
                    ctx.lineTo(xAxis.right, yPos);  // ✅ До самого правого краю
                    ctx.stroke();
                    
                    ctx.restore();
                }
            }]
        });
    } catch (error) {
        console.error('Error loading class comparison:', error);
    }
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
                            const percent = context.parsed || 0;
                            
                            // ✅ ДОДАТИ: Абсолютна кількість
                            const counts = {
                                'Високий рівень': data.high_count || 0,
                                'Достатній рівень': data.sufficient_count || 0,
                                'Середній рівень': data.average_count || 0,
                                'Початковий рівень': data.initial_count || 0
                            };
                            
                            const count = counts[label];
                            const countText = count === 1 ? 'результат' : (count < 5 ? 'результати' : 'результатів');
                            
                            const lines = [
                                `${label}`,
                                `${percent.toFixed(1)}% (${count} ${countText})`
                            ];
                            
                            // ✅ ДОДАТИ: Для початкового рівня - показати деталі
                            if (label === 'Початковий рівень' && data.initial_details && data.initial_details.length > 0) {
                                lines.push('');
                                lines.push('⚠️ Потребує уваги:');
                                
                                data.initial_details.slice(0, 12).forEach(item => {
                                    const studentText = item.count === 1 ? 'учень' : (item.count < 5 ? 'учні' : 'учнів');
                                    lines.push(`• ${item.class} ${item.subject} (${item.count} ${studentText})`);
                                });
                                
                                if (data.initial_details.length > 12) {
                                    lines.push(`... та ще ${data.initial_details.length - 5}`);
                                }
                            }
                            
                            return lines;
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
    
    const allSubjects = data;
    const canvas = document.getElementById('subjectAnalysisChart');
    const container = document.getElementById('subjectAnalysisContainer');
    const ctx = canvas.getContext('2d');
    
    if (charts.subjectAnalysis) {
        charts.subjectAnalysis.destroy();
    }
    
    // ✅ Встановити висоту canvas
    const itemHeight = 35;
    const totalHeight = allSubjects.length * itemHeight;
    canvas.style.height = `${totalHeight}px`;
    container.style.height = `${totalHeight}px`;
    
    charts.subjectAnalysis = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: allSubjects.map(item => item.subject),
            datasets: [{
                label: 'Середній бал',
                data: allSubjects.map(item => item.avg_score),
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
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return allSubjects[context[0].dataIndex].subject;
                        },
                        label: function(context) {
                            const item = allSubjects[context.dataIndex];
                            return [
                                `Середній бал: ${item.avg_score.toFixed(2)}`,
                                `Класи: ${item.classes.join(', ')}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 12,
                    grid: { color: 'rgba(0, 0, 0, 0.05)' }
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 11 } }
                }
            }
        }
    });
}

// 4. КЯЗ та КР по класах (лінійна діаграма)
async function loadQualityChart() {
    try {
        // ✅ ДОДАТИ: Отримати дані самостійно
        const response = await fetch(`/api/analytics/class-comparison/${currentYear}/${currentSemester}`);
        const classData = await response.json();
        
        if (!classData || classData.length === 0) {
            document.getElementById('qualityChart').style.display = 'none';
            return;
        }
        
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
    } catch (error) {
        console.error('Error loading quality chart:', error);
    }
}

async function loadSchoolOverview() {
    // Приховати графіки для конкретного класу
    document.getElementById('classSpecificCharts').style.display = 'none';
    
    // Завантажити загальні графіки
    await Promise.all([
        loadClassComparison(),
        loadLevelDistribution(),
        loadSubjectAnalysis(),
        loadQualityChart(),        // ✅ ДОДАТИ ЦЕЙ РЯДОК
        loadSemesterComparison(),
        loadTopBottom()
    ]);
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
    
    // ✅ ДОДАТИ: Перевірка чи є дані для обох семестрів
    const hasSemester1 = data.semester1.records_count > 0;
    const hasSemester2 = data.semester2.records_count > 0;
    
    if (!hasSemester1 || !hasSemester2) {
        // ✅ ПОКАЗАТИ ПОВІДОМЛЕННЯ замість графіка
        const chartContainer = ctx.canvas.parentElement;
        chartContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; color: #64748b;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
                <h3 style="margin: 0; color: #1e293b;">Відсутні дані для порівняння</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem;">
                    Для порівняння семестрів потрібні дані з обох семестрів
                </p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.7;">
                    I семестр: ${hasSemester1 ? '✓ Є дані' : '✗ Немає даних'} | 
                    II семестр: ${hasSemester2 ? '✓ Є дані' : '✗ Немає даних'}
                </p>
            </div>
        `;
        return;
    }
    
    // ✅ Якщо є дані - показати графік
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

// ==================== ГРАФІКИ ДЛЯ КОНКРЕТНОГО КЛАСУ ====================

// 1. Середній бал по предметах класу
async function loadClassSubjects() {
    const response = await fetch(`/api/analytics/class-subjects/${currentYear}/${currentSemester}/${currentClass}`);
    const data = await response.json();
    
    if (!data || data.length === 0) {
        console.warn('No class subjects data');
        return;
    }
    
    // Оновити основний графік "Середній бал по класах" для показу предметів
    const ctx = document.getElementById('classComparisonChart').getContext('2d');
    
    if (charts.classComparison) {
        charts.classComparison.destroy();
    }
    
    // Динамічна висота для багатьох предметів
    const canvas = document.getElementById('classComparisonChart');
    const container = canvas.parentElement;
    const itemHeight = 35;
    const totalHeight = Math.max(400, data.length * itemHeight);
    
    canvas.style.height = `${totalHeight}px`;
    container.style.height = `${totalHeight}px`;
    container.style.maxHeight = '600px';
    container.style.overflowY = 'auto';
    
    charts.classComparison = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.subject),
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
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: `Середній бал по предметах (${currentClass})`,
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#667eea'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const item = data[context.dataIndex];
                            return [
                                `Середній бал: ${item.avg_score.toFixed(2)}`,
                                `Вчитель: ${item.teacher}`,
                                `Учнів: ${item.student_count}`
                            ];
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
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// 2. КЯЗ по предметах класу
async function loadClassQuality() {
    const response = await fetch(`/api/analytics/class-quality/${currentYear}/${currentSemester}/${currentClass}`);
    const data = await response.json();
    
    if (!data || data.length === 0) {
        console.warn('No class quality data');
        return;
    }
    
    const canvas = document.getElementById('classQualityChart');
    const container = document.getElementById('classQualityContainer');
    const ctx = canvas.getContext('2d');
    
    if (charts.classQuality) {
        charts.classQuality.destroy();
    }
    
    // Динамічна висота
    const itemHeight = 35;
    const totalHeight = data.length * itemHeight;
    canvas.style.height = `${totalHeight}px`;
    container.style.height = `${totalHeight}px`;
    
    charts.classQuality = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.subject),
            datasets: [{
                label: 'КЯЗ (%)',
                data: data.map(item => item.quality),
                backgroundColor: 'rgba(255, 99, 132, 0.8)',
                borderColor: 'rgba(255, 99, 132, 1)',
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
                            const item = data[context.dataIndex];
                            return [
                                `КЯЗ: ${item.quality.toFixed(1)}%`,
                                `Вчитель: ${item.teacher}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
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
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// 3. КР по предметах класу
async function loadClassResult() {
    const response = await fetch(`/api/analytics/class-result/${currentYear}/${currentSemester}/${currentClass}`);
    const data = await response.json();
    
    if (!data || data.length === 0) {
        console.warn('No class result data');
        return;
    }
    
    const canvas = document.getElementById('classResultChart');
    const container = document.getElementById('classResultContainer');
    const ctx = canvas.getContext('2d');
    
    if (charts.classResult) {
        charts.classResult.destroy();
    }
    
    // Динамічна висота
    const itemHeight = 35;
    const totalHeight = data.length * itemHeight;
    canvas.style.height = `${totalHeight}px`;
    container.style.height = `${totalHeight}px`;
    
    charts.classResult = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.subject),
            datasets: [{
                label: 'КР (%)',
                data: data.map(item => item.result),
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
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
                            const item = data[context.dataIndex];
                            return [
                                `КР: ${item.result.toFixed(1)}%`,
                                `Вчитель: ${item.teacher}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
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
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// 4. Порівняння вчителів класу (радарна діаграма)
async function loadClassTeachers() {
    const response = await fetch(`/api/analytics/class-teachers/${currentYear}/${currentSemester}/${currentClass}`);
    const data = await response.json();
    
    if (!data || data.length === 0) {
        console.warn('No class teachers data');
        const ctx = document.getElementById('classTeachersChart').getContext('2d');
        const chartContainer = ctx.canvas.parentElement;
        chartContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">👨‍🏫</div>
                <h3 style="margin: 0; color: #1e293b;">Недостатньо даних</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem;">
                    Для порівняння вчителів потрібно більше даних
                </p>
            </div>
        `;
        return;
    }
    
    const ctx = document.getElementById('classTeachersChart').getContext('2d');
    
    if (charts.classTeachers) {
        charts.classTeachers.destroy();
    }
    
    // Підготувати дані для радарної діаграми
    const teachers = data.slice(0, 5); // Максимум 5 вчителів для читабельності
    
    const datasets = teachers.map((teacher, index) => {
        const colors = [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)'
        ];
        
        return {
            label: teacher.teacher,
            data: [
                teacher.avg_score,
                teacher.avg_quality,
                teacher.avg_result
            ],
            backgroundColor: colors[index % colors.length],
            borderColor: colors[index % colors.length].replace('0.6', '1'),
            borderWidth: 2
        };
    });
    
    charts.classTeachers = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Середній бал', 'КЯЗ (%)', 'КР (%)'],
            datasets: datasets
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
                            size: 11
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const teacher = teachers[context.datasetIndex];
                            return `${teacher.teacher}: ${context.parsed.r.toFixed(1)}`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            }
        }
    });
}

// 5. Динаміка класу (I vs II семестр)
async function loadClassDynamics() {
    const response = await fetch(`/api/analytics/class-dynamics/${currentYear}/${currentClass}`);
    const data = await response.json();
    
    const ctx = document.getElementById('classDynamicsChart').getContext('2d');
    
    if (charts.classDynamics) {
        charts.classDynamics.destroy();
    }
    
    // Перевірка чи є дані
    const hasSemester1 = data.semester1.count > 0;
    const hasSemester2 = data.semester2.count > 0;
    
    if (!hasSemester1 || !hasSemester2) {
        const chartContainer = ctx.canvas.parentElement;
        chartContainer.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; color: #64748b;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📈</div>
                <h3 style="margin: 0; color: #1e293b;">Відсутні дані для порівняння</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem;">
                    Для порівняння семестрів потрібні дані з обох семестрів
                </p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.7;">
                    I семестр: ${hasSemester1 ? '✓ Є дані' : '✗ Немає даних'} | 
                    II семестр: ${hasSemester2 ? '✓ Є дані' : '✗ Немає даних'}
                </p>
            </div>
        `;
        return;
    }
    
    charts.classDynamics = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Середній бал', 'КЯЗ (%)', 'КР (%)'],
            datasets: [
                {
                    label: 'I семестр',
                    data: [
                        data.semester1.avg_score,
                        data.semester1.avg_quality,
                        data.semester1.avg_result
                    ],
                    backgroundColor: 'rgba(33, 150, 243, 0.8)',
                    borderColor: 'rgba(33, 150, 243, 1)',
                    borderWidth: 2,
                    borderRadius: 8
                },
                {
                    label: 'II семестр',
                    data: [
                        data.semester2.avg_score,
                        data.semester2.avg_quality,
                        data.semester2.avg_result
                    ],
                    backgroundColor: 'rgba(76, 175, 80, 0.8)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 2,
                    borderRadius: 8
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
                        font: {
                            size: 13,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
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

// 6. Порівняння з паралельними класами
async function loadParallelClasses() {
    const response = await fetch(`/api/analytics/parallel-classes/${currentYear}/${currentSemester}/${currentClass}`);
    const data = await response.json();
    
    if (!data || data.length === 0) {
        console.warn('No parallel classes data');
        return;
    }
    
    const ctx = document.getElementById('parallelClassesChart').getContext('2d');
    
    if (charts.parallelClasses) {
        charts.parallelClasses.destroy();
    }
    
    // Виділити поточний клас іншим кольором
    const backgroundColors = data.map(item => 
        item.is_current ? 'rgba(255, 193, 7, 0.8)' : 'rgba(102, 126, 234, 0.8)'
    );
    const borderColors = data.map(item => 
        item.is_current ? 'rgba(255, 193, 7, 1)' : 'rgba(102, 126, 234, 1)'
    );
    
    charts.parallelClasses = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.class),
            datasets: [{
                label: 'Середній бал',
                data: data.map(item => item.avg_score),
                backgroundColor: backgroundColors,
                borderColor: borderColors,
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
                            const item = data[context.dataIndex];
                            return [
                                `Середній бал: ${item.avg_score.toFixed(2)}`,
                                `Предметів: ${item.subjects_count}`,
                                item.is_current ? '⭐ Поточний клас' : ''
                            ].filter(Boolean);
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

// 7. Топ та аутсайдери предметів
async function loadClassTopBottom() {
    const response = await fetch(`/api/analytics/class-top-bottom/${currentYear}/${currentSemester}/${currentClass}?limit=5`);
    const data = await response.json();
    
    // Топ-5 предметів
    const topList = document.getElementById('classTopSubjectsList');
    topList.innerHTML = '';
    
    if (data.top && data.top.length > 0) {
        data.top.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'stat-item';
            li.innerHTML = `
                <span class="stat-name">${index + 1}. ${item.subject}</span>
                <span class="stat-value">${item.avg_score.toFixed(2)}</span>
            `;
            topList.appendChild(li);
        });
    } else {
        topList.innerHTML = '<li class="stat-item"><span class="stat-name">Немає даних</span></li>';
    }
    
    // Аутсайдери
    const bottomList = document.getElementById('classBottomSubjectsList');
    bottomList.innerHTML = '';
    
    if (data.bottom && data.bottom.length > 0) {
        data.bottom.forEach((item) => {
            const li = document.createElement('li');
            li.className = 'stat-item';
            
            let badge = 'badge-warning';
            if (item.avg_score < 7) {
                badge = 'badge-danger';
            }
            
            li.innerHTML = `
                <span class="stat-name">${item.subject}</span>
                <span class="stat-badge ${badge}">${item.avg_score.toFixed(2)}</span>
            `;
            bottomList.appendChild(li);
        });
    } else {
        bottomList.innerHTML = '<li class="stat-item"><span class="stat-name">Немає даних</span></li>';
    }
}

// 8. Детальна таблиця
async function loadClassDetailedTable() {
    const response = await fetch(`/api/analytics/class-detailed/${currentYear}/${currentSemester}/${currentClass}`);
    const data = await response.json();
    
    const tbody = document.querySelector('#classDetailedTable tbody');
    tbody.innerHTML = '';
    
    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="13" style="text-align: center; padding: 2rem; color: #64748b;">
                    Немає даних для відображення
                </td>
            </tr>
        `;
        return;
    }
    
    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="text-align: left;"><strong>${item.subject}</strong></td>
            <td style="text-align: left;">${item.teacher}</td>
            <td>${item.student_count}</td>
            <td><strong>${item.avg_score}</strong></td>
            <td>${item.learning_level}</td>
            <td>${item.quality_coeff}</td>
            <td>${item.quality_percent}</td>
            <td>${item.result_coeff}</td>
            <td>${item.high}</td>
            <td>${item.sufficient}</td>
            <td>${item.average}</td>
            <td>${item.initial}</td>
            <td>${item.not_assessed}</td>
        `;
        tbody.appendChild(row);
    });
}