"""
Експорт усіх Excel-звітів за 1 семестр 2025-2026.
Створює папку backups/2025-2026_semester1/excel_reports/ та зберігає:
- Zvit_shkola_2025-2026_1_semestr.xlsx (звіт по школі)
- Zvit_<клас>_2025-2026_1_semestr.xlsx (звіт по кожному з 13 класів)
"""

import os
import db_mongo
import export_excel


YEAR = '2025-2026'
SEMESTER = 1  # 1 семестр
SEMESTER_ROMAN = 'I'


def export_school_report(output_dir):
    """Експорт звіту по школі."""
    print("🏫 Експорт звіту по школі...")
    
    school_data = db_mongo.get_school_data()
    all_monitoring = db_mongo.get_all_monitoring_data(YEAR, SEMESTER)
    
    excel_file = export_excel.create_school_report_excel(
        school_data,
        all_monitoring,
        YEAR,
        SEMESTER_ROMAN
    )
    
    filename = f"Zvit_shkola_{YEAR}_{SEMESTER}_semestr.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(excel_file.getvalue())
    
    size_kb = os.path.getsize(filepath) / 1024
    print(f"  ✓ {filename}  ({size_kb:.1f} KB)")


def export_class_report(class_name, output_dir):
    """Експорт звіту по конкретному класу."""
    school_data = db_mongo.get_school_data()
    monitoring_data = db_mongo.get_class_monitoring_data(YEAR, class_name, SEMESTER)
    
    # Знайти класного керівника
    class_head_name = None
    all_users = list(db_mongo.users_collection.find({
        'role': {'$in': ['class_head', 'admin', 'superadmin']}
    }))
    for user in all_users:
        if user.get('class') == class_name:
            class_head_name = user.get('name')
            break
    
    # Зібрати дані як у get_class_report
    all_subjects = {}
    for teacher, classes in school_data.get('teachers', {}).items():
        if class_name in classes:
            for subject in classes[class_name]:
                all_subjects[f"{teacher}_{subject}"] = {
                    'teacher': teacher,
                    'subject': subject
                }
    
    monitoring_dict = {}
    for record in monitoring_data:
        key = f"{record['teacher']}_{record['subject']}"
        monitoring_dict[key] = record
    
    class_data = []
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
    
    if not class_data:
        print(f"  ⚠️  {class_name}: немає заповнених предметів — пропускаємо")
        return
    
    excel_file = export_excel.create_class_report_excel(
        class_data,
        class_name,
        YEAR,
        SEMESTER_ROMAN,
        class_head_name
    )
    
    filename = f"Zvit_{class_name}_{YEAR}_{SEMESTER}_semestr.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(excel_file.getvalue())
    
    size_kb = os.path.getsize(filepath) / 1024
    filled_count = len([d for d in class_data if d.get('filled')])
    print(f"  ✓ {filename}  ({size_kb:.1f} KB, заповнено: {filled_count})")


def main():
    print("=" * 70)
    print(f"📦 ЕКСПОРТ EXCEL-ЗВІТІВ ЗА {SEMESTER_ROMAN} СЕМЕСТР {YEAR}")
    print("=" * 70)
    
    # Створити папку
    output_dir = os.path.join('backups', f'{YEAR}_semester{SEMESTER}', 'excel_reports')
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n📁 Папка: {output_dir}\n")
    
    # 1. Звіт по школі
    export_school_report(output_dir)
    
    # 2. Звіти по класах
    print(f"\n📚 Експорт звітів по класах...")
    school_data = db_mongo.get_school_data()
    classes = sorted(school_data['classes'].keys(), key=lambda c: (int(c.split('-')[0]), c))
    
    for class_name in classes:
        export_class_report(class_name, output_dir)
    
    # Підсумок
    files = os.listdir(output_dir)
    total_size = sum(os.path.getsize(os.path.join(output_dir, f)) for f in files) / 1024
    
    print("\n" + "=" * 70)
    print("✅ ЕКСПОРТ ЗАВЕРШЕНО!")
    print("=" * 70)
    print(f"📁 Розташування: {os.path.abspath(output_dir)}")
    print(f"📄 Створено файлів: {len(files)}")
    print(f"💾 Загальний розмір: {total_size:.1f} KB")
    print("=" * 70)


if __name__ == '__main__':
    main()