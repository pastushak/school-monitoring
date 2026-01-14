# utils/decorators.py
"""Декоратори для маршрутів"""
from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """Перевірка чи користувач залогінений"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Будь ласка, увійдіть в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    """Перевірка ролі користувача"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_email' not in session:
                flash('Будь ласка, увійдіть в систему', 'warning')
                return redirect(url_for('login'))
            
            user_role = session.get('user_role')
            if user_role not in allowed_roles:
                flash('У вас немає доступу до цієї сторінки', 'error')
                return redirect(url_for('mode_selection'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Перевірка чи користувач є адміном"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Будь ласка, увійдіть в систему', 'warning')
            return redirect(url_for('login'))
        
        user_role = session.get('user_role')
        if user_role not in ['admin', 'superadmin']:
            flash('Доступ заборонено', 'error')
            return redirect(url_for('mode_selection'))
        
        return f(*args, **kwargs)
    return decorated_function
