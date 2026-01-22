from db_mongo import monitoring_collection, users_collection

def migrate_teacher_emails():
    """Замінити email на ПІБ у всіх записах моніторингу"""
    print("=" * 80)
    print("МІГРАЦІЯ: email → ПІБ вчителів")
    print("=" * 80)
    
    # Знайти всі унікальні email у моніторингу
    teacher_emails = monitoring_collection.distinct("teacher")
    email_teachers = [t for t in teacher_emails if '@' in t]
    
    print(f"\nЗнайдено вчителів з email: {len(email_teachers)}")
    
    if not email_teachers:
        print("✓ Всі записи вже мають ПІБ")
        return
    
    total_updated = 0
    
    for email in email_teachers:
        # Знайти ПІБ в users
        user = users_collection.find_one({"email": email})
        
        if not user:
            print(f"⚠️  Email не знайдено в users: {email}")
            continue
        
        full_name = user.get('name')
        
        # Порахувати скільки записів
        count = monitoring_collection.count_documents({"teacher": email})
        
        print(f"\n{email}")
        print(f"  → {full_name}")
        print(f"  Записів: {count}")
        
        # Оновити всі записи
        result = monitoring_collection.update_many(
            {"teacher": email},
            {"$set": {"teacher": full_name}}
        )
        
        print(f"  ✅ Оновлено: {result.modified_count}")
        total_updated += result.modified_count
    
    print("\n" + "=" * 80)
    print(f"✅ МІГРАЦІЯ ЗАВЕРШЕНА! Оновлено {total_updated} записів")
    print("=" * 80)

if __name__ == '__main__':
    migrate_teacher_emails()