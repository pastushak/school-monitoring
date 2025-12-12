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
            
            if (classInfo.filled > 0) {
                // Тут потрібно завантажити детальні дані класу для показників
                // Поки що показуємо прогрес
                row.innerHTML = `
                    <td><strong>${className}</strong></td>
                    <td colspan="11" style="text-align: center;">
                        <em>Дані доступні тільки при перегляді по класу</em>
                    </td>
                    <td>
                        <div class="mini-progress">
                            <div class="mini-progress-fill" style="width: ${classInfo.progress}%"></div>
                        </div>
                        <br><small>${classInfo.progress}%</small>
                    </td>
                `;
            } else {
                row.innerHTML = `
                    <td><strong>${className}</strong></td>
                    <td colspan="11" class="status-empty">Дані не внесені</td>
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
        const avgRow = document.createElement('tr');
        avgRow.className = 'total-row';
        avgRow.innerHTML = `
            <td><strong>середні дані по ліцею</strong></td>
            <td colspan="11" style="text-align: center;">
                <em>Розраховуються на основі детальних даних класів</em>
            </td>
            <td>
                <strong>${document.getElementById('overallProgressText').textContent}</strong>
            </td>
        `;
        reportBody.appendChild(avgRow);
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