# models/monitoring.py
"""Pydantic моделі для валідації даних моніторингу"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class GradesModel(BaseModel):
    """Модель для оцінок"""
    grade_12: int = Field(ge=0, le=50, alias='grade12')
    grade_11: int = Field(ge=0, le=50, alias='grade11')
    grade_10: int = Field(ge=0, le=50, alias='grade10')
    grade_9: int = Field(ge=0, le=50, alias='grade9')
    grade_8: int = Field(ge=0, le=50, alias='grade8')
    grade_7: int = Field(ge=0, le=50, alias='grade7')
    grade_6: int = Field(ge=0, le=50, alias='grade6')
    grade_5: int = Field(ge=0, le=50, alias='grade5')
    grade_4: int = Field(ge=0, le=50, alias='grade4')
    grade_3: int = Field(ge=0, le=50, alias='grade3')
    grade_2: int = Field(ge=0, le=50, alias='grade2')
    grade_1: int = Field(ge=0, le=50, alias='grade1')
    
    model_config = {'populate_by_name': True}


class StatisticsModel(BaseModel):
    """Модель для статистики"""
    avgScore: str = Field(pattern=r'^\d+(\.\d+)?$')
    qualityCoeff: str = Field(pattern=r'^\d+(\.\d+)?%$')
    learningLevel: Optional[str] = None
    qualityPercent: Optional[str] = None
    resultCoeff: Optional[str] = None
    successCoeff: Optional[str] = None  # Зробити опціональним


class MonitoringDataModel(BaseModel):
    """Модель для даних моніторингу"""
    year: str = Field(pattern=r'^\d{4}-\d{4}$')
    class_name: str = Field(alias='class', pattern=r'^\d{1,2}-[А-ЯІЄЇҐ]$')
    teacher: str = Field(min_length=5, max_length=100)
    subject: str = Field(min_length=3, max_length=100)
    student_count: int = Field(ge=1, le=50)
    semester: int = Field(ge=1, le=2)
    grades: GradesModel
    statistics: StatisticsModel
    freed_count: Optional[int] = Field(default=0, ge=0, le=50)

    model_config = {'populate_by_name': True}

    @field_validator('teacher')
    def validate_teacher_name(cls, v):
        # Дозволити email або ПІБ
        if '@' in v:
            return v
        if re.match(r'^[А-ЯІЄЇҐ][а-яієїґ\'\-]+ [А-ЯІЄЇҐ][а-яієїґ\'\-]+ [А-ЯІЄЇҐ][а-яієїґ\'\-]+$', v):
            return v
        raise ValueError('Teacher must be email or full name')

    @field_validator('subject')
    def validate_subject(cls, v):
        if not re.match(r'^[А-ЯІЄЇҐа-яієїґ\s\'\-]+$', v):
            raise ValueError('Subject format error')
        return v