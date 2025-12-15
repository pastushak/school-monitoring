document.addEventListener('DOMContentLoaded', function() {
    const yearSelect = document.getElementById('year');
    const classSelect = document.getElementById('class');
    const teacherSelect = document.getElementById('teacher');
    const subjectSelect = document.getElementById('subject');
    const studentCountInput = document.getElementById('studentCount');
    const dataSection = document.getElementById('dataSection');
    const calculateBtn = document.getElementById('calculateBtn');
    const form = document.getElementById('monitoringForm');
    const messageDiv = document.getElementById('message');
    
    // Масив для зберігання полів оцінок
    const gradeInputs = [];
    for (let i = 12; i >= 1; i--) {
        gradeInputs.push(document.getElementById('grade' + i));
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
            
            teacherSelect.disabled = true;
            teacherSelect.innerHTML = '<option value="">Спочатку оберіть клас</option>';
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">Спочатку оберіть вчителя</option>';
            dataSection.style.display = 'none';
        } catch (error) {
            console.error('Error loading classes:', error);
        }
    });
    
    classSelect.addEventListener('change', async function() {
        const year = yearSelect.value;
        const className = this.value;
        
        if (!className) {
            teacherSelect.disabled = true;
            teacherSelect.innerHTML = '<option value="">Спочатку оберіть клас</option>';
            subjectSelect.disabled = true;
            dataSection.style.display = 'none';
            return;
        }
        
        // Завантаження вчителів
        try {
            const response = await fetch(`/get_teachers/${year}/${className}`);
            const teachers = await response.json();
            
            teacherSelect.innerHTML = '<option value="">Оберіть вчителя</option>';
            teachers.forEach(teacher => {
                const option = document.createElement('option');
                option.value = teacher;
                option.textContent = teacher;
                teacherSelect.appendChild(option);
            });
            teacherSelect.disabled = false;
            
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">Спочатку оберіть вчителя</option>';
            dataSection.style.display = 'none';
            
            // Завантаження кількості учнів
            const countResponse = await fetch(`/get_student_count/${className}`);
            const count = await countResponse.json();
            studentCountInput.value = count;
        } catch (error) {
            console.error('Error loading teachers:', error);
        }
    });
    
    teacherSelect.addEventListener('change', async function() {
        const year = yearSelect.value;
        const className = classSelect.value;
        const teacher = this.value;
        
        if (!teacher) {
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">Спочатку оберіть вчителя</option>';
            dataSection.style.display = 'none';
            return;
        }
        
        // Завантаження предметів
        try {
            const response = await fetch(`/get_subjects/${year}/${className}/${teacher}`);
            const subjects = await response.json();
            
            subjectSelect.innerHTML = '<option value="">Оберіть предмет</option>';
            subjects.forEach(subject => {
                const option = document.createElement('option');
                option.value = subject;
                option.textContent = subject;
                subjectSelect.appendChild(option);
            });
            subjectSelect.disabled = false;
            dataSection.style.display = 'none';
        } catch (error) {
            console.error('Error loading subjects:', error);
        }
    });
    
    subjectSelect.addEventListener('change', async function() {
        const subject = this.value;
        
        if (!subject) {
            dataSection.style.display = 'none';
            return;
        }
        
        // Показати форму для введення даних
        dataSection.style.display = 'block';
        clearGrades();
        
        // Спроба завантажити збережені дані
        try {
            const year = yearSelect.value;
            const className = classSelect.value;
            const teacher = teacherSelect.value;
            
            const response = await fetch(`/get_monitoring/${year}/${className}/${teacher}/${subject}`);
            const data = await response.json();
            
            if (data.grades) {
                // Заповнити форму збереженими даними
                for (let i = 1; i <= 12; i++) {
                    document.getElementById('grade' + i).value = data.grades['grade' + i] || 0;
                }
                calculateStatistics();
            }
        } catch (error) {
            console.error('Error loading saved data:', error);
        }
    });
    
    // Автоматичний розрахунок відсотків при введенні
    gradeInputs.forEach(input => {
        input.addEventListener('input', function() {
            calculatePercentages();
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
    }
    
    // Розрахунок всіх показників
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
        
        // Перевірка
        if (inputTotal > total) {
            showMessage('Увага! Сума введених оцінок перевищує кількість учнів у класі', 'error');
            return;
        }
        
        // 1. Середній бал успішності
        let sumGrades = 0;
        for (let i = 1; i <= 12; i++) {
            sumGrades += i * grades[i];
        }
        const avgScore = inputTotal > 0 ? (sumGrades / inputTotal).toFixed(2) : 0;
        document.getElementById('avgScore').textContent = avgScore;
        
        // 2. Ступінь навченості (СН) за формулою Симонова
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
        
        // 3. Коефіцієнт якості знань
        const highGrades = grades[12] + grades[11] + grades[10];
        const qualityCoeff = total > 0 ? ((highGrades / total) * 100).toFixed(2) : 0;
        document.getElementById('qualityCoeff').textContent = qualityCoeff + '%';
        
        // 4. Якість знань
        const passedGrades = grades[12] + grades[11] + grades[10] + grades[9] + grades[8] + grades[7];
        const qualityPercent = total > 0 ? ((passedGrades / total) * 100).toFixed(2) : 0;
        document.getElementById('qualityPercent').textContent = qualityPercent + '%';
        
        // 5. Коефіцієнт результативності знань
        const resultCoeff = total > 0 ? ((inputTotal / total) * 100).toFixed(2) : 0;
        document.getElementById('resultCoeff').textContent = resultCoeff + '%';
        
        calculatePercentages();
        showMessage('Показники успішно розраховано!', 'success');
    }
    
    // Збереження даних
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const year = yearSelect.value;
        const className = classSelect.value;
        const teacher = teacherSelect.value;
        const subject = subjectSelect.value;
        
        if (!year || !className || !teacher || !subject) {
            showMessage('Заповніть всі обов\'язкові поля', 'error');
            return;
        }
        
        // Зібрати дані оцінок
        const grades = {};
        for (let i = 1; i <= 12; i++) {
            grades['grade' + i] = parseInt(document.getElementById('grade' + i).value) || 0;
        }
        
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
            teacher: teacher,
            subject: subject,
            student_count: parseInt(studentCountInput.value),
            grades: grades,
            statistics: statistics
        };
        
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
            } else {
                showMessage('✗ Помилка збереження даних', 'error');
            }
        } catch (error) {
            showMessage('✗ Помилка з\'єднання з сервером', 'error');
            console.error('Error:', error);
        }
    });
    
    // НОВІ ОБРОБНИКИ КНОПОК
    
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
            // Скинути всі фільтри
            yearSelect.value = '';
            classSelect.value = '';
            classSelect.disabled = true;
            classSelect.innerHTML = '<option value="">Спочатку оберіть навчальний рік</option>';
            teacherSelect.value = '';
            teacherSelect.disabled = true;
            teacherSelect.innerHTML = '<option value="">Спочатку оберіть клас</option>';
            subjectSelect.value = '';
            subjectSelect.disabled = true;
            subjectSelect.innerHTML = '<option value="">Спочатку оберіть вчителя</option>';
            
            // Сховати секцію даних
            dataSection.style.display = 'none';
            
            // Очистити кількість учнів
            studentCountInput.value = '';
            
            // Очистити повідомлення
            messageDiv.style.display = 'none';
            
            showMessage('Фільтри скинуто', 'success');
        });
    }
    
    function resetForm() {
        classSelect.disabled = true;
        classSelect.innerHTML = '<option value="">Спочатку оберіть навчальний рік</option>';
        teacherSelect.disabled = true;
        teacherSelect.innerHTML = '<option value="">Спочатку оберіть клас</option>';
        subjectSelect.disabled = true;
        subjectSelect.innerHTML = '<option value="">Спочатку оберіть вчителя</option>';
        dataSection.style.display = 'none';
        studentCountInput.value = '';
        clearGrades();
    }
    
    function clearGrades() {
        for (let i = 1; i <= 12; i++) {
            document.getElementById('grade' + i).value = 0;
            document.getElementById('percent' + i).textContent = '0%';
        }
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