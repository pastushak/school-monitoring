from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Завантажити змінні середовища
load_dotenv()

# Підключення до MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client.school_monitoring

# Колекції
users_collection = db.users
monitoring_collection = db.monitoring_data
school_data_collection = db.school_data

def init_mongodb():
    """Ініціалізація даних у MongoDB"""
    
    # Перевірити чи є дані
    if users_collection.count_documents({}) > 0:
        print("MongoDB вже ініціалізовано")
        return
    
    print("Ініціалізація MongoDB...")
    
    # Додати користувачів
    users = [
        {"email": "tkachuk_volodymyr@kolgym.if.ua", "role": "admin", "name": "Ткачук Володимир Михайлович", "class": None},
        {"email": "kushytckyy_roman1@kolgym.if.ua", "role": "admin", "name": "Кушицький Роман Зеновійович", "class": None},
        {"email": "fedoryshyna_olena@kolgym.if.ua", "role": "admin", "name": "Федоришин Олена Миколаївна", "class": None},
        {"email": "sembratovych_lyubov@kolgym.if.ua", "role": "admin", "name": "Сембратович Любов Василівна", "class": None},
        {"email": "zademlenyuk_iryna@kolgym.if.ua", "role": "admin", "name": "Задемленюк Ірина Тарасівна", "class": None},
        {"email": "kudyba_liliya@kolgym.if.ua", "role": "class_head", "name": "Кудиба Лілія Богданівна", "class": "5-А"},
        {"email": "filonenko_iryna@kolgym.if.ua", "role": "class_head", "name": "Філоненко Ірина Миколаївна", "class": "6-А"},
        {"email": "boichuk_maryana@kolgym.if.ua", "role": "class_head", "name": "Бойчук Мар'яна Юріївна", "class": "6-Б"},
        {"email": "tytyk_svitlana@kolgym.if.ua", "role": "class_head", "name": "Титик Світлана Григорівна", "class": "7-А"},
        {"email": "vasylkova_iryna@kolgym.if.ua", "role": "class_head", "name": "Василькова Ірина Василівна", "class": "7-Б"},
        {"email": "pertsovych_dariya@kolgym.if.ua", "role": "class_head", "name": "Перцович Дарія Несторівна", "class": "8-А"},
        {"email": "pashnyk_tetyana@kolgym.if.ua", "role": "class_head", "name": "Пашник Тетяна Миколаївна", "class": "8-Б"},
        {"email": "ilkiv_nataliya@kolgym.if.ua", "role": "class_head", "name": "Ільків Наталія Валентинівна", "class": "9-А"},
        {"email": "andreychenko_lesya@kolgym.if.ua", "role": "class_head", "name": "Андрейченко Леся Євгенівна", "class": "9-Б"},
        {"email": "jaremczuk_iryna@kolgym.if.ua", "role": "class_head", "name": "Яремчук Ірина Михайлівна", "class": "10-А"},
        {"email": "vovk_mariya@kolgym.if.ua", "role": "class_head", "name": "Вовк Марія Василівна", "class": "10-Б"},
        {"email": "boledzyuk_iryna@kolgym.if.ua", "role": "class_head", "name": "Боледзюк Ірина Степанівна", "class": "11-А"},
        {"email": "petranyuk_ulyana@kolgym.if.ua", "role": "class_head", "name": "Петранюк Уляна Василівна", "class": "11-Б"},
        {"email": "boytsan_larysa@kolgym.if.ua", "role": "teacher", "name": "Бойцан Лариса Василівна", "class": None},
        {"email": "vankovych_khrystyna@kolgym.if.ua", "role": "teacher", "name": "Ванькович Христина Степанівна", "class": None},
        {"email": "grytsaniuk_galyna@kolgym.if.ua", "role": "teacher", "name": "Грицанюк Галина Миколаївна", "class": None},
        {"email": "dzvinchuk_taras@kolgym.if.ua", "role": "teacher", "name": "Дзвінчук Тарас Юрійович", "class": None},
        {"email": "zademleniuk_oleg@kolgym.if.ua", "role": "teacher", "name": "Задемленюк Олег Вікторович", "class": None},
        {"email": "kryvyuk_liliya@kolgym.if.ua", "role": "teacher", "name": "Кривюк Лілія Михайлівна", "class": None},
        {"email": "koltsiuk_valeriy@kolgym.if.ua", "role": "teacher", "name": "Кольцюк Валерій Дмитрович", "class": None},
        {"email": "kokh_alla@kolgym.if.ua", "role": "teacher", "name": "Кох Алла Степанівна", "class": None},
        {"email": "lazor_olha@kolgym.if.ua", "role": "teacher", "name": "Лазор Ольга Ярославівна", "class": None},
        {"email": "matiichuk_mariia@kolgym.if.ua", "role": "teacher", "name": "Матійчук Марія Михайлівна", "class": None},
        {"email": "matkovska_lyubov@kolgym.if.ua", "role": "teacher", "name": "Матковська Любов Михайлівна", "class": None},
        {"email": "nosurak_ivan@kolgym.if.ua", "role": "teacher", "name": "Носурак Іван Васильович", "class": None},
        {"email": "tkachuk_oksana@kolgym.if.ua", "role": "teacher", "name": "Ткачук Оксана Євгенівна", "class": None},
        {"email": "pastushak_roman@kolgym.if.ua", "role": "superadmin", "name": "Пастушак Роман Васильович", "class": None},
        {"email": "pashko_tetyana@kolgym.if.ua", "role": "teacher", "name": "Пашко Тетяна Миколаївна", "class": None},
        {"email": "fedorak_olena@kolgym.if.ua", "role": "teacher", "name": "Федорак Олена Ігорівна", "class": None},
    ]
    
    users_collection.insert_many(users)
    print(f"✓ Додано {len(users)} користувачів")
    
    # Додати дані школи (скорочена версія, повну додамо пізніше)
    school_data = {
        "academic_years": ["2025-2026"],
        "classes": {
            "5-А": 32, "6-А": 31, "6-Б": 31, "7-А": 29, "7-Б": 30,
            "8-А": 26, "8-Б": 28, "9-А": 35, "9-Б": 36,
            "10-А": 23, "10-Б": 18, "11-А": 26, "11-Б": 26
        },
        "teachers": {
            "Петранюк Уляна Василівна": {
                "5-А": ["Українська мова", "Українська література"],
                "6-А": ["Українська мова"],
                "6-Б": ["Українська мова"],
                "10-А": ["Українська мова"],
                "11-Б": ["Українська мова", "Українська література"]
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
            }
        }
    }
    
    school_data_collection.insert_one(school_data)
    print("✓ Додано дані школи")
    
    print("\n🎉 MongoDB успішно ініціалізовано!")

def get_user_by_email(email):
    """Отримати користувача за email"""
    return users_collection.find_one({"email": email})

def save_monitoring_data(data):
    """Зберегти дані моніторингу з урахуванням семестру"""
    
    # ✅ ВИПРАВЛЕНО: Створити індекс для швидшого пошуку
    try:
        monitoring_collection.create_index([
            ('year', 1),
            ('class', 1),
            ('teacher', 1),
            ('subject', 1),
            ('semester', 1)
        ], unique=True, background=True, name='monitoring_unique_index')
    except Exception as e:
        pass
    
    # Додати timestamp оновлення
    data['updated_at'] = datetime.now()
    
    # Перетворити semester на int якщо це строка
    if 'semester' in data:
        data['semester'] = int(data['semester'])
    
    # Підготувати фільтр для пошуку
    query = {
        'year': data['year'],
        'class': data['class'],
        'teacher': data['teacher'],
        'subject': data['subject'],
        'semester': data.get('semester', 1)
    }
    
    print(f"[SAVE] Query: {query}")
    
    # Перевірити чи існує запис
    existing = monitoring_collection.find_one(query)
    
    if existing:
        result = monitoring_collection.update_one(query, {"$set": data}, upsert=True)
        print(f"[SAVE] Updated existing record, matched: {result.matched_count}, modified: {result.modified_count}")
    else:
        data['created_at'] = datetime.now()
        result = monitoring_collection.insert_one(data)
        print(f"[SAVE] Inserted new record, id: {result.inserted_id}")
    
    # ✅ ВИПРАВЛЕНО: Примусово синхронізувати
    try:
        client.admin.command('fsync', lock=False)
        print(f"[SAVE] fsync completed successfully")
    except Exception as e:
        print(f"[SAVE] fsync skipped or failed: {e}")
    
    # Перевірка
    saved = monitoring_collection.find_one(query)
    if saved:
        print(f"[SAVE] Verification: Data saved successfully")
        return True
    else:
        print(f"[SAVE] WARNING: Data not found after save!")
        return False

def get_monitoring_data(year, class_name, teacher, subject, semester):
    """Отримати дані моніторингу"""
    # Перетворити semester на int
    if isinstance(semester, str):
        semester = int(semester)
    
    query = {
        'year': year,
        'class': class_name,
        'teacher': teacher,
        'subject': subject,
        'semester': semester
    }
    
    print(f"[GET] Query: {query}")
    
    result = monitoring_collection.find_one(query)
    
    if result:
        print(f"[GET] Found record, updated_at: {result.get('updated_at')}")
        # ✅ ВИПРАВЛЕНО: Видалити _id перед поверненням
        if '_id' in result:
            del result['_id']
    else:
        print(f"[GET] No record found")
    
    return result

def get_class_monitoring_data(year, class_name, semester=None):
    """Отримати всі дані по класу з урахуванням семестру"""
    query = {
        'year': year,
        'class': class_name
    }
    
    if semester is not None:
        query['semester'] = int(semester)
    
    cursor = monitoring_collection.find(query)
    results = list(cursor)
    
    # ✅ ВИПРАВЛЕНО: Видалити _id з кожного результату
    for r in results:
        if '_id' in r:
            del r['_id']
    
    return results

def get_all_monitoring_data(year, semester=None):
    """Отримати всі дані по школі з урахуванням семестру"""
    query = {'year': year}
    
    if semester is not None:
        query['semester'] = int(semester)
    
    cursor = monitoring_collection.find(query)
    results = list(cursor)
    
    # ✅ ВИПРАВЛЕНО: Видалити _id з кожного результату
    for r in results:
        if '_id' in r:
            del r['_id']
    
    return results

def get_school_data():
    """Отримати дані школи"""
    result = school_data_collection.find_one()
    
    # ✅ ВИПРАВЛЕНО: Видалити _id
    if result and '_id' in result:
        del result['_id']
    
    return result

def get_analytics_data(year, semester=None, class_name=None):
    """Отримати дані для аналітики з фільтрами"""
    query = {'year': year}
    
    if semester:
        query['semester'] = int(semester)
    
    if class_name:
        query['class'] = class_name
    
    data = list(monitoring_collection.find(query))
    
    # ✅ ВИПРАВЛЕНО: Видалити _id з кожного результату
    for item in data:
        if '_id' in item:
            del item['_id']
    
    return data


def get_class_comparison(year, semester):
    """Порівняння класів за середнім балом"""
    data = get_analytics_data(year, semester)
    
    class_stats = {}
    for record in data:
        class_name = record['class']
        if class_name not in class_stats:
            class_stats[class_name] = {
                'subjects': [],
                'avg_scores': [],
                'quality_coeffs': [],
                'result_coeffs': []
            }
        
        stats = record.get('statistics', {})
        class_stats[class_name]['subjects'].append(record['subject'])
        class_stats[class_name]['avg_scores'].append(float(stats.get('avgScore', 0)))
        class_stats[class_name]['quality_coeffs'].append(
            float(stats.get('qualityCoeff', '0%').replace('%', ''))
        )
        class_stats[class_name]['result_coeffs'].append(
            float(stats.get('resultCoeff', '0%').replace('%', ''))
        )
    
    result = []
    for class_name, data in sorted(class_stats.items()):
        if data['avg_scores']:
            result.append({
                'class': class_name,
                'avg_score': round(sum(data['avg_scores']) / len(data['avg_scores']), 2),
                'avg_quality': round(sum(data['quality_coeffs']) / len(data['quality_coeffs']), 2),
                'avg_result': round(sum(data['result_coeffs']) / len(data['result_coeffs']), 2),
                'subjects_count': len(data['subjects'])
            })
    
    return result


def get_level_distribution(year, semester, class_name=None):
    """Розподіл учнів по рівнях навченості"""
    data = get_analytics_data(year, semester, class_name)
    
    if not data:
        return {
            'high': 0, 'sufficient': 0, 'average': 0, 'initial': 0,
            'high_percent': 0, 'sufficient_percent': 0, 
            'average_percent': 0, 'initial_percent': 0
        }
    
    total_high_pct = 0
    total_sufficient_pct = 0
    total_average_pct = 0
    total_initial_pct = 0
    
    for record in data:
        grades = record.get('grades', {})
        student_count = record.get('student_count', 0)
        
        if student_count == 0:
            continue
        
        high = (int(grades.get('grade12', 0)) + 
                int(grades.get('grade11', 0)) + 
                int(grades.get('grade10', 0)))
        
        sufficient = (int(grades.get('grade9', 0)) + 
                     int(grades.get('grade8', 0)) + 
                     int(grades.get('grade7', 0)))
        
        average = (int(grades.get('grade6', 0)) + 
                  int(grades.get('grade5', 0)) + 
                  int(grades.get('grade4', 0)))
        
        initial = (int(grades.get('grade3', 0)) + 
                  int(grades.get('grade2', 0)) + 
                  int(grades.get('grade1', 0)))
        
        total_high_pct += (high / student_count * 100)
        total_sufficient_pct += (sufficient / student_count * 100)
        total_average_pct += (average / student_count * 100)
        total_initial_pct += (initial / student_count * 100)
    
    num_records = len(data)
    
    return {
        'high': round(total_high_pct / num_records, 1) if num_records > 0 else 0,
        'sufficient': round(total_sufficient_pct / num_records, 1) if num_records > 0 else 0,
        'average': round(total_average_pct / num_records, 1) if num_records > 0 else 0,
        'initial': round(total_initial_pct / num_records, 1) if num_records > 0 else 0,
        'high_percent': round(total_high_pct / num_records, 1) if num_records > 0 else 0,
        'sufficient_percent': round(total_sufficient_pct / num_records, 1) if num_records > 0 else 0,
        'average_percent': round(total_average_pct / num_records, 1) if num_records > 0 else 0,
        'initial_percent': round(total_initial_pct / num_records, 1) if num_records > 0 else 0
    }


def get_subject_analysis(year, semester):
    """Аналіз по предметах"""
    data = get_analytics_data(year, semester)
    
    subject_stats = {}
    for record in data:
        subject = record['subject']
        if subject not in subject_stats:
            subject_stats[subject] = {
                'avg_scores': [],
                'quality_coeffs': [],
                'classes': []
            }
        
        stats = record.get('statistics', {})
        subject_stats[subject]['avg_scores'].append(float(stats.get('avgScore', 0)))
        subject_stats[subject]['quality_coeffs'].append(
            float(stats.get('qualityCoeff', '0%').replace('%', ''))
        )
        
        if record['class'] not in subject_stats[subject]['classes']:
            subject_stats[subject]['classes'].append(record['class'])
    
    result = []
    for subject, data in sorted(subject_stats.items()):
        if data['avg_scores']:
            result.append({
                'subject': subject,
                'avg_score': round(sum(data['avg_scores']) / len(data['avg_scores']), 2),
                'avg_quality': round(sum(data['quality_coeffs']) / len(data['quality_coeffs']), 2),
                'classes_count': len(data['classes']),
                'classes': sorted(data['classes'])
            })
    
    result.sort(key=lambda x: x['avg_score'], reverse=True)
    
    return result


def get_semester_comparison(year, class_name=None):
    """Порівняння семестрів"""
    semester1_data = get_analytics_data(year, 1, class_name)
    semester2_data = get_analytics_data(year, 2, class_name)
    
    def calculate_average(data):
        if not data:
            return 0
        scores = [float(record.get('statistics', {}).get('avgScore', 0)) for record in data]
        return round(sum(scores) / len(scores), 2) if scores else 0
    
    return {
        'semester1': {
            'avg_score': calculate_average(semester1_data),
            'records_count': len(semester1_data)
        },
        'semester2': {
            'avg_score': calculate_average(semester2_data),
            'records_count': len(semester2_data)
        }
    }


def get_top_bottom_classes(year, semester, limit=5):
    """Топ та аутсайдери"""
    comparison = get_class_comparison(year, semester)
    
    if not comparison:
        return {'top': [], 'bottom': []}
    
    sorted_by_score = sorted(comparison, key=lambda x: x['avg_score'], reverse=True)
    
    return {
        'top': sorted_by_score[:limit],
        'bottom': sorted_by_score[-limit:][::-1]
    }

def get_class_subjects_comparison(year, semester, class_name):
    """Середній бал по предметах для конкретного класу"""
    data = get_analytics_data(year, semester, class_name)
    
    result = []
    for record in data:
        stats = record.get('statistics', {})
        result.append({
            'subject': record['subject'],
            'teacher': record['teacher'],
            'avg_score': float(stats.get('avgScore', 0)),
            'quality': float(stats.get('qualityCoeff', '0%').replace('%', '')),
            'result': float(stats.get('resultCoeff', '0%').replace('%', '')),
            'student_count': record.get('student_count', 0)
        })
    
    result.sort(key=lambda x: x['avg_score'], reverse=True)
    
    return result


def get_class_quality_comparison(year, semester, class_name):
    """КЯЗ по предметах для конкретного класу"""
    data = get_analytics_data(year, semester, class_name)
    
    result = []
    for record in data:
        stats = record.get('statistics', {})
        result.append({
            'subject': record['subject'],
            'teacher': record['teacher'],
            'quality': float(stats.get('qualityCoeff', '0%').replace('%', ''))
        })
    
    result.sort(key=lambda x: x['quality'], reverse=True)
    
    return result


def get_class_result_comparison(year, semester, class_name):
    """КР по предметах для конкретного класу"""
    data = get_analytics_data(year, semester, class_name)
    
    result = []
    for record in data:
        stats = record.get('statistics', {})
        result.append({
            'subject': record['subject'],
            'teacher': record['teacher'],
            'result': float(stats.get('resultCoeff', '0%').replace('%', ''))
        })
    
    result.sort(key=lambda x: x['result'], reverse=True)
    
    return result


def get_class_teachers_comparison(year, semester, class_name):
    """Порівняння вчителів у конкретному класі"""
    data = get_analytics_data(year, semester, class_name)
    
    teachers_stats = {}
    for record in data:
        teacher = record['teacher']
        if teacher not in teachers_stats:
            teachers_stats[teacher] = {
                'subjects': [],
                'avg_scores': [],
                'quality_coeffs': [],
                'result_coeffs': []
            }
        
        stats = record.get('statistics', {})
        teachers_stats[teacher]['subjects'].append(record['subject'])
        teachers_stats[teacher]['avg_scores'].append(float(stats.get('avgScore', 0)))
        teachers_stats[teacher]['quality_coeffs'].append(
            float(stats.get('qualityCoeff', '0%').replace('%', ''))
        )
        teachers_stats[teacher]['result_coeffs'].append(
            float(stats.get('resultCoeff', '0%').replace('%', ''))
        )
    
    result = []
    for teacher, data in teachers_stats.items():
        if data['avg_scores']:
            result.append({
                'teacher': teacher,
                'avg_score': round(sum(data['avg_scores']) / len(data['avg_scores']), 2),
                'avg_quality': round(sum(data['quality_coeffs']) / len(data['quality_coeffs']), 2),
                'avg_result': round(sum(data['result_coeffs']) / len(data['result_coeffs']), 2),
                'subjects': data['subjects']
            })
    
    return result


def get_class_semester_dynamics(year, class_name):
    """Динаміка класу по семестрах"""
    semester1_data = get_analytics_data(year, 1, class_name)
    semester2_data = get_analytics_data(year, 2, class_name)
    
    def calculate_stats(data):
        if not data:
            return {'avg_score': 0, 'avg_quality': 0, 'avg_result': 0, 'count': 0}
        
        scores = []
        qualities = []
        results = []
        
        for record in data:
            stats = record.get('statistics', {})
            scores.append(float(stats.get('avgScore', 0)))
            qualities.append(float(stats.get('qualityCoeff', '0%').replace('%', '')))
            results.append(float(stats.get('resultCoeff', '0%').replace('%', '')))
        
        return {
            'avg_score': round(sum(scores) / len(scores), 2) if scores else 0,
            'avg_quality': round(sum(qualities) / len(qualities), 2) if qualities else 0,
            'avg_result': round(sum(results) / len(results), 2) if results else 0,
            'count': len(data)
        }
    
    return {
        'semester1': calculate_stats(semester1_data),
        'semester2': calculate_stats(semester2_data)
    }


def get_class_top_bottom_subjects(year, semester, class_name, limit=5):
    """Топ та аутсайдери предметів для класу"""
    data = get_class_subjects_comparison(year, semester, class_name)
    
    if not data:
        return {'top': [], 'bottom': []}
    
    return {
        'top': data[:limit],
        'bottom': data[-limit:][::-1]
    }


def get_parallel_classes_comparison(year, semester, class_name):
    """Порівняння з паралельними класами"""
    grade = class_name.split('-')[0]
    
    school_data = get_school_data()
    parallel_classes = [cls for cls in school_data['classes'].keys() if cls.startswith(grade + '-')]
    
    result = []
    for cls in sorted(parallel_classes):
        cls_data = get_analytics_data(year, semester, cls)
        
        if cls_data:
            scores = [float(record.get('statistics', {}).get('avgScore', 0)) for record in cls_data]
            qualities = [float(record.get('statistics', {}).get('qualityCoeff', '0%').replace('%', '')) for record in cls_data]
            
            result.append({
                'class': cls,
                'avg_score': round(sum(scores) / len(scores), 2) if scores else 0,
                'avg_quality': round(sum(qualities) / len(qualities), 2) if qualities else 0,
                'subjects_count': len(cls_data),
                'is_current': cls == class_name
            })
    
    return result


def get_class_detailed_table(year, semester, class_name):
    """Детальна таблиця по предметах для класу"""
    data = get_analytics_data(year, semester, class_name)
    
    result = []
    for record in data:
        stats = record.get('statistics', {})
        grades = record.get('grades', {})
        
        high = (int(grades.get('grade12', 0)) + 
                int(grades.get('grade11', 0)) + 
                int(grades.get('grade10', 0)))
        sufficient = (int(grades.get('grade9', 0)) + 
                     int(grades.get('grade8', 0)) + 
                     int(grades.get('grade7', 0)))
        average = (int(grades.get('grade6', 0)) + 
                  int(grades.get('grade5', 0)) + 
                  int(grades.get('grade4', 0)))
        initial = (int(grades.get('grade3', 0)) + 
                  int(grades.get('grade2', 0)) + 
                  int(grades.get('grade1', 0)))
        
        student_count = record.get('student_count', 0)
        
        result.append({
            'subject': record['subject'],
            'teacher': record['teacher'],
            'student_count': student_count,
            'avg_score': stats.get('avgScore', '0'),
            'learning_level': stats.get('learningLevel', '0%'),
            'quality_coeff': stats.get('qualityCoeff', '0%'),
            'quality_percent': stats.get('qualityPercent', '0%'),
            'result_coeff': stats.get('resultCoeff', '0%'),
            'high': high,
            'sufficient': sufficient,
            'average': average,
            'initial': initial,
            'not_assessed': int(grades.get('gradeNA', 0))
        })
    
    return result

if __name__ == "__main__":
    print("Підключення до MongoDB...")
    print("✓ MongoDB підключено успішно!\n")
    init_mongodb()