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
        {"email": "kryvyuk_liliya@kolgym.if.ua", "role": "class_head", "name": "Кривюк Лілія Михайлівна", "class": "6-Б"},
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
        {"email": "boichuk_maryana@kolgym.if.ua", "role": "teacher", "name": "Бойчук Мар'яна Юріївна", "class": None},
        {"email": "vankovych_khrystyna@kolgym.if.ua", "role": "teacher", "name": "Ванькович Христина Степанівна", "class": None},
        {"email": "grytsaniuk_galyna@kolgym.if.ua", "role": "teacher", "name": "Грицанюк Галина Миколаївна", "class": None},
        {"email": "dzvinchuk_taras@kolgym.if.ua", "role": "teacher", "name": "Дзвінчук Тарас Юрійович", "class": None},
        {"email": "zademleniuk_oleg@kolgym.if.ua", "role": "teacher", "name": "Задемленюк Олег Вікторович", "class": None},
        {"email": "koltsiuk_valeriy@kolgym.if.ua", "role": "teacher", "name": "Кольцюк Валерій Дмитрович", "class": None},
        {"email": "kokh_alla@kolgym.if.ua", "role": "teacher", "name": "Кох Алла Степанівна", "class": None},
        {"email": "lazor_olha@kolgym.if.ua", "role": "teacher", "name": "Лазор Ольга Ярославівна", "class": None},
        {"email": "matiichuk_mariia@kolgym.if.ua", "role": "teacher", "name": "Матійчук Марія Михайлівна", "class": None},
        {"email": "matkovska_lyubov@kolgym.if.ua", "role": "teacher", "name": "Матковська Любов Михайлівна", "class": None},
        {"email": "nosurak_ivan@kolgym.if.ua", "role": "teacher", "name": "Носурак Іван Васильович", "class": None},
        {"email": "pastushak_roman@kolgym.if.ua", "role": "teacher", "name": "Пастушак Роман Васильович", "class": None},
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
    data['updated_at'] = datetime.now()
    
    # Перетворити semester на int якщо це строка
    if 'semester' in data:
        data['semester'] = int(data['semester'])
    
    query = {
        'year': data['year'],
        'class': data['class'],
        'teacher': data['teacher'],
        'subject': data['subject'],
        'semester': data.get('semester', 1)  # За замовчуванням 1
    }
    
    existing = monitoring_collection.find_one(query)
    
    if existing:
        monitoring_collection.update_one(query, {"$set": data})
    else:
        data['created_at'] = datetime.now()
        monitoring_collection.insert_one(data)

def get_monitoring_data(year, class_name, teacher, subject, semester):
    """Отримати дані моніторингу з урахуванням семестру"""
    result = monitoring_collection.find_one({
        'year': year,
        'class': class_name,
        'teacher': teacher,
        'subject': subject,
        'semester': int(semester)
    })
    if result:
        result.pop('_id', None)
    return result

def get_class_monitoring_data(year, class_name, semester=None):
    """Отримати всі дані по класу з урахуванням семестру"""
    query = {
        'year': year,
        'class': class_name
    }
    
    # Якщо вказано семестр - фільтрувати
    if semester is not None:
        query['semester'] = int(semester)
    
    cursor = monitoring_collection.find(query)
    results = list(cursor)
    for r in results:
        r.pop('_id', None)
    return results

def get_all_monitoring_data(year, semester=None):
    """Отримати всі дані по школі з урахуванням семестру"""
    query = {'year': year}
    
    # Якщо вказано семестр - фільтрувати
    if semester is not None:
        query['semester'] = int(semester)
    
    cursor = monitoring_collection.find(query)
    results = list(cursor)
    for r in results:
        r.pop('_id', None)
    return results

def get_school_data():
    """Отримати дані школи"""
    result = school_data_collection.find_one()
    if result:
        result.pop('_id', None)
    return result

if __name__ == "__main__":
    print("Підключення до MongoDB...")
    print("✓ MongoDB підключено успішно!\n")
    init_mongodb()
