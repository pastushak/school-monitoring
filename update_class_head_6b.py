#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Оновлення класного керівника 6-Б класу
Кривюк Лілія Михайлівна → Бойчук Мар'яна Юріївна
"""

from db_mongo import users_collection
from datetime import datetime

print("=" * 60)
print("ОНОВЛЕННЯ КЛАСНОГО КЕРІВНИКА 6-Б")
print("=" * 60)

# 1. Зняти роль класного керівника з Кривюк Л.М.
result1 = users_collection.update_one(
    {"email": "kryvyuk_liliya@kolgym.if.ua"},
    {"$set": {
        "role": "teacher",
        "class": None,
        "updated_at": datetime.now()
    }}
)
print(f"✓ Кривюк Л.М. → teacher (оновлено: {result1.modified_count})")

# 2. Призначити Бойчук М.Ю. класним керівником 6-Б
result2 = users_collection.update_one(
    {"email": "boichuk_maryana@kolgym.if.ua"},
    {"$set": {
        "role": "class_head",
        "class": "6-Б",
        "updated_at": datetime.now()
    }}
)
print(f"✓ Бойчук М.Ю. → class_head 6-Б (оновлено: {result2.modified_count})")

# 3. Перевірка
print("\nПеревірка оновлень:")
kryvyuk = users_collection.find_one({"email": "kryvyuk_liliya@kolgym.if.ua"})
boichuk = users_collection.find_one({"email": "boichuk_maryana@kolgym.if.ua"})

print(f"  Кривюк Л.М.: role={kryvyuk['role']}, class={kryvyuk['class']}")
print(f"  Бойчук М.Ю.: role={boichuk['role']}, class={boichuk['class']}")

print("=" * 60)
print("✓ ОНОВЛЕННЯ ЗАВЕРШЕНО!")
print("=" * 60)