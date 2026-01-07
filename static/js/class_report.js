document.addEventListener('DOMContentLoaded', function() {
    const yearFilter = document.getElementById('yearFilter');
    const classFilter = document.getElementById('classFilter');
    const semesterFilter = document.getElementById('semesterFilter');
    const loadReportBtn = document.getElementById('loadReportBtn');
    const progressSection = document.getElementById('progressSection');
    const reportTable = document.getElementById('reportTable');
    const messageDiv = document.getElementById('message');
    
    // Активувати вибір класу після вибору року
    yearFilter.addEventListener('change', function() {
        if (this.value) {
            classFilter.disabled = false;
        } else {
            classFilter.disabled = true;
            classFilter.value = '';
        }
        progressSection.style.display = 'none';
        reportTable.style.display = 'none';
    });
    
    // Завантаження звіту
    loadReportBtn.addEventListener('click', async function() {
        const year = yearFilter.value;
        const className = classFilter.value;
        const semester = semesterFilter.value;
        
        if (!year || !className) {
            showMessage('Оберіть навчальний рік та клас', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`/get_class_report/${year}/${className}`);
            const result = await response.json();
            
            if (!result.data || result.data.length === 0) {
                showMessage('Немає даних для відображення', 'warning');
                progressSection.style.display = 'none';
                reportTable.style.display = 'none';
                return;
            }
            
            // Показати прогрес
            progressSection.style.display = 'block';
            document.getElementById('progressFill').style.width = result.progress + '%';
            document.getElementById('progressText').textContent = result.progress + '%';
            document.getElementById('filledCount').textContent = result.filled;
            document.getElementById('totalCount').textContent = result.total;
            
            // Відобразити таблицю
            displayReport(result.data, className, semester);
            reportTable.style.display = 'block';
            
            if (result.filled < result.total) {
                showMessage(`Увага: заповнено ${result.filled} з ${result.total} предметів (${result.progress}%)`, 'warning');
            } else {
                showMessage('✓ Всі предмети заповнені', 'success');
            }
            
        } catch (error) {
            console.error('Error:', error);
            showMessage('Помилка завантаження звіту', 'error');
        }
    });
    
    function displayReport(data, className, semester) {
        const reportTitle = document.getElementById('reportTitle');
        const reportBody = document.getElementById('reportBody');
        
        reportTitle.textContent = `${semester === '1' ? 'I' : 'II'} семестр ${yearFilter.value} н.р. (${className}, узагальнені уточнення)`;
        
        reportBody.innerHTML = '';
        
        let rowNum = 1;
        let totalData = {
            notAssessed: 0,
            initial: 0,
            average: 0,
            sufficient: 0,
            high: 0,
            // ✅ ДОДАТИ: Абсолютні числа
            notAssessedCount: 0,
            initialCount: 0,
            averageCount: 0,
            sufficientCount: 0,
            highCount: 0,
            avgScore: [],
            learningLevel: [],
            qualityCoeff: [],
            qualityPercent: [],
            resultCoeff: [],
            count: 0
        };
        
        data.forEach(item => {
            const row = document.createElement('tr');
            
            if (item.filled) {
                const stats = item.statistics;
                const grades = item.grades;
                const studentCount = item.student_count;
                
                // Розрахунок відсотків по рівнях
                const g3 = parseInt(grades.grade3 || 0);
                const g2 = parseInt(grades.grade2 || 0);
                const g1 = parseInt(grades.grade1 || 0);
                const initialLevel = g3 + g2 + g1;
                const initialPercent = ((initialLevel / studentCount) * 100).toFixed(2);
                
                const g6 = parseInt(grades.grade6 || 0);
                const g5 = parseInt(grades.grade5 || 0);
                const g4 = parseInt(grades.grade4 || 0);
                const averageLevel = g6 + g5 + g4;
                const averagePercent = ((averageLevel / studentCount) * 100).toFixed(2);
                
                const g9 = parseInt(grades.grade9 || 0);
                const g8 = parseInt(grades.grade8 || 0);
                const g7 = parseInt(grades.grade7 || 0);
                const sufficientLevel = g9 + g8 + g7;
                const sufficientPercent = ((sufficientLevel / studentCount) * 100).toFixed(2);
                
                const g12 = parseInt(grades.grade12 || 0);
                const g11 = parseInt(grades.grade11 || 0);
                const g10 = parseInt(grades.grade10 || 0);
                const highLevel = g12 + g11 + g10;
                const highPercent = ((highLevel / studentCount) * 100).toFixed(2);
                
                // Н/А (не атестовані) - учні без оцінок
                const totalGraded = initialLevel + averageLevel + sufficientLevel + highLevel;
                const notAssessed = studentCount - totalGraded;
                const notAssessedPercent = ((notAssessed / studentCount) * 100).toFixed(2);
                
                // СН - визначення текстом
                const learningLevelNum = parseFloat(stats.learningLevel.replace('%', ''));
                let learningLevelText = '';
                if (learningLevelNum >= 64) learningLevelText = 'високий ступінь навченості';
                else if (learningLevelNum >= 36) learningLevelText = 'достатній ступінь навченості';
                else if (learningLevelNum > 0) learningLevelText = 'середній ступінь навченості';
                
                // ✅ ОНОВЛЕНО: Додати кількість в дужках
                row.innerHTML = `
                    <td>${rowNum}</td>
                    <td style="text-align: left;">${item.subject}</td>
                    <td>${notAssessedPercent}% (${item.not_assessed_count || notAssessed})</td>
                    <td>${initialPercent}% (${item.initial_count || initialLevel})</td>
                    <td>${averagePercent}% (${item.average_count || averageLevel})</td>
                    <td>${sufficientPercent}% (${item.sufficient_count || sufficientLevel})</td>
                    <td>${highPercent}% (${item.high_count || highLevel})</td>
                    <td>${stats.avgScore}</td>
                    <td>${stats.learningLevel}</td>
                    <td style="font-size: 0.85rem;">${learningLevelText}</td>
                    <td>${stats.qualityCoeff}</td>
                    <td>${stats.qualityPercent}</td>
                    <td>${stats.resultCoeff}</td>
                `;
                
                // ✅ ОНОВЛЕНО: Накопичення для середнього по класу
                totalData.notAssessed += parseFloat(notAssessedPercent);
                totalData.initial += parseFloat(initialPercent);
                totalData.average += parseFloat(averagePercent);
                totalData.sufficient += parseFloat(sufficientPercent);
                totalData.high += parseFloat(highPercent);
                
                totalData.notAssessedCount += (item.not_assessed_count || notAssessed);
                totalData.initialCount += (item.initial_count || initialLevel);
                totalData.averageCount += (item.average_count || averageLevel);
                totalData.sufficientCount += (item.sufficient_count || sufficientLevel);
                totalData.highCount += (item.high_count || highLevel);
                
                totalData.avgScore.push(parseFloat(stats.avgScore));
                totalData.learningLevel.push(learningLevelNum);
                totalData.qualityCoeff.push(parseFloat(stats.qualityCoeff.replace('%', '')));
                totalData.qualityPercent.push(parseFloat(stats.qualityPercent.replace('%', '')));
                totalData.resultCoeff.push(parseFloat(stats.resultCoeff.replace('%', '')));
                totalData.count++;
                
                rowNum++;
            } else {
                row.innerHTML = `
                    <td>${rowNum}</td>
                    <td style="text-align: left;">${item.subject}</td>
                    <td colspan="11" class="status-empty">Дані не внесені</td>
                `;
                rowNum++;
            }
            
            reportBody.appendChild(row);
        });
        
        // ✅ ОНОВЛЕНО: Додати рядок "ПОКАЗНИК ПО КЛАСУ" з абсолютними числами
        if (totalData.count > 0) {
            const avgRow = document.createElement('tr');
            avgRow.className = 'total-row';
            
            const avgNotAssessed = (totalData.notAssessed / totalData.count).toFixed(2);
            const avgInitial = (totalData.initial / totalData.count).toFixed(2);
            const avgAverage = (totalData.average / totalData.count).toFixed(2);
            const avgSufficient = (totalData.sufficient / totalData.count).toFixed(2);
            const avgHigh = (totalData.high / totalData.count).toFixed(2);
            
            const avgScore = (totalData.avgScore.reduce((a,b) => a+b, 0) / totalData.avgScore.length).toFixed(2);
            const avgLearningLevel = (totalData.learningLevel.reduce((a,b) => a+b, 0) / totalData.learningLevel.length).toFixed(2);
            const avgQualityCoeff = (totalData.qualityCoeff.reduce((a,b) => a+b, 0) / totalData.qualityCoeff.length).toFixed(2);
            const avgQualityPercent = (totalData.qualityPercent.reduce((a,b) => a+b, 0) / totalData.qualityPercent.length).toFixed(2);
            const avgResultCoeff = (totalData.resultCoeff.reduce((a,b) => a+b, 0) / totalData.resultCoeff.length).toFixed(2);
            
            let avgLearningText = '';
            if (avgLearningLevel >= 64) avgLearningText = 'високий ступінь навченості';
            else if (avgLearningLevel >= 36) avgLearningText = 'достатній ступінь навченості';
            else if (avgLearningLevel > 0) avgLearningText = 'середній ступінь навченості';
            
            avgRow.innerHTML = `
                <td colspan="2" style="text-align: left;"><strong>ПОКАЗНИК ПО КЛАСУ</strong></td>
                <td>${avgNotAssessed}% (${totalData.notAssessedCount})</td>
                <td>${avgInitial}% (${totalData.initialCount})</td>
                <td>${avgAverage}% (${totalData.averageCount})</td>
                <td>${avgSufficient}% (${totalData.sufficientCount})</td>
                <td>${avgHigh}% (${totalData.highCount})</td>
                <td>${avgScore}</td>
                <td>${avgLearningLevel}%</td>
                <td style="font-size: 0.85rem;">${avgLearningText}</td>
                <td>${avgQualityCoeff}%</td>
                <td>${avgQualityPercent}%</td>
                <td>${avgResultCoeff}%</td>
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
    const exportBtn = document.getElementById('exportExcelBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            const year = yearFilter.value;
            const className = classFilter.value;
            const semester = semesterFilter.value;
            
            if (!year || !className) {
                showMessage('Спочатку завантажте звіт', 'warning');
                return;
            }
            
            // Завантажити Excel - кодуємо назву класу
            window.location.href = `/export_class_report/${encodeURIComponent(year)}/${encodeURIComponent(className)}/${semester}`;
        });
    }

});