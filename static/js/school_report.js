document.addEventListener('DOMContentLoaded', function() {
    const yearFilter = document.getElementById('yearFilter');
    const semesterFilter = document.getElementById('semesterFilter');
    const loadReportBtn = document.getElementById('loadReportBtn');
    const progressSection = document.getElementById('progressSection');
    const reportTable = document.getElementById('reportTable');
    const messageDiv = document.getElementById('message');
    
    // Завантаження звіту
    loadReportBtn.addEventListener('click', async function() {
        const year = yearFilter.value;
        const semester = semesterFilter.value;
        
        if (!year) {
            showMessage('Оберіть навчальний рік', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`/get_school_report/${year}`);
            const result = await response.json();
            
            if (!result.classes || Object.keys(result.classes).length === 0) {
                showMessage('Немає даних для відображення', 'warning');
                progressSection.style.display = 'none';
                reportTable.style.display = 'none';
                return;
            }
            
            // Показати загальний прогрес
            progressSection.style.display = 'block';
            document.getElementById('overallProgressFill').style.width = result.overall_progress + '%';
            document.getElementById('overallProgressText').textContent = result.overall_progress + '%';
            document.getElementById('overallFilledCount').textContent = result.overall_filled;
            document.getElementById('overallTotalCount').textContent = result.overall_total;
            
            // Відобразити таблицю
            displayReport(result.classes, semester);
            reportTable.style.display = 'block';
            
            if (result.overall_progress < 100) {
                showMessage(`Заповнено ${result.overall_progress}% по школі`, 'warning');
            } else {
                showMessage('✓ Всі дані заповнені', 'success');
            }
            
        } catch (error) {
            console.error('Error:', error);
            showMessage('Помилка завантаження звіту', 'error');
        }
    });
    
    function displayReport(classesData, semester) {
            const reportTitle = document.getElementById('reportTitle');
            const reportBody = document.getElementById('reportBody');
            
            reportTitle.textContent = `${semester === '1' ? 'I' : 'II'} семестр ${yearFilter.value} н.р.`;
            
            reportBody.innerHTML = '';
            
            // Сортувати класи
            const sortedClasses = Object.keys(classesData).sort((a, b) => {
                const numA = parseInt(a.match(/\d+/)[0]);
                const numB = parseInt(b.match(/\d+/)[0]);
                if (numA !== numB) return numA - numB;
                return a.localeCompare(b);
            });
            
            let totalData = {
                notAssessed: 0,
                initial: 0,
                average: 0,
                sufficient: 0,
                high: 0,
                avgScore: [],
                learningLevel: [],
                qualityCoeff: [],
                qualityPercent: [],
                resultCoeff: [],
                count: 0
            };
            
            sortedClasses.forEach(className => {
                const classInfo = classesData[className];
                const row = document.createElement('tr');
                
                if (classInfo.statistics) {
                    // Визначити текстовий опис СН
                    let snText = '';
                    if (classInfo.statistics.learning_level >= 64) {
                        snText = 'високий ступінь навченості';
                    } else if (classInfo.statistics.learning_level >= 36) {
                        snText = 'достатній ступінь навченості';
                    } else {
                        snText = 'середній ступінь навченості';
                    }
                    
                    row.innerHTML = `
                        <td><strong>${className}</strong></td>
                        <td>${classInfo.statistics.not_assessed}%</td>
                        <td>${classInfo.statistics.initial}%</td>
                        <td>${classInfo.statistics.average}%</td>
                        <td>${classInfo.statistics.sufficient}%</td>
                        <td>${classInfo.statistics.high}%</td>
                        <td>${classInfo.statistics.avg_score}</td>
                        <td>${classInfo.statistics.learning_level}%</td>
                        <td>${snText}</td>
                        <td>${classInfo.statistics.quality_coeff}%</td>
                        <td>${classInfo.statistics.quality_percent}%</td>
                        <td>${classInfo.statistics.result_coeff}%</td>
                        <td>
                            <div class="mini-progress">
                                <div class="mini-progress-fill" style="width: ${classInfo.progress}%"></div>
                            </div>
                            <br><small>${classInfo.progress}%</small>
                        </td>
                    `;
                    
                    // Накопичувати дані для середніх по ліцею
                    totalData.notAssessed += classInfo.statistics.not_assessed;
                    totalData.initial += classInfo.statistics.initial;
                    totalData.average += classInfo.statistics.average;
                    totalData.sufficient += classInfo.statistics.sufficient;
                    totalData.high += classInfo.statistics.high;
                    totalData.avgScore.push(classInfo.statistics.avg_score);
                    totalData.learningLevel.push(classInfo.statistics.learning_level);
                    totalData.qualityCoeff.push(classInfo.statistics.quality_coeff);
                    totalData.qualityPercent.push(classInfo.statistics.quality_percent);
                    totalData.resultCoeff.push(classInfo.statistics.result_coeff);
                    totalData.count++;
                    
                } else {
                    row.innerHTML = `
                        <td><strong>${className}</strong></td>
                        <td colspan="11" class="status-empty" style="text-align: center; font-style: italic; color: #64748b;">Дані не внесені</td>
                        <td>
                            <div class="mini-progress">
                                <div class="mini-progress-fill" style="width: 0%"></div>
                            </div>
                            <br><small>0%</small>
                        </td>
                    `;
                }
                
                reportBody.appendChild(row);
            });
            
            // Додати рядок "середні дані по ліцею"
            if (totalData.count > 0) {
                const avgNotAssessed = (totalData.notAssessed / totalData.count).toFixed(2);
                const avgInitial = (totalData.initial / totalData.count).toFixed(2);
                const avgAverage = (totalData.average / totalData.count).toFixed(2);
                const avgSufficient = (totalData.sufficient / totalData.count).toFixed(2);
                const avgHigh = (totalData.high / totalData.count).toFixed(2);
                const avgScore = (totalData.avgScore.reduce((a, b) => a + b, 0) / totalData.count).toFixed(2);
                const avgLearningLevel = (totalData.learningLevel.reduce((a, b) => a + b, 0) / totalData.count).toFixed(2);
                const avgQualityCoeff = (totalData.qualityCoeff.reduce((a, b) => a + b, 0) / totalData.count).toFixed(2);
                const avgQualityPercent = (totalData.qualityPercent.reduce((a, b) => a + b, 0) / totalData.count).toFixed(2);
                const avgResultCoeff = (totalData.resultCoeff.reduce((a, b) => a + b, 0) / totalData.count).toFixed(2);
                
                // Визначити текст СН для середніх
                let avgSnText = '';
                if (avgLearningLevel >= 64) {
                    avgSnText = 'високий ступінь навченості';
                } else if (avgLearningLevel >= 36) {
                    avgSnText = 'достатній ступінь навченості';
                } else {
                    avgSnText = 'середній ступінь навченості';
                }
                
                const avgRow = document.createElement('tr');
                avgRow.style.background = 'linear-gradient(135deg, #fef3c7, #fde68a)';
                avgRow.style.fontWeight = 'bold';
                avgRow.innerHTML = `
                    <td><strong>середні дані по ліцею</strong></td>
                    <td>${avgNotAssessed}%</td>
                    <td>${avgInitial}%</td>
                    <td>${avgAverage}%</td>
                    <td>${avgSufficient}%</td>
                    <td>${avgHigh}%</td>
                    <td>${avgScore}</td>
                    <td>${avgLearningLevel}%</td>
                    <td>${avgSnText}</td>
                    <td>${avgQualityCoeff}%</td>
                    <td>${avgQualityPercent}%</td>
                    <td>${avgResultCoeff}%</td>
                    <td>
                        <strong>${document.getElementById('overallProgressText').textContent}</strong>
                    </td>
                `;
                reportBody.appendChild(avgRow);
            }
        }
    
    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = 'message ' + type;
        messageDiv.style.display = 'block';
        
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }

    // Експорт в Excel
    const exportBtn = document.getElementById('exportSchoolExcelBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            const year = yearFilter.value;
            const semester = semesterFilter.value;
            
            if (!year) {
                showMessage('Спочатку завантажте звіт', 'warning');
                return;
            }
            
            window.location.href = `/export_school_report/${encodeURIComponent(year)}/${semester}`;
        });
    }

});