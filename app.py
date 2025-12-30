from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from datetime import datetime
import os
from dotenv import load_dotenv
import db_mongo
import export_excel

# Версія додатку
APP_VERSION = "1.2.0"
APP_UPDATE_DATE = "27.12.2024"

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

# Викликати при старті застосунку
sync_school_data_on_startup()

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
        
        session['available_roles'] = available_roles
        
        # Перенаправлення
        if len(available_roles) > 1:
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
        return jsonify({'success': False, 'error': 'Немає прав доступу'})
    
    data = request.json
    db_mongo.save_monitoring_data(data)
    
    return jsonify({'success': True})

@app.route('/get_monitoring/<year>/<class_name>/<teacher>/<subject>/<semester>')
def get_monitoring(year, class_name, teacher, subject, semester):
    data = db_mongo.get_monitoring_data(year, class_name, teacher, subject, semester)
    return jsonify(data if data else {})

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
            class_data.append({
                'subject': info['subject'],
                'teacher': info['teacher'],
                'statistics': record['statistics'],
                'grades': record['grades'],
                'student_count': record['student_count'],
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
    
    for class_name in school_data['classes'].keys():
        # Підрахувати предмети для класу
        class_subjects = []
        for teacher, classes in school_data.get('teachers', {}).items():
            if class_name in classes:
                for subject in classes[class_name]:
                    class_subjects.append(f"{class_name}_{teacher}_{subject}")
        
        class_total = len(class_subjects)
        class_filled = sum(1 for key in class_subjects if key in monitoring_dict)
        
        total_subjects += class_total
        filled_subjects += class_filled
        
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
    
    # Отримати дані моніторингу
    monitoring_data = db_mongo.get_monitoring_data(year, class_name, teacher, subject)
    
    if not monitoring_data:
        return "Дані не знайдено", 404
    
    # Створити Excel файл
    excel_file = export_excel.create_teacher_report_excel(
        monitoring_data,
        year,
        class_name,
        teacher,
        subject,
        'I' if semester == '1' else 'II'
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)