document.addEventListener('DOMContentLoaded', function() {
    // Список предметів що можуть мати поділ на групи
    const DIVISIBLE_SUBJECTS = [
        'Англійська мова',
        'Інформатика',
        'Німецька мова',
        'Технології',
        'Українська мова',
        'Захист України'
    ];
    const yearSelect = document.getElementById('year');
    const classSelect = document.getElementById('class');
    const teacherInput = document.getElementById('teacher'); // Тепер це hidden input
    const teacherName = teacherInput ? teacherInput.value : '';
    const subjectSelect = document.getElementById('subject');
    const studentCountInput = document.getElementById('studentCount');
    const dataSection = document.getElementById('dataSection');
    const calculateBtn = document.getElementById('calculateBtn');
    const form = document.getElementById('monitoringForm');
    const messageDiv = document.getElementById('message');
    const peExemptedSection = document.getElementById('peExemptedSection');
    const peExemptedCount = document.getElementById('peExemptedCount');
    let originalStudentCount = 0;
    let calculateTimeout
    
    // Масив для зберігання полів оцінок
    const gradeInputs = [];
    for (let i = 12; i >= 1; i--) {
        gradeInputs.push(document.getElementById('grade' + i));
    }
    // ✅ ДОДАТИ н/а
    const gradeNA = document.getElementById('gradeNA');
    if (gradeNA) {
        gradeInputs.push(gradeNA);
    }
    
    // Каскадні випадаючі списки
    yearSelect.addEventListener('change', async function() {
        const year = this.value;
        if (!year) {
            resetForm();
            return;
        }
        
        // Завантаження класів
        try {
            const response = await fetch(`/get_classes/${year}`);
            const classes = await response.json();
            
            classSelect.innerHTML = '<option value="">Оберіть клас</option>';
            classes.forEach(cls => {
                const option = document.createElement('option');
                option.value = cls;
                option.textContent = cls;
                classSelect.appendChild(option);
            });
            classSelect.disabled = false;
            
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">Спочатку оберіть клас</option>';
            dataSection.style.display = 'none';
        } catch (error) {
            console.error('Error loading classes:', error);
        }
    });
    
    classSelect.addEventListener('change', async function() {
        const year = yearSelect.value;
        const className = this.value;
        
        if (!className) {
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">Спочатку оберіть клас</option>';
            dataSection.style.display = 'none';
            peExemptedSection.style.display = 'none';  // ✅ ДОДАТИ
            return;
        }
        
        try {
            // Показати що завантажується
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">Завантаження...</option>';
            dataSection.style.display = 'none';
            peExemptedSection.style.display = 'none';  // ✅ ДОДАТИ
            
            // Завантаження кількості учнів
            const countResponse = await fetch(`/get_student_count/${className}`);
            const count = await countResponse.json();
            studentCountInput.value = count;
            originalStudentCount = count;  // ✅ ДОДАТИ
            peExemptedCount.value = 0;     // ✅ ДОДАТИ
            
            // Автоматично завантажити предмети для поточного вчителя
            if (teacherName) {
                const subjectsResponse = await fetch(`/get_subjects/${year}/${className}/${encodeURIComponent(teacherName)}`);
                const subjects = await subjectsResponse.json();
                
                subjectSelect.innerHTML = '<option value="">Оберіть предмет</option>';
                subjects.forEach(subject => {
                    const option = document.createElement('option');
                    option.value = subject;
                    option.textContent = subject;
                    subjectSelect.appendChild(option);
                });
                subjectSelect.disabled = false;
            }
        } catch (error) {
            console.error('Error loading subjects:', error);
            subjectSelect.innerHTML = '<option value="">Помилка завантаження</option>';
        }
    });
    
    subjectSelect.addEventListener('change', async function() {
        const subject = this.value;
        
        if (!subject) {
            peExemptedSection.style.display = 'none';  // ✅ ДОДАТИ
            dataSection.style.display = 'none';
            return;
        }
        
        // ✅ ДОДАТИ: Показати поле для фізкультури
        if (subject === 'Фізична культура') {
            peExemptedSection.style.display = 'block';
        } else {
            peExemptedSection.style.display = 'none';
            peExemptedCount.value = 0;
        }
        
        // Показати форму для введення даних
        dataSection.style.display = 'block';
        clearGrades();

        // Показати форму для введення даних
        dataSection.style.display = 'block';
        clearGrades();
        
        // ✅ ДОДАТИ ЦЕ: Показати/сховати підказку про поділ
        const divisionHint = document.getElementById('divisionHint');
        if (divisionHint) {
            if (DIVISIBLE_SUBJECTS.includes(subject)) {
                divisionHint.style.display = 'block';
            } else {
                divisionHint.style.display = 'none';
            }
        }
        
        // Спроба завантажити збережені дані
        try {
            const year = yearSelect.value;
            const className = classSelect.value;
            const semesterSelect = document.getElementById('semester');
            const semester = semesterSelect ? semesterSelect.value : '1';
            
            // ✅ ОНОВЛЕНО: Додати timestamp
            const timestamp = Date.now();
            const url = `/get_monitoring/${year}/${className}/${encodeURIComponent(teacherName)}/${encodeURIComponent(subject)}/${semester}?t=${timestamp}`;
            
            const response = await fetch(url, {
                // ✅ ДОДАТИ: Заголовки
                headers: {
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
            });
            
            const data = await response.json();
            
            if (data.grades) {
                // Заповнити форму збереженими даними
                for (let i = 1; i <= 12; i++) {
                    document.getElementById('grade' + i).value = data.grades['grade' + i] || 0;
                }
                
                if (data.grades.gradeNA !== undefined) {
                    document.getElementById('gradeNA').value = data.grades.gradeNA || 0;
                }
                
                // Завантажити збережену кількість учнів
                if (data.student_count) {
                    studentCountInput.value = data.student_count;
                }

                if (subject === 'Фізична культура' && data.pe_exempted_count !== undefined) {
                    peExemptedCount.value = data.pe_exempted_count;
                    originalStudentCount = data.student_count + data.pe_exempted_count;
                }
                
                calculateStatistics();
            }
        } catch (error) {
            console.error('Error loading saved data:', error);
        }
    });

    // ✅ ДОДАТИ: Обробник зміни семестру
    const semesterRadios = document.querySelectorAll('input[name="semester"]');
    semesterRadios.forEach(radio => {
        radio.addEventListener('change', async function() {
            const subject = subjectSelect.value;
            
            if (!subject) {
                return;
            }
            
            // Перезавантажити дані для нового семестру
            await reloadCurrentData();
        });
    });

    // ✅ ДОДАТИ: Функція для перезавантаження поточних даних
async function reloadCurrentData() {
    const year = yearSelect.value;
    const className = classSelect.value;
    const subject = subjectSelect.value;
    const semesterSelect = document.getElementById('semester');
    const semester = semesterSelect ? semesterSelect.value : '1';
    
    if (!year || !className || !subject || !semester) {
        return;
    }
    
    try {
        // ✅ Додати timestamp для уникнення кешування
        const timestamp = Date.now();
        const url = `/get_monitoring/${year}/${className}/${encodeURIComponent(teacherName)}/${encodeURIComponent(subject)}/${semester}?t=${timestamp}`;
        
        const response = await fetch(url, {
            // ✅ Заголовки для уникнення кешу
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        });
        
        const data = await response.json();
        
        if (data.grades) {
            // Заповнити форму збереженими даними
            for (let i = 1; i <= 12; i++) {
                document.getElementById('grade' + i).value = data.grades['grade' + i] || 0;
            }
            
            if (data.grades.gradeNA !== undefined) {
                document.getElementById('gradeNA').value = data.grades.gradeNA || 0;
            }
            
            if (data.student_count) {
                studentCountInput.value = data.student_count;
            }

            if (subject === 'Фізична культура' && data.pe_exempted_count !== undefined) {
                peExemptedCount.value = data.pe_exempted_count;
                originalStudentCount = data.student_count + data.pe_exempted_count;
            }
            
            calculateStatistics();
            console.log('[RELOAD] Дані успішно перезавантажено');
        }
    } catch (error) {
        console.error('[RELOAD] Помилка перезавантаження:', error);
    }
}

    // ✅ ДОДАТИ ЦІЛКОМ НОВИЙ ОБРОБНИК:
    // Автопідрахунок при зміні звільнених
    peExemptedCount.addEventListener('input', function() {
        const subject = subjectSelect.value;
        
        if (subject !== 'Фізична культура') {
            return;
        }
        
        if (!originalStudentCount || originalStudentCount === 0) {
            originalStudentCount = parseInt(studentCount.value) || 0;
        }
        
        const exempted = parseInt(this.value) || 0;
        const active = originalStudentCount - exempted;
        
        if (active > 0) {
            studentCount.value = active;
            showMessage(`✓ Оновлено: ${originalStudentCount} - ${exempted} = ${active} учнів`, 'success');
        } else {
            showMessage('❌ Кількість звільнених не може перевищувати загальну кількість учнів', 'error');
            this.value = Math.max(0, originalStudentCount - 1);
            studentCount.value = 1;
        }
    });
    
    gradeInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Скасувати попередній таймер
            clearTimeout(calculateTimeout);
            
            // Почекати 300ms перед розрахунком
            calculateTimeout = setTimeout(() => {
                calculatePercentages();
            }, 300);
        });
    });
    
    // Кнопка розрахунку показників
    calculateBtn.addEventListener('click', function() {
        calculateStatistics();
    });
    
    // Розрахунок відсотків
    function calculatePercentages() {
        const total = parseInt(studentCountInput.value) || 0;
        if (total === 0) return;
        
        for (let i = 1; i <= 12; i++) {
            const count = parseInt(document.getElementById('grade' + i).value) || 0;
            const percent = ((count / total) * 100).toFixed(2);
            document.getElementById('percent' + i).textContent = percent + '%';
        }

        // ✅ ДОДАТИ н/а
        const naCount = parseInt(document.getElementById('gradeNA').value) || 0;
        const naPercent = ((naCount / total) * 100).toFixed(2);
        document.getElementById('percentNA').textContent = naPercent + '%';
    }
    
    function calculateStatistics() {
        const total = parseInt(studentCountInput.value) || 0;
        if (total === 0) {
            showMessage('Спочатку оберіть клас', 'warning');
            return;
        }
        
        // Зібрати кількість оцінок
        const grades = {};
        let inputTotal = 0;
        for (let i = 1; i <= 12; i++) {
            const count = parseInt(document.getElementById('grade' + i).value) || 0;
            grades[i] = count;
            inputTotal += count;
        }
        
        // ✅ ДОДАТИ н/а
        const naCount = parseInt(document.getElementById('gradeNA').value) || 0;
        
        // Перевірка: оцінені + н/а не повинні перевищувати загальну кількість
        if (inputTotal + naCount > total) {
            showMessage('Увага! Сума оцінок та н/а перевищує кількість учнів у класі', 'error');
            return;
        }
        
        // 1. Середній бал (тільки з оцінених)
        let sumGrades = 0;
        for (let i = 1; i <= 12; i++) {
            sumGrades += i * grades[i];
        }
        const avgScore = inputTotal > 0 ? (sumGrades / inputTotal).toFixed(2) : 0;
        document.getElementById('avgScore').textContent = avgScore;
        
        // 2. Ступінь навченості (від загальної кількості учнів)
        let snSum = 0;
        for (let i = 4; i <= 12; i++) {
            snSum += i * grades[i];
        }
        const learningLevel = total > 0 ? ((snSum / (12 * total)) * 100).toFixed(2) : 0;
        document.getElementById('learningLevel').textContent = learningLevel + '%';
        
        // Визначення рівня навченості
        let levelText = '';
        if (learningLevel >= 64) levelText = 'високий ступінь навченості';
        else if (learningLevel >= 36) levelText = 'достатній ступінь навченості';
        else if (learningLevel > 0) levelText = 'середній ступінь навченості';
        else levelText = '-';
        document.getElementById('learningLevelText').textContent = levelText;
        
        // 3. Коефіцієнт якості знань (від загальної кількості)
        const highGrades = grades[12] + grades[11] + grades[10];
        const qualityCoeff = total > 0 ? ((highGrades / total) * 100).toFixed(2) : 0;
        document.getElementById('qualityCoeff').textContent = qualityCoeff + '%';
        
        // 4. Якість знань (від загальної кількості)
        const passedGrades = grades[12] + grades[11] + grades[10] + grades[9] + grades[8] + grades[7];
        const qualityPercent = total > 0 ? ((passedGrades / total) * 100).toFixed(2) : 0;
        document.getElementById('qualityPercent').textContent = qualityPercent + '%';
        
        // 5. Коефіцієнт результативності (від тих хто міг бути оцінений)
        // ✅ ВИПРАВЛЕНО: враховуємо н/а
        const couldBeGraded = total - naCount; // Мінус н/а
        const resultCoeff = couldBeGraded > 0 ? ((inputTotal / couldBeGraded) * 100).toFixed(2) : 0;
        document.getElementById('resultCoeff').textContent = resultCoeff + '%';
        
        calculatePercentages();
        showMessage('Показники успішно розраховано!', 'success');
    }
    
    // Збереження даних
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const year = yearSelect.value;
        const className = classSelect.value;
        const subject = subjectSelect.value;
        const semesterSelect = document.getElementById('semester');
        const semester = semesterSelect ? semesterSelect.value : '1';
        
        if (!year || !className || !teacherName || !subject) {
            showMessage('Заповніть всі обов\'язкові поля', 'error');
            return;
        }

        const studentCount = parseInt(studentCountInput.value);
        if (!studentCount || studentCount < 1 || studentCount > 50) {
            showMessage('❌ Вкажіть коректну кількість учнів (1-50)', 'error');
            return;
        }
        
        // Зібрати дані оцінок
        const grades = {};
        for (let i = 1; i <= 12; i++) {
            grades['grade' + i] = parseInt(document.getElementById('grade' + i).value) || 0;
        }
        grades['gradeNA'] = parseInt(document.getElementById('gradeNA').value) || 0;
        
        // Зібрати статистику
        const statistics = {
            avgScore: document.getElementById('avgScore').textContent,
            learningLevel: document.getElementById('learningLevel').textContent,
            qualityCoeff: document.getElementById('qualityCoeff').textContent,
            qualityPercent: document.getElementById('qualityPercent').textContent,
            resultCoeff: document.getElementById('resultCoeff').textContent
        };
        
        const data = {
            year: year,
            class: className,
            teacher: teacherName,
            subject: subject,
            student_count: parseInt(studentCountInput.value),
            grades: grades,
            statistics: statistics,
            semester: parseInt(semester)  // ✅ ДОДАТИ семестр
        };

        if (subject === 'Фізична культура') {
            data.pe_exempted_count = parseInt(peExemptedCount.value) || 0;
        }
        
        try {
            const response = await fetch('/save_monitoring', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showMessage('✓ Дані успішно збережено!', 'success');
                
                // ✅ ДОДАТИ: Затримка перед перезавантаженням
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // ✅ ДОДАТИ: Примусово перезавантажити дані
                await reloadCurrentData();
            } else {
                showMessage('✗ Помилка збереження даних', 'error');
            }
        } catch (error) {
            showMessage('✗ Помилка з\'єднання з сервером', 'error');
            console.error('Error:', error);
        }
    });
    
    // Кнопка "Очистити дані" - тільки оцінки
    const clearDataBtn = document.getElementById('clearDataBtn');
    if (clearDataBtn) {
        clearDataBtn.addEventListener('click', function() {
            // Очистити тільки поля оцінок
            for (let i = 1; i <= 12; i++) {
                const gradeInput = document.getElementById(`grade${i}`);
                if (gradeInput) {
                    gradeInput.value = '0';
                }
            }
            
            // Перерахувати (скине на нулі)
            calculateStatistics();
            
            showMessage('Дані очищено. Фільтри залишились незмінними.', 'success');
        });
    }
    
    // Кнопка "Скинути фільтри"
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function() {
            // Скинути фільтри
            yearSelect.value = '';
            classSelect.value = '';
            classSelect.disabled = true;
            classSelect.innerHTML = '<option value="">Спочатку оберіть навчальний рік</option>';
            subjectSelect.value = '';
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">Спочатку оберіть клас</option>';
            
            // Сховати секцію даних
            dataSection.style.display = 'none';
            
            // Очистити кількість учнів
            studentCountInput.value = '';
            
            // Очистити повідомлення
            messageDiv.style.display = 'none';
            
            showMessage('Фільтри скинуто', 'success');
        });
    }
    
    // Кнопка експорту в Excel для вчителя
    const exportTeacherBtn = document.getElementById('exportTeacherBtn');
    if (exportTeacherBtn) {
        exportTeacherBtn.addEventListener('click', function() {
            const year = yearSelect.value;
            const className = classSelect.value;
            const subject = subjectSelect.value;
            
            if (!year || !className || !teacherName || !subject) {
                showMessage('Спочатку оберіть всі параметри', 'warning');
                return;
            }
            
            // Перевірка чи є збережені дані
            const avgScore = document.getElementById('avgScore').textContent;
            if (!avgScore || avgScore === '0') {
                showMessage('Спочатку розрахуйте та збережіть дані', 'warning');
                return;
            }
            
            // ✅ ОНОВЛЕНО: Отримати вибраний семестр
            const semesterSelect = document.getElementById('semester');
            const semester = semesterSelect ? semesterSelect.value : '1';
            
            // Створити URL з правильним кодуванням
            const url = '/export_teacher_report/' + 
                encodeURIComponent(year) + '/' + 
                encodeURIComponent(className) + '/' + 
                encodeURIComponent(teacherName) + '/' + 
                encodeURIComponent(subject) + '/' + 
                semester;
            
            console.log('Export URL:', url);
            
            // Завантажити Excel
            window.location.href = url;
        });
    }
    
    function resetForm() {
        classSelect.disabled = true;
        classSelect.innerHTML = '<option value="">Спочатку оберіть навчальний рік</option>';
        subjectSelect.disabled = true;
        subjectSelect.innerHTML = '<option value="">Спочатку оберіть клас</option>';
        dataSection.style.display = 'none';
        studentCountInput.value = '';
        clearGrades();
    }
    
    function clearGrades() {
        for (let i = 1; i <= 12; i++) {
            document.getElementById('grade' + i).value = 0;
            document.getElementById('percent' + i).textContent = '0%';
        }
        // ✅ Очистити н/а
        document.getElementById('gradeNA').value = 0;
        document.getElementById('percentNA').textContent = '0%';
        
        // ✅ ДОДАТИ: Очистити дані про звільнених
        peExemptedCount.value = 0;
        originalStudentCount = 0;
        
        document.getElementById('avgScore').textContent = '0';
        document.getElementById('learningLevel').textContent = '0%';
        document.getElementById('learningLevelText').textContent = '-';
        document.getElementById('qualityCoeff').textContent = '0%';
        document.getElementById('qualityPercent').textContent = '0%';
        document.getElementById('resultCoeff').textContent = '0%';
    }
    
    function showMessage(text, type) {
        messageDiv.textContent = text;
        messageDiv.className = 'message ' + type;
        messageDiv.style.display = 'block';
        
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
});