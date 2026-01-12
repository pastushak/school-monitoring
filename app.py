from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, make_response
from datetime import datetime
import os
from dotenv import load_dotenv
import db_mongo
import export_excel
import json
import time

# Версія додатку
APP_VERSION = "1.5.0"
APP_UPDATE_DATE = "08.01.2026"

# Автоматична синхронізація school_data при старті
def sync_school_data_on_startup():
    """Синхронізувати school_data.json з MongoDB при старті"""
    import json
    from db_mongo import db  # ✅ ВАЖЛИВО!
    
    print("=" * 60)
    print("СИНХРОНІЗАЦІЯ school_data.json → MongoDB")
    print("=" * 60)
    
    try:
        with open('data/school_data.json', 'r', encoding='utf-8') as f:
            school_data = json.load(f)
        
        # Видалити стару колекцію
        result = db['school_data'].delete_many({})
        print(f"✓ Видалено старих записів: {result.deleted_count}")
        
        # Вставити нові дані
        db['school_data'].insert_one(school_data)
        print(f"✓ Додано класів: {len(school_data['classes'])}")
        print(f"✓ Додано вчителів: {len(school_data['teachers'])}")
        
        print("=" * 60)
        print("✓ СИНХРОНІЗАЦІЯ ЗАВЕРШЕНА!")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ ПОМИЛКА синхронізації: {e}")

# Викликати при старті
sync_school_data_on_startup()

# Завантажити змінні середовища
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Завантажити змінні середовища
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# ✅ ДОДАТИ: Декоратор для перевірки ролей
from functools import wraps

def role_required(roles):
    """Декоратор для перевірки ролей користувача"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'email' not in session:
                return redirect(url_for('login'))
            
            user_role = session.get('role')
            if user_role not in roles:
                return redirect(url_for('mode_selection'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_academic_years():
    """Отримати список навчальних років"""
    school_data = db_mongo.get_school_data()
    return school_data.get('academic_years', [])

# Головна сторінка - вибір режиму
@app.route('/')
def index():
    return render_template('login.html')

# Авторизація
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = db_mongo.get_user_by_email(email)
        
        if not user:
            return render_template('login.html', error="Користувача не знайдено")
        
        session['email'] = email
        session['name'] = user['name']
        session['role'] = user['role']
        session['class'] = user.get('class')
        
        # Визначити всі доступні ролі
        available_roles = ['teacher']
        if user['role'] == 'class_head':
            available_roles.append('class_head')
        elif user['role'] == 'admin':
            available_roles.append('admin')
        elif user['role'] == 'superadmin':
            available_roles = ['teacher', 'class_head', 'admin', 'superadmin']
        
        session['available_roles'] = available_roles
        
        # Перенаправлення
        if user['role'] == 'superadmin':
            return redirect(url_for('mode_selection'))  # ✅ Суперадмін завжди йде на вибір режиму
        elif len(available_roles) > 1:
            return redirect(url_for('mode_selection'))
        else:
            return redirect(url_for('teacher_form'))
    
    return render_template('login.html')

# Вибір режиму роботи
@app.route('/mode_selection')
def mode_selection():
    if 'email' not in session:
        return redirect(url_for('index'))
    
    available_roles = session.get('available_roles', ['teacher'])

    # Перевірити чи користувач бачив changelog для цієї версії
    show_changelog = session.get('last_seen_version') != APP_VERSION

    return render_template('mode_selection.html', 
                         available_roles=available_roles,
                         user_name=session['name'],
                         user_class=session.get('class'),
                         show_changelog=show_changelog,
                         app_version=APP_VERSION)

@app.route('/mark_changelog_seen')
def mark_changelog_seen():
    """Позначити що користувач бачив changelog"""
    if 'email' in session:
        session['last_seen_version'] = APP_VERSION
    return jsonify({'success': True})

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
    elif mode == 'superadmin' and 'superadmin' in available_roles:  # ✅ ДОДАТИ ЦЕЙ БЛОК
        return redirect(url_for('superadmin_dashboard'))
    
    return redirect(url_for('mode_selection'))

# Вихід
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Форма для вчителя
@app.route('/teacher_form')
def teacher_form():
    if 'email' not in session:
        return redirect(url_for('index'))
    
    school_data = db_mongo.get_school_data()
    return render_template('teacher_form.html', 
                         academic_years=school_data['academic_years'],
                         teacher_name=session['name'])

# Звіт по класу
@app.route('/class_report')
def class_report():
    if 'email' not in session or session['role'] not in ['class_head', 'admin']:
        return redirect(url_for('index'))
    
    school_data = db_mongo.get_school_data()
    
    # Для класного керівника - тільки його клас
    available_classes = [session['class']] if session['role'] == 'class_head' else list(school_data['classes'].keys())
    
    return render_template('class_report.html',
                         academic_years=school_data['academic_years'],
                         classes=available_classes,
                         user_role=session['role'])

# Звіт по школі
@app.route('/school_report')
def school_report():
    if 'email' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    
    school_data = db_mongo.get_school_data()
    return render_template('school_report.html',
                         academic_years=school_data['academic_years'])

# API endpoints
@app.route('/get_classes/<year>')
def get_classes(year):
    school_data = db_mongo.get_school_data()
    teacher_name = session.get('name')
    
    # Якщо вчитель має навантаження - показати тільки його класи
    if teacher_name and teacher_name in school_data.get('teachers', {}):
        teacher_classes = list(school_data['teachers'][teacher_name].keys())
        return jsonify(sorted(teacher_classes))
    
    # Інакше всі класи (для адмінів)
    return jsonify(sorted(list(school_data['classes'].keys())))

@app.route('/get_teachers/<year>/<class_name>')
def get_teachers(year, class_name):
    school_data = db_mongo.get_school_data()
    teacher_name = session.get('name')
    
    # Якщо користувач викладає в цьому класі - показати тільки його
    if teacher_name and teacher_name in school_data.get('teachers', {}):
        if class_name in school_data['teachers'][teacher_name]:
            return jsonify([teacher_name])
    
    # Інакше всі вчителі класу
    teachers_for_class = []
    for teacher, classes in school_data['teachers'].items():
        if class_name in classes:
            teachers_for_class.append(teacher)
    return jsonify(sorted(teachers_for_class))

@app.route('/get_subjects/<year>/<class_name>/<teacher>')
def get_subjects(year, class_name, teacher):
    school_data = db_mongo.get_school_data()
    if teacher in school_data.get('teachers', {}) and class_name in school_data['teachers'][teacher]:
        return jsonify(school_data['teachers'][teacher][class_name])
    return jsonify([])

@app.route('/get_student_count/<class_name>')
def get_student_count(class_name):
    school_data = db_mongo.get_school_data()
    return jsonify(school_data['classes'].get(class_name, 0))

@app.route('/save_monitoring', methods=['POST'])
def save_monitoring():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Не авторизовано'})
    
    data = request.json
    data['teacher'] = session.get('email')
    
    # ✅ ДОДАТИ: Детальне логування
    print(f"\n{'='*80}")
    print(f"[SAVE REQUEST] User: {session.get('email')}")
    print(f"[SAVE REQUEST] Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print(f"{'='*80}\n")
    
    try:
        success = db_mongo.save_monitoring_data(data)
        
        if success:
            # ✅ ДОДАТИ: Затримка для синхронізації
            import time
            time.sleep(0.1)  # 100ms затримка
            
            return jsonify({'success': True, 'message': 'Дані збережено'})
        else:
            return jsonify({'success': False, 'message': 'Помилка збереження'})
    except Exception as e:
        print(f"[SAVE ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_monitoring/<year>/<class_name>/<teacher>/<subject>/<semester>')
def get_monitoring(year, class_name, teacher, subject, semester):
    """Отримати збережені дані моніторингу"""
    
    # ✅ ДОДАТИ: Детальне логування
    print(f"\n{'='*80}")
    print(f"[GET REQUEST] Year: {year}, Class: {class_name}, Teacher: {teacher}")
    print(f"[GET REQUEST] Subject: {subject}, Semester: {semester}")
    print(f"{'='*80}\n")
    
    data = db_mongo.get_monitoring_data(year, class_name, teacher, subject, int(semester))
    
    # ✅ ДОДАТИ: Заголовки для уникнення кешування
    response = make_response(jsonify(data if data else {}))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

# Звіт по класу - дані
@app.route('/get_class_report/<year>/<class_name>')
def get_class_report(year, class_name):
    school_data = db_mongo.get_school_data()
    monitoring_data = db_mongo.get_class_monitoring_data(year, class_name)
    
    # Знайти всі можливі предмети для класу
    all_subjects = {}
    for teacher, classes in school_data.get('teachers', {}).items():
        if class_name in classes:
            for subject in classes[class_name]:
                all_subjects[f"{teacher}_{subject}"] = {
                    'teacher': teacher,
                    'subject': subject
                }
    
    # Зібрати дані
    class_data = []
    filled_count = 0
    total_count = len(all_subjects)
    
    # Створити словник для швидкого пошуку
    monitoring_dict = {}
    for record in monitoring_data:
        key = f"{record['teacher']}_{record['subject']}"
        monitoring_dict[key] = record
    
    for key, info in all_subjects.items():
        if key in monitoring_dict:
            record = monitoring_dict[key]
            grades = record['grades']
            student_count = record['student_count']
            
            # ✅ ДОДАТИ: Розрахувати абсолютні числа
            g3 = int(grades.get('grade3', 0))
            g2 = int(grades.get('grade2', 0))
            g1 = int(grades.get('grade1', 0))
            initial_count = g3 + g2 + g1
            
            g6 = int(grades.get('grade6', 0))
            g5 = int(grades.get('grade5', 0))
            g4 = int(grades.get('grade4', 0))
            average_count = g6 + g5 + g4
            
            g9 = int(grades.get('grade9', 0))
            g8 = int(grades.get('grade8', 0))
            g7 = int(grades.get('grade7', 0))
            sufficient_count = g9 + g8 + g7
            
            g12 = int(grades.get('grade12', 0))
            g11 = int(grades.get('grade11', 0))
            g10 = int(grades.get('grade10', 0))
            high_count = g12 + g11 + g10
            
            total_graded = initial_count + average_count + sufficient_count + high_count
            not_assessed_count = max(0, student_count - total_graded)
            
            class_data.append({
                'subject': info['subject'],
                'teacher': info['teacher'],
                'statistics': record['statistics'],
                'grades': record['grades'],
                'student_count': record['student_count'],
                # ✅ ДОДАТИ: Абсолютні числа
                'not_assessed_count': not_assessed_count,
                'initial_count': initial_count,
                'average_count': average_count,
                'sufficient_count': sufficient_count,
                'high_count': high_count,
                'filled': True
            })
            filled_count += 1
        else:
            class_data.append({
                'subject': info['subject'],
                'teacher': info['teacher'],
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
    school_data = db_mongo.get_school_data()
    all_monitoring = db_mongo.get_all_monitoring_data(year)
    
    # Створити словник для швидкого пошуку
    monitoring_dict = {}
    for record in all_monitoring:
        key = f"{record['class']}_{record['teacher']}_{record['subject']}"
        monitoring_dict[key] = record
    
    # Підрахувати для кожного класу
    total_subjects = 0
    filled_subjects = 0
    class_reports = {}
    
    for class_name in sorted(school_data['classes'].keys()):
        student_count = school_data['classes'][class_name]
        
        # Підрахувати предмети для класу
        class_subjects = []
        class_records = []
        
        for teacher, classes in school_data.get('teachers', {}).items():
            if class_name in classes:
                for subject in classes[class_name]:
                    key = f"{class_name}_{teacher}_{subject}"
                    class_subjects.append(key)
                    if key in monitoring_dict:
                        class_records.append(monitoring_dict[key])
        
        class_total = len(class_subjects)
        class_filled = len(class_records)
        
        total_subjects += class_total
        filled_subjects += class_filled
        
        class_progress = (class_filled / class_total * 100) if class_total > 0 else 0
        
        # Розрахувати середні показники для класу
        if class_records:
            # ✅ ДОДАТИ: Лічильники для абсолютних чисел
            total_not_assessed = 0
            total_initial = 0
            total_average = 0
            total_sufficient = 0
            total_high = 0
            
            total_not_assessed_pct = 0
            total_initial_pct = 0
            total_average_pct = 0
            total_sufficient_pct = 0
            total_high_pct = 0
            sum_avg_score = 0
            sum_learning_level = 0
            sum_quality_coeff = 0
            sum_quality_percent = 0
            sum_result_coeff = 0
            
            for record in class_records:
                grades = record['grades']
                rec_student_count = record['student_count']
                
                # ✅ ДОДАТИ: Захист від ділення на нуль
                if rec_student_count == 0:
                    continue
                
                # Рівні
                g1 = int(grades.get('grade1', 0))
                g2 = int(grades.get('grade2', 0))
                g3 = int(grades.get('grade3', 0))
                initial = g1 + g2 + g3
                
                g4 = int(grades.get('grade4', 0))
                g5 = int(grades.get('grade5', 0))
                g6 = int(grades.get('grade6', 0))
                average = g4 + g5 + g6
                
                g7 = int(grades.get('grade7', 0))
                g8 = int(grades.get('grade8', 0))
                g9 = int(grades.get('grade9', 0))
                sufficient = g7 + g8 + g9
                
                g10 = int(grades.get('grade10', 0))
                g11 = int(grades.get('grade11', 0))
                g12 = int(grades.get('grade12', 0))
                high = g10 + g11 + g12
                
                total_graded = initial + average + sufficient + high
                not_assessed = max(0, rec_student_count - total_graded)
                
                # ✅ ОНОВЛЕНО: Додати абсолютні числа
                total_not_assessed += not_assessed
                total_initial += initial
                total_average += average
                total_sufficient += sufficient
                total_high += high
                
                # Відсотки
                total_not_assessed_pct += (not_assessed / rec_student_count * 100)
                total_initial_pct += (initial / rec_student_count * 100)
                total_average_pct += (average / rec_student_count * 100)
                total_sufficient_pct += (sufficient / rec_student_count * 100)
                total_high_pct += (high / rec_student_count * 100)
                
                # Статистика
                stats = record['statistics']
                sum_avg_score += float(stats.get('avgScore', 0))
                sum_learning_level += float(stats.get('learningLevel', '0%').replace('%', ''))
                sum_quality_coeff += float(stats.get('qualityCoeff', '0%').replace('%', ''))
                sum_quality_percent += float(stats.get('qualityPercent', '0%').replace('%', ''))
                sum_result_coeff += float(stats.get('resultCoeff', '0%').replace('%', ''))
            
            num_records = len(class_records)
            
            # ✅ ДОДАТИ: Захист від ділення на нуль
            if num_records == 0:
                continue
            
            class_reports[class_name] = {
                'filled': class_filled,
                'total': class_total,
                'progress': round(class_progress, 1),
                'statistics': {
                    'not_assessed': round(total_not_assessed_pct / num_records, 2),
                    'initial': round(total_initial_pct / num_records, 2),
                    'average': round(total_average_pct / num_records, 2),
                    'sufficient': round(total_sufficient_pct / num_records, 2),
                    'high': round(total_high_pct / num_records, 2),
                    # ✅ ДОДАТИ: Абсолютні числа
                    'not_assessed_count': total_not_assessed,
                    'initial_count': total_initial,
                    'average_count': total_average,
                    'sufficient_count': total_sufficient,
                    'high_count': total_high,
                    'avg_score': round(sum_avg_score / num_records, 2),
                    'learning_level': round(sum_learning_level / num_records, 2),
                    'quality_coeff': round(sum_quality_coeff / num_records, 2),
                    'quality_percent': round(sum_quality_percent / num_records, 2),
                    'result_coeff': round(sum_result_coeff / num_records, 2)
                }
            }
        else:
            class_reports[class_name] = {
                'filled': class_filled,
                'total': class_total,
                'progress': round(class_progress, 1),
                'statistics': None
            }
    
    overall_progress = (filled_subjects / total_subjects * 100) if total_subjects > 0 else 0
    
    return jsonify({
        'classes': class_reports,
        'overall_progress': round(overall_progress, 1),
        'overall_filled': filled_subjects,
        'overall_total': total_subjects
    })

# Експорт звіту по класу в Excel
@app.route('/export_class_report/<year>/<class_name>/<semester>')
def export_class_report(year, class_name, semester):
    if 'email' not in session:
        return redirect(url_for('index'))
    
    school_data = db_mongo.get_school_data()
    monitoring_data = db_mongo.get_class_monitoring_data(year, class_name)
    
    # Зібрати дані як у get_class_report
    all_subjects = {}
    for teacher, classes in school_data.get('teachers', {}).items():
        if class_name in classes:
            for subject in classes[class_name]:
                all_subjects[f"{teacher}_{subject}"] = {
                    'teacher': teacher,
                    'subject': subject
                }
    
    class_data = []
    monitoring_dict = {}
    for record in monitoring_data:
        key = f"{record['teacher']}_{record['subject']}"
        monitoring_dict[key] = record
    
    for key, info in all_subjects.items():
        if key in monitoring_dict:
            record = monitoring_dict[key]
            class_data.append({
                'subject': info['subject'],
                'teacher': info['teacher'],
                'statistics': record['statistics'],
                'grades': record['grades'],
                'student_count': record['student_count'],
                'filled': True
            })
    
    # Створити Excel файл
    excel_file = export_excel.create_class_report_excel(
        class_data, 
        class_name, 
        year, 
        'I' if semester == '1' else 'II'
    )
    
    filename = f"Zvit_{class_name}_{year}_{semester}_semestr.xlsx"
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

# Експорт звіту по школі в Excel
@app.route('/export_school_report/<year>/<semester>')
def export_school_report(year, semester):
    if 'email' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    
    school_data = db_mongo.get_school_data()
    all_monitoring = db_mongo.get_all_monitoring_data(year)
    
    # Створити Excel файл з усіма даними моніторингу
    excel_file = export_excel.create_school_report_excel(
        school_data,
        all_monitoring,
        year,
        'I' if semester == '1' else 'II'
    )
    
    filename = f"Zvit_shkola_{year}_{semester}_semestr.xlsx"
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )
    
# Експорт звіту для вчителя в Excel
@app.route('/export_teacher_report/<year>/<class_name>/<teacher>/<subject>/<semester>')
def export_teacher_report(year, class_name, teacher, subject, semester):
    if 'email' not in session:
        return redirect(url_for('index'))
    
    # Використати semester з URL (вже є в параметрах)
    semester = int(semester)
    monitoring_data = db_mongo.get_monitoring_data(year, class_name, teacher, subject, semester)
    
    if not monitoring_data:
        return "Дані не знайдено", 404
    
    # Створити Excel файл
    # Створити Excel файл
    excel_file = export_excel.create_teacher_report_excel(
        monitoring_data,
        year,
        class_name,
        teacher,
        subject,
        semester  # ✅ Передати число (1 або 2)
    )
    
    # Безпечне ім'я файлу
    safe_subject = subject.replace('/', '-').replace('\\', '-')
    filename = f"Zvit_vchytelya_{class_name}_{safe_subject}_{year}_{semester}_semestr.xlsx"
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

# Панель суперадміна
@app.route('/superadmin_dashboard')
def superadmin_dashboard():
    if 'email' not in session or session['role'] != 'superadmin':
        return redirect(url_for('index'))
    
    school_data = db_mongo.get_school_data()
    
    # Статистика
    total_users = db_mongo.users_collection.count_documents({})
    total_records = db_mongo.monitoring_collection.count_documents({})
    total_classes = len(school_data.get('classes', {}))
    total_teachers = len(school_data.get('teachers', {}))
    
    # Останні 20 записів
    recent_activity = list(db_mongo.monitoring_collection.find().sort('updated_at', -1).limit(20))
    
    return render_template('superadmin_dashboard.html',
                         total_users=total_users,
                         total_records=total_records,
                         total_classes=total_classes,
                         total_teachers=total_teachers,
                         recent_activity=recent_activity,
                         user_name=session['name'])

# Перегляд по класах для суперадміна
@app.route('/superadmin/classes')
def superadmin_classes():
    if 'email' not in session or session['role'] != 'superadmin':
        return redirect(url_for('index'))
    
    school_data = db_mongo.get_school_data()
    classes_stats = {}
    
    # Підрахунок для кожного класу
    for class_name in school_data['classes'].keys():
        # Підрахувати всі можливі предмети
        total_subjects = 0
        for teacher, classes in school_data['teachers'].items():
            if class_name in classes:
                total_subjects += len(classes[class_name])
        
        # Підрахувати УНІКАЛЬНІ комбінації (вчитель + предмет)
        pipeline = [
            {"$match": {"class": class_name}},
            {"$group": {
                "_id": {
                    "teacher": "$teacher",
                    "subject": "$subject"
                }
            }},
            {"$count": "unique_count"}
        ]
        
        result = list(db_mongo.monitoring_collection.aggregate(pipeline))
        filled_subjects = result[0]['unique_count'] if result else 0
        
        progress = (filled_subjects / total_subjects * 100) if total_subjects > 0 else 0
        
        classes_stats[class_name] = {
            'total': total_subjects,
            'filled': filled_subjects,
            'progress': round(progress, 1),
            'student_count': school_data['classes'][class_name]
        }
    
    return render_template('superadmin_classes.html',
                         classes_stats=classes_stats,
                         user_name=session['name'])

# Перегляд по вчителях для суперадміна
@app.route('/superadmin/teachers')
def superadmin_teachers():
    if 'email' not in session or session['role'] != 'superadmin':
        return redirect(url_for('index'))
    
    school_data = db_mongo.get_school_data()
    teachers_stats = {}
    
    # Підрахунок для кожного вчителя
    for teacher_name in school_data['teachers'].keys():
        # Підрахувати всі можливі предмети вчителя
        total_subjects = 0
        for class_name, subjects in school_data['teachers'][teacher_name].items():
            total_subjects += len(subjects)
        
        # Підрахувати УНІКАЛЬНІ комбінації (клас + предмет)
        # Використовуємо distinct для підрахунку унікальних записів
        pipeline = [
            {"$match": {"teacher": teacher_name}},
            {"$group": {
                "_id": {
                    "class": "$class",
                    "subject": "$subject"
                }
            }},
            {"$count": "unique_count"}
        ]
        
        result = list(db_mongo.monitoring_collection.aggregate(pipeline))
        filled_subjects = result[0]['unique_count'] if result else 0
        
        progress = (filled_subjects / total_subjects * 100) if total_subjects > 0 else 0
        
        teachers_stats[teacher_name] = {
            'total': total_subjects,
            'filled': filled_subjects,
            'progress': round(progress, 1),
            'classes': list(school_data['teachers'][teacher_name].keys())
        }
    
    return render_template('superadmin_teachers.html',
                         teachers_stats=teachers_stats,
                         user_name=session['name'])

# Детальна статистика по вчителю
@app.route('/superadmin/teacher/<teacher_name>')
def superadmin_teacher_detail(teacher_name):
    if 'email' not in session or session['role'] != 'superadmin':
        return redirect(url_for('index'))
    
    school_data = db_mongo.get_school_data()
    
    # Перевірити чи існує вчитель
    if teacher_name not in school_data['teachers']:
        return redirect(url_for('superadmin_teachers'))
    
    # Отримати всі записи вчителя (тільки останні версії для кожної комбінації клас+предмет)
    teacher_records_raw = list(db_mongo.monitoring_collection.find({'teacher': teacher_name}).sort('updated_at', -1))

    # Створити словник для зберігання тільки останніх записів
    unique_records = {}
    for record in teacher_records_raw:
        key = (record['class'], record['subject'])
        if key not in unique_records:
            unique_records[key] = record

    teacher_records = list(unique_records.values())
    
    # Підготувати дані по класах та предметах
    teacher_data = {}
    for class_name, subjects in school_data['teachers'][teacher_name].items():
        teacher_data[class_name] = {}
        for subject in subjects:
            # Знайти запис для цього предмету
            record = next((r for r in teacher_records if r['class'] == class_name and r['subject'] == subject), None)
            
            teacher_data[class_name][subject] = {
                'filled': bool(record),
                'statistics': record.get('statistics', {}) if record else {},
                'student_count': record.get('student_count', 0) if record else 0,
                'semester': record.get('semester', 1) if record else 1,
                'updated_at': record.get('updated_at') if record else None
            }
    
    # Загальна статистика (рахуємо тільки унікальні комбінації)
    total_subjects = sum(len(subjects) for subjects in school_data['teachers'][teacher_name].values())

    # Підрахунок заповнених предметів через aggregation pipeline
    pipeline = [
        {"$match": {"teacher": teacher_name}},
        {"$group": {
            "_id": {
                "class": "$class",
                "subject": "$subject"
            }
        }},
        {"$count": "unique_count"}
    ]
    result = list(db_mongo.monitoring_collection.aggregate(pipeline))
    filled_subjects = result[0]['unique_count'] if result else 0
    progress = (filled_subjects / total_subjects * 100) if total_subjects > 0 else 0
    
    return render_template('superadmin_teacher_detail.html',
                         teacher_name=teacher_name,
                         teacher_data=teacher_data,
                         total_subjects=total_subjects,
                         filled_subjects=filled_subjects,
                         progress=round(progress, 1),
                         user_name=session['name'])

@app.route('/analytics')
@role_required(['superadmin', 'admin'])
def analytics():
    """Сторінка аналітики для адміністрації"""
    academic_years = get_academic_years()
    return render_template('analytics.html', 
                         academic_years=academic_years,
                         user_name=session.get('name'))


@app.route('/api/analytics/class-comparison/<year>/<semester>')
@role_required(['superadmin', 'admin'])
def api_class_comparison(year, semester):
    """API: Порівняння класів"""
    data = db_mongo.get_class_comparison(year, int(semester))
    return jsonify(data)


@app.route('/api/analytics/level-distribution/<year>/<semester>')
@role_required(['superadmin', 'admin'])
def get_level_distribution(year, semester):
    class_name = request.args.get('class')
    
    # Отримати дані розподілу
    distribution = db_mongo.get_level_distribution(year, int(semester), class_name)
    
    # ✅ ДОДАТИ: Отримати детальну інформацію для початкового рівня
    if not class_name:  # Тільки для режиму "всі класи"
        initial_details = db_mongo.get_initial_level_details(year, int(semester))
        distribution['initial_details'] = initial_details
    
    return jsonify(distribution)


@app.route('/api/analytics/subject-analysis/<year>/<semester>')
@role_required(['superadmin', 'admin'])
def api_subject_analysis(year, semester):
    """API: Аналіз по предметах"""
    data = db_mongo.get_subject_analysis(year, int(semester))
    return jsonify(data)


@app.route('/api/analytics/semester-comparison/<year>')
@role_required(['superadmin', 'admin'])
def api_semester_comparison(year):
    """API: Порівняння семестрів"""
    class_name = request.args.get('class', None)
    data = db_mongo.get_semester_comparison(year, class_name)
    return jsonify(data)


@app.route('/api/analytics/top-bottom/<year>/<semester>')
@role_required(['superadmin', 'admin'])
def api_top_bottom(year, semester):
    """API: Топ та аутсайдери"""
    limit = request.args.get('limit', 5, type=int)
    data = db_mongo.get_top_bottom_classes(year, int(semester), limit)
    return jsonify(data)

@app.route('/api/analytics/class-subjects/<year>/<semester>/<class_name>')
@role_required(['superadmin', 'admin'])
def api_class_subjects(year, semester, class_name):
    """API: Предмети конкретного класу"""
    data = db_mongo.get_class_subjects_comparison(year, int(semester), class_name)
    return jsonify(data)


@app.route('/api/analytics/class-quality/<year>/<semester>/<class_name>')
@role_required(['superadmin', 'admin'])
def api_class_quality(year, semester, class_name):
    """API: КЯЗ по предметах класу"""
    data = db_mongo.get_class_quality_comparison(year, int(semester), class_name)
    return jsonify(data)


@app.route('/api/analytics/class-result/<year>/<semester>/<class_name>')
@role_required(['superadmin', 'admin'])
def api_class_result(year, semester, class_name):
    """API: КР по предметах класу"""
    data = db_mongo.get_class_result_comparison(year, int(semester), class_name)
    return jsonify(data)


@app.route('/api/analytics/class-teachers/<year>/<semester>/<class_name>')
@role_required(['superadmin', 'admin'])
def api_class_teachers(year, semester, class_name):
    """API: Вчителі класу"""
    data = db_mongo.get_class_teachers_comparison(year, int(semester), class_name)
    return jsonify(data)


@app.route('/api/analytics/class-dynamics/<year>/<class_name>')
@role_required(['superadmin', 'admin'])
def api_class_dynamics(year, class_name):
    """API: Динаміка класу"""
    data = db_mongo.get_class_semester_dynamics(year, class_name)
    return jsonify(data)


@app.route('/api/analytics/class-top-bottom/<year>/<semester>/<class_name>')
@role_required(['superadmin', 'admin'])
def api_class_top_bottom(year, semester, class_name):
    """API: Топ та аутсайдери предметів"""
    limit = request.args.get('limit', 5, type=int)
    data = db_mongo.get_class_top_bottom_subjects(year, int(semester), class_name, limit)
    return jsonify(data)


@app.route('/api/analytics/parallel-classes/<year>/<semester>/<class_name>')
@role_required(['superadmin', 'admin'])
def api_parallel_classes(year, semester, class_name):
    """API: Порівняння з паралельними класами"""
    data = db_mongo.get_parallel_classes_comparison(year, int(semester), class_name)
    return jsonify(data)


@app.route('/api/analytics/class-detailed/<year>/<semester>/<class_name>')
@role_required(['superadmin', 'admin'])
def api_class_detailed(year, semester, class_name):
    """API: Детальна таблиця класу"""
    data = db_mongo.get_class_detailed_table(year, int(semester), class_name)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)