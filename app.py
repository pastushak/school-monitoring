from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import os
from dotenv import load_dotenv
import db_mongo

# Завантажити змінні середовища
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Шлях до файлів даних
DATA_DIR = 'data'
SCHOOL_DATA_FILE = os.path.join(DATA_DIR, 'school_data.json')
MONITORING_DATA_FILE = os.path.join(DATA_DIR, 'monitoring_data.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Ініціалізація файлів даних
def init_data_files():
    # Створення users.json з ролями
    if not os.path.exists(USERS_FILE):
        users = {
            # Приклад: email -> роль, ПІБ, клас (для класних керівників)
            "admin@school.com": {
                "role": "admin",
                "name": "Адміністратор",
                "class": None
            },
            "classhead5a@school.com": {
                "role": "class_head",
                "name": "Класний керівник 5-А",
                "class": "5-А"
            },
            # Вчителі - будуть додані автоматично з навантаження
        }
        
        # Додати всіх вчителів
        school_data_temp = load_school_data_init()
        if school_data_temp:
            for teacher_name in school_data_temp.get('teachers', {}).keys():
                email = teacher_name.replace(" ", ".").lower() + "@school.com"
                users[email] = {
                    "role": "teacher",
                    "name": teacher_name,
                    "class": None
                }
        
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    # Створення school_data.json
    if not os.path.exists(SCHOOL_DATA_FILE):
        school_data = {
            "academic_years": ["2025-2026"],
            "classes": {
                "5-А": 32, "6-А": 31, "6-Б": 31, "7-А": 29, "7-Б": 30,
                "8-А": 26, "8-Б": 28, "9-А": 35, "9-Б": 36,
                "10-А": 23, "10-Б": 18, "11-А": 26, "11-Б": 26
            },
            "teachers": {
                "Ільків Наталія Валентинівна": {
                    "5-А": ["Інтегрований курс \"Пізнаємо природу\""],
                    "8-А": ["Біологія"],
                    "8-Б": ["Біологія"],
                    "9-А": ["Біологія", "Основи здоров'я"],
                    "9-Б": ["Основи здоров'я"],
                    "10-А": ["Біологія"],
                    "10-Б": ["Біологія"],
                    "11-А": ["Біологія"],
                    "11-Б": ["Біологія"]
                },
                "Андрейченко Леся Євгенівна": {
                    "6-А": ["Українська мова"],
                    "6-Б": ["Українська мова"],
                    "7-А": ["Українська мова"],
                    "7-Б": ["Українська мова"],
                    "8-А": ["Українська мова"],
                    "9-Б": ["Українська мова", "Українська література"]
                },
                "Бойцан Лариса Василівна": {
                    "7-А": ["Алгебра", "Геометрія"],
                    "8-А": ["Алгебра", "Геометрія"],
                    "10-Б": ["Математика"],
                    "11-Б": ["Математика"]
                },
                "Бойчук Мар'яна Юріївна": {
                    "5-А": ["Фізична культура"],
                    "6-Б": ["Фізична культура"],
                    "8-А": ["Фізична культура"],
                    "8-Б": ["Фізична культура"],
                    "10-А": ["Фізична культура"],
                    "11-А": ["Фізична культура"],
                    "11-Б": ["Фізична культура"]
                },
                "Боледзюк Ірина Степанівна": {
                    "8-А": ["Історія України", "Всесвітня історія"],
                    "8-Б": ["Історія України", "Всесвітня історія"],
                    "9-А": ["Історія України", "Всесвітня історія"],
                    "9-Б": ["Історія України", "Всесвітня історія"],
                    "10-А": ["Історія України", "Всесвітня історія"],
                    "10-Б": ["Історія України"],
                    "11-А": ["Історія України", "Всесвітня історія"],
                    "11-Б": ["Історія України"]
                },
                "Ванькович Христина Степанівна": {
                    "6-А": ["Мистецтво"],
                    "6-Б": ["Мистецтво"],
                    "7-А": ["Мистецтво"],
                    "7-Б": ["Мистецтво"],
                    "8-А": ["Мистецтво"],
                    "8-Б": ["Мистецтво"],
                    "9-А": ["Мистецтво"],
                    "9-Б": ["Мистецтво"]
                },
                "Василькова Ірина Василівна": {
                    "7-А": ["Англійська мова"],
                    "7-Б": ["Англійська мова"],
                    "9-Б": ["Англійська мова"],
                    "10-Б": ["Англійська мова"],
                    "11-А": ["Англійська мова"]
                },
                "Вовк Марія Василівна": {
                    "6-А": ["Українська література"],
                    "8-А": ["Зарубіжна література"],
                    "8-Б": ["Зарубіжна література"],
                    "9-Б": ["Зарубіжна література"],
                    "10-А": ["Українська література", "Зарубіжна література"],
                    "10-Б": ["Українська література", "Зарубіжна література"]
                },
                "Грицанюк Галина Миколаївна": {
                    "5-А": ["Зарубіжна література"],
                    "6-А": ["Зарубіжна література"],
                    "6-Б": ["Зарубіжна література"],
                    "7-А": ["Зарубіжна література"],
                    "7-Б": ["Зарубіжна література"]
                },
                "Дзвінчук Тарас Юрійович": {
                    "5-А": ["Технології"],
                    "6-А": ["Технології"],
                    "6-Б": ["Технології"],
                    "7-А": ["Технології"],
                    "7-Б": ["Технології"],
                    "8-Б": ["Технології"],
                    "9-А": ["Технології"],
                    "9-Б": ["Технології"]
                },
                "Задемленюк Ірина Тарасівна": {
                    "5-А": ["Технології"],
                    "6-А": ["Технології"],
                    "6-Б": ["Технології"],
                    "7-А": ["Технології"],
                    "7-Б": ["Технології"],
                    "8-А": ["Технології", "ІК \"Здоров'я, безпека та добробут\""],
                    "8-Б": ["ІК \"Здоров'я, безпека та добробут\""],
                    "9-А": ["Технології"],
                    "9-Б": ["Технології"],
                    "10-А": ["Технології"],
                    "10-Б": ["Технології"],
                    "11-А": ["Технології"],
                    "11-Б": ["Технології"]
                },
                "Задемленюк Олег Вікторович": {
                    "5-А": ["Інформатика"],
                    "6-А": ["Інформатика"],
                    "6-Б": ["Інформатика"],
                    "7-А": ["Інформатика"],
                    "8-А": ["Інформатика"],
                    "9-А": ["Інформатика"],
                    "10-А": ["Інформатика"],
                    "10-Б": ["Інформатика"],
                    "11-А": ["Інформатика"],
                    "11-Б": ["Інформатика"]
                },
                "Кольцюк Валерій Дмитрович": {
                    "5-А": ["Інформатика"],
                    "6-А": ["Інформатика"],
                    "6-Б": ["Інформатика"],
                    "7-А": ["Фізика"],
                    "7-Б": ["Інформатика", "Фізика"],
                    "8-А": ["Інформатика"],
                    "8-Б": ["Інформатика"],
                    "9-А": ["Інформатика"],
                    "9-Б": ["Інформатика"],
                    "10-А": ["Інформатика"],
                    "10-Б": ["Інформатика"],
                    "11-А": ["Астрономія"],
                    "11-Б": ["Астрономія"]
                },
                "Кох Алла Степанівна": {
                    "7-А": ["Українська мова", "Українська література"],
                    "7-Б": ["Українська література"],
                    "9-А": ["Українська мова"],
                    "9-Б": ["Українська мова"],
                    "10-Б": ["Українська мова"]
                },
                "Кривюк Лілія Михайлівна": {
                    "7-А": ["Хімія"],
                    "7-Б": ["Хімія"],
                    "8-А": ["Хімія"],
                    "8-Б": ["Хімія"],
                    "9-А": ["Хімія", "Біологія"],
                    "9-Б": ["Хімія"],
                    "10-А": ["Хімія"],
                    "10-Б": ["Хімія"],
                    "11-А": ["Хімія"],
                    "11-Б": ["Хімія"]
                },
                "Кудиба Лілія Богданівна": {
                    "5-А": ["Математика"],
                    "6-Б": ["Математика"],
                    "7-Б": ["Алгебра", "Геометрія"],
                    "9-А": ["Алгебра", "Геометрія"]
                },
                "Кушицький Роман Зеновійович": {
                    "8-А": ["Географія", "Підприємництво і фінансова грамотність"],
                    "8-Б": ["Географія", "Підприємництво і фінансова грамотність"]
                },
                "Лазор Ольга Ярославівна": {
                    "8-А": ["Фізика"],
                    "8-Б": ["Фізика"],
                    "9-А": ["Фізика"],
                    "9-Б": ["Фізика"],
                    "10-А": ["Фізика"],
                    "10-Б": ["Фізика"],
                    "11-А": ["Фізика"],
                    "11-Б": ["Фізика"]
                },
                "Матійчук Марія Михайлівна": {
                    "5-А": ["ІК \"Здоров'я, безпека та добробут\""],
                    "6-А": ["Біологія", "ІК \"Здоров'я, безпека та добробут\""],
                    "6-Б": ["Біологія", "ІК \"Здоров'я, безпека та добробут\""],
                    "7-А": ["Біологія", "ІК \"Здоров'я, безпека та добробут\""],
                    "7-Б": ["Біологія", "ІК \"Здоров'я, безпека та добробут\""]
                },
                "Матковська Любов Михайлівна": {
                    "6-А": ["Географія"],
                    "6-Б": ["Географія"],
                    "7-А": ["Географія"],
                    "7-Б": ["Географія"],
                    "9-А": ["Географія"],
                    "9-Б": ["Географія"],
                   "10-А": ["Географія"],
                    "10-Б": ["Географія"],
                    "11-А": ["Географія"],
                    "11-Б": ["Географія"]
                },
                "Носурак Іван Васильович": {
                    "8-Б": ["Алгебра", "Геометрія"],
                    "9-Б": ["Алгебра"],
                    "10-А": ["Математика"],
                    "11-А": ["Математика"]
                },
                "Пастушак Роман Васильович": {
                    "6-А": ["Математика"],
                    "7-А": ["Інформатика"],
                    "7-Б": ["Інформатика"],
                    "8-Б": ["Інформатика"],
                    "9-Б": ["Інформатика", "Геометрія"],
                    "11-А": ["Інформатика"],
                    "11-Б": ["Інформатика"]
                },
                "Пашко Тетяна Миколаївна": {
                    "5-А": ["Німецька мова"],
                    "7-А": ["Німецька мова"],
                    "10-А": ["Німецька мова"],
                    "11-А": ["Німецька мова"]
                },
                "Пашник Тетяна Миколаївна": {
                    "5-А": ["Українська мова"],
                    "7-Б": ["Українська мова"],
                    "8-А": ["Українська література"],
                    "8-Б": ["Українська мова", "Українська література"],
                    "11-А": ["Українська мова"]
                },
                "Перцович Дарія Несторівна": {
                    "5-А": ["Англійська мова"],
                    "8-А": ["Англійська мова"],
                    "8-Б": ["Англійська мова"],
                    "9-А": ["Англійська мова"],
                    "11-Б": ["Англійська мова"]
                },
                "Петранюк Уляна Василівна": {
                    "5-А": ["Українська мова", "Українська література"],
                    "6-А": ["Українська мова"],
                    "6-Б": ["Українська мова"],
                    "10-А": ["Українська мова"],
                    "11-Б": ["Українська мова", "Українська література"]
                },
                "Сембратович Любов Василівна": {
                    "9-А": ["Українська мова", "Українська література", "Зарубіжна література"],
                    "11-А": ["Українська література", "Зарубіжна література"],
                    "11-Б": ["Зарубіжна література"]
                },
                "Титик Світлана Григорівна": {
                    "6-А": ["Англійська мова"],
                    "6-Б": ["Англійська мова"],
                    "7-А": ["Англійська мова"],
                    "7-Б": ["Англійська мова"],
                    "9-А": ["Англійська мова"]
                },
                "Ткачук Володимир Михайлович": {
                    "10-Б": ["Всесвітня історія"],
                    "11-Б": ["Всесвітня історія"]
                },
                "Ткачук Оксана Євгенівна": {
                    "5-А": ["Вступ до історії України та громадянської освіти"],
                    "6-А": ["Вступ до історії України та громадянської освіти"],
                    "6-Б": ["Вступ до історії України та громадянської освіти"],
                    "7-А": ["Історія України", "Всесвітня історія"],
                    "7-Б": ["Історія України", "Всесвітня історія"],
                    "9-А": ["Основи правознавства"],
                    "9-Б": ["Основи правознавства"],
                    "10-А": ["Громадянська освіта"],
                    "10-Б": ["Громадянська освіта"]
                },
                "Філоненко Ірина Миколаївна": {
                    "5-А": ["Німецька мова"],
                    "6-А": ["Німецька мова"],
                    "6-Б": ["Німецька мова"],
                    "7-Б": ["Німецька мова"],
                    "8-А": ["Німецька мова"],
                    "8-Б": ["Німецька мова"],
                    "9-А": ["Німецька мова"],
                    "9-Б": ["Німецька мова"]
                },
                "Федорак Олена Ігорівна": {
                    "6-А": ["Фізична культура"],
                    

# Головна сторінка - вибір режиму
@app.route('/')
def index():
    return render_template('login.html')

# Авторизація
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        users = load_users()
        
        if email not in users:
            return render_template('login.html', error="Користувача не знайдено")
        
        user = users[email]
        session['email'] = email
        session['name'] = user['name']
        session['role'] = user['role']
        session['class'] = user.get('class')
        
        # Визначити всі доступні ролі (вчитель завжди є у всіх)
        available_roles = ['teacher']
        if user['role'] == 'class_head':
            available_roles.append('class_head')
        elif user['role'] == 'admin':
            available_roles.append('admin')
        
        session['available_roles'] = available_roles
        
        # Перенаправлення на сторінку вибору режиму або на форму вчителя
        if len(available_roles) > 1:
            return redirect(url_for('mode_selection'))
        else:
            return redirect(url_for('teacher_form'))
    
    return render_template('login.html')

# Вибір режиму роботи (для користувачів з кількома ролями)
@app.route('/mode_selection')
def mode_selection():
    if 'email' not in session:
        return redirect(url_for('index'))
    
    available_roles = session.get('available_roles', ['teacher'])
    return render_template('mode_selection.html', 
                         available_roles=available_roles,
                         user_name=session['name'],
                         user_class=session.get('class'))

# Перемикання режиму
@app.route('/switch_mode/<mode>')
def switch_mode(mode):
    if 'email' not in session:
        return redirect(url_for('index'))
    
    available_roles = session.get('available_roles', ['teacher'])
    
    if mode == 'teacher':
        return redirect(url_for('teacher_form'))
    elif mode == 'class_head' and 'class_head' in available_roles:
        return redirect(url_for('class_report'))
    elif mode == 'admin' and 'admin' in available_roles:
        return redirect(url_for('school_report'))
    
    return redirect(url_for('mode_selection'))

# Вихід
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Форма для вчителя
@app.route('/teacher_form')
def teacher_form():
    if 'email' not in session or session['role'] != 'teacher':
        return redirect(url_for('index'))
    
    school_data = load_school_data()
    return render_template('teacher_form.html', 
                         academic_years=school_data['academic_years'],
                         teacher_name=session['name'])

# Звіт по класу (для класних керівників)
@app.route('/class_report')
def class_report():
    if 'email' not in session or session['role'] not in ['class_head', 'admin']:
        return redirect(url_for('index'))
    
    school_data = load_school_data()
    
    # Якщо класний керівник - показати тільки його клас
    available_classes = [session['class']] if session['role'] == 'class_head' else list(school_data['classes'].keys())
    
    return render_template('class_report.html',
                         academic_years=school_data['academic_years'],
                         classes=available_classes,
                         user_role=session['role'])

# Звіт по школі (тільки для адміністрації)
@app.route('/school_report')
def school_report():
    if 'email' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    
    school_data = load_school_data()
    return render_template('school_report.html',
                         academic_years=school_data['academic_years'])

# API endpoints
@app.route('/get_classes/<year>')
def get_classes(year):
    school_data = load_school_data()
    
    # Для вчителя - тільки класи де він викладає
    if session.get('role') == 'teacher':
        teacher_name = session.get('name')
        teacher_classes = []
        if teacher_name in school_data['teachers']:
            teacher_classes = list(school_data['teachers'][teacher_name].keys())
        return jsonify(sorted(teacher_classes))
    
    return jsonify(list(school_data['classes'].keys()))

@app.route('/get_teachers/<year>/<class_name>')
def get_teachers(year, class_name):
    school_data = load_school_data()
    
    # Для вчителя - тільки він сам
    if session.get('role') == 'teacher':
        return jsonify([session.get('name')])
    
    teachers_for_class = []
    for teacher, classes in school_data['teachers'].items():
        if class_name in classes:
            teachers_for_class.append(teacher)
    return jsonify(sorted(teachers_for_class))

@app.route('/get_subjects/<year>/<class_name>/<teacher>')
def get_subjects(year, class_name, teacher):
    school_data = load_school_data()
    if teacher in school_data['teachers'] and class_name in school_data['teachers'][teacher]:
        return jsonify(school_data['teachers'][teacher][class_name])
    return jsonify([])

@app.route('/get_student_count/<class_name>')
def get_student_count(class_name):
    school_data = load_school_data()
    return jsonify(school_data['classes'].get(class_name, 0))

@app.route('/save_monitoring', methods=['POST'])
def save_monitoring():
    if 'email' not in session or session['role'] != 'teacher':
        return jsonify({'success': False, 'error': 'Немає прав доступу'})
    
    data = request.json
    monitoring_data = load_monitoring_data()
    
    year = data['year']
    class_name = data['class']
    teacher = data['teacher']
    subject = data['subject']
    
    key = f"{year}_{class_name}_{teacher}_{subject}"
    monitoring_data[key] = {
        'year': year,
        'class': class_name,
        'teacher': teacher,
        'subject': subject,
        'student_count': data['student_count'],
        'grades': data['grades'],
        'statistics': data['statistics'],
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    save_monitoring_data(monitoring_data)
    return jsonify({'success': True})

@app.route('/get_monitoring/<year>/<class_name>/<teacher>/<subject>')
def get_monitoring(year, class_name, teacher, subject):
    monitoring_data = load_monitoring_data()
    key = f"{year}_{class_name}_{teacher}_{subject}"
    return jsonify(monitoring_data.get(key, {}))

# Звіт по класу - дані
@app.route('/get_class_report/<year>/<class_name>')
def get_class_report(year, class_name):
    monitoring_data = load_monitoring_data()
    school_data = load_school_data()
    
    # Знайти всі можливі предмети для цього класу
    all_subjects = {}
    for teacher, classes in school_data['teachers'].items():
        if class_name in classes:
            for subject in classes[class_name]:
                if subject not in all_subjects:
                    all_subjects[subject] = teacher
    
    # Зібрати дані
    class_data = []
    filled_count = 0
    total_count = len(all_subjects)
    
    for subject, teacher in all_subjects.items():
        key = f"{year}_{class_name}_{teacher}_{subject}"
        if key in monitoring_data:
            record = monitoring_data[key]
            class_data.append({
                'subject': subject,
                'teacher': teacher,
                'statistics': record['statistics'],
                'grades': record['grades'],
                'student_count': record['student_count'],
                'filled': True
            })
            filled_count += 1
        else:
            class_data.append({
                'subject': subject,
                'teacher': teacher,
                'filled': False
            })
    
    progress = (filled_count / total_count * 100) if total_count > 0 else 0
    
    return jsonify({
        'data': class_data,
        'progress': round(progress, 1),
        'filled': filled_count,
        'total': total_count
    })

# Звіт по школі - дані
@app.route('/get_school_report/<year>')
def get_school_report(year):
    monitoring_data = load_monitoring_data()
    school_data = load_school_data()
    
    # Підрахувати загальну кількість предметів по школі
    total_subjects = 0
    filled_subjects = 0
    
    class_reports = {}
    
    for class_name in school_data['classes'].keys():
        # Підрахувати предмети для класу
        class_subjects = {}
        for teacher, classes in school_data['teachers'].items():
            if class_name in classes:
                for subject in classes[class_name]:
                    class_subjects[f"{teacher}_{subject}"] = {
                        'teacher': teacher,
                        'subject': subject
                    }
        
        class_total = len(class_subjects)
        class_filled = 0
        
        # Перевірити заповнені
        for key_combo, info in class_subjects.items():
            total_subjects += 1
            key = f"{year}_{class_name}_{info['teacher']}_{info['subject']}"
            if key in monitoring_data:
                class_filled += 1
                filled_subjects += 1
        
        class_progress = (class_filled / class_total * 100) if class_total > 0 else 0
        
        class_reports[class_name] = {
            'filled': class_filled,
            'total': class_total,
            'progress': round(class_progress, 1)
        }
    
    overall_progress = (filled_subjects / total_subjects * 100) if total_subjects > 0 else 0
    
    return jsonify({
        'classes': class_reports,
        'overall_progress': round(overall_progress, 1),
        'overall_filled': filled_subjects,
        'overall_total': total_subjects
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
