#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Синхронізація school_data.json з MongoDB Atlas
Запускати після кожного оновлення school_data.json
"""

import json
from db_mongo import db

def sync_school_data():
    """Оновити школьні дані з school_data.json"""
    print("=" * 60)
    print("СИНХРОНІЗАЦІЯ school_data.json → MongoDB Atlas")
    print("=" * 60)
    
    with open('data/school_data.json', 'r', encoding='utf-8') as f:
        school_data = json.load(f)
    
    # Видалити стару колекцію
    result = db['school_data'].delete_many({})
    print(f"✓ Видалено старих записів: {result.deleted_count}")
    
    # Вставити нові дані
    db['school_data'].insert_one(school_data)
    print(f"✓ Додано класів: {len(school_data['classes'])}")
    print(f"✓ Додано вчителів: {len(school_data['teachers'])}")
    
    # Перевірка
    updated = db['school_data'].find_one()
    pashnik_data = updated['teachers'].get('Пашник Тетяна Миколаївна', {})
    
    if '6-Б' in pashnik_data:
        print(f"✓ Перевірка: 6-Б у Пашник - {pashnik_data['6-Б']}")
    else:
        print("✗ ПОМИЛКА: 6-Б не знайдено у Пашник!")
    
    print("=" * 60)
    print("СИНХРОНІЗАЦІЯ ЗАВЕРШЕНА!")
    print("=" * 60)

if __name__ == '__main__':
    sync_school_data()