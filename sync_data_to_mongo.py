#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Синхронізація даних з JSON файлів до MongoDB
"""

import json
from db_mongo import db

def sync_users():
    """Оновити користувачів з users.json"""
    print("Синхронізація користувачів...")
    
    with open('data/users.json', 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    for email, user_info in users_data.items():
        # Оновити або вставити користувача
        db['users'].update_one(
            {'email': email},
            {'$set': {
                'email': email,
                'name': user_info['name'],
                'role': user_info['role'],
                'class': user_info.get('class')
            }},
            upsert=True
        )
        print(f"✓ {user_info['name']}")
    
    print(f"Оновлено {len(users_data)} користувачів\n")

def sync_school_data():
    """Оновити школьні дані з school_data.json"""
    print("Синхронізація школьних даних...")
    
    with open('data/school_data.json', 'r', encoding='utf-8') as f:
        school_data = json.load(f)
    
    # Оновити school_data
    db['school_data'].delete_many({})  # Очистити
    db['school_data'].insert_one(school_data)
    
    print(f"✓ Класи: {len(school_data['classes'])}")
    print(f"✓ Вчителі: {len(school_data['teachers'])}\n")

if __name__ == '__main__':
    print("=" * 50)
    print("СИНХРОНІЗАЦІЯ ДАНИХ З JSON → MongoDB")
    print("=" * 50)
    
    sync_users()
    sync_school_data()
    
    print("=" * 50)
    print("СИНХРОНІЗАЦІЯ ЗАВЕРШЕНА!")
    print("=" * 50)