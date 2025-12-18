from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime
import io

def create_teacher_report_excel(data, year, class_name, teacher, subject, semester):
    """Створити Excel звіт для вчителя"""
    
    wb = Workbook()
    ws = wb.active
    ws.title = f"{class_name}_{subject[:20]}"
    
    # Заголовок
    ws.merge_cells('A1:M1')
    title_cell = ws['A1']
    title_cell.value = f'Коломийський ліцей "Коломийська гімназія імені Михайла Грушевського"'
    title_cell.font = Font(size=14, bold=True)
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    ws.merge_cells('A2:M2')
    subtitle_cell = ws['A2']
    subtitle_cell.value = f'Звіт вчителя за {semester} семестр {year} н.р.'
    subtitle_cell.font = Font(size=12, bold=True)
    subtitle_cell.alignment = Alignment(horizontal='center')
    
    ws.merge_cells('A3:M3')
    info_cell = ws['A3']
    info_cell.value = f'Клас: {class_name} | Вчитель: {teacher} | Предмет: {subject}'
    info_cell.font = Font(size=11)
    info_cell.alignment = Alignment(horizontal='center')
    
    # Заголовки колонок
    headers = ['Учні', 'н/а', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=5, column=col, value=header)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
    
    # Дані (тут можна додати список учнів, якщо є)
    row = 6
    student_count = data.get('student_count', 0)
    grades = data.get('grades', {})
    
    # Показати розподіл оцінок
    ws.cell(row=row, column=1, value='Кількість учнів:').font = Font(bold=True)
    
    not_assessed = student_count
    for i in range(1, 13):
        grade_count = int(grades.get(f'grade{i}', 0))
        not_assessed -= grade_count
        ws.cell(row=row, column=i+2, value=grade_count).alignment = Alignment(horizontal='center')
    
    ws.cell(row=row, column=2, value=not_assessed).alignment = Alignment(horizontal='center')
    
    # Статистика
    stats = data.get('statistics', {})
    row += 2
    
    ws.merge_cells(f'A{row}:D{row}')
    ws.cell(row=row, column=1, value='СТАТИСТИЧНІ ПОКАЗНИКИ').font = Font(bold=True, size=11)
    row += 1
    
    stats_data = [
        ('Середній бал (СБ):', stats.get('avgScore', '0')),
        ('Ступінь навченості (СН):', stats.get('learningLevel', '0%')),
        ('Коефіцієнт якості знань (КЯЗ):', stats.get('qualityCoeff', '0%')),
        ('Якість знань (ЯЗ):', stats.get('qualityPercent', '0%')),
        ('Коефіцієнт результативності (КР):', stats.get('resultCoeff', '0%'))
    ]
    
    for label, value in stats_data:
        ws.cell(row=row, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value).font = Font(size=11, color='0000FF')
        row += 1
    
    # Підпис директора
    row += 2
    ws.merge_cells(f'A{row}:M{row}')
    ws.cell(row=row, column=1, value='Директор                          /підпис/              Володимир ТКАЧУК')
    ws.cell(row=row, column=1).alignment = Alignment(horizontal='left')
    row += 1
    ws.merge_cells(f'A{row}:M{row}')
    ws.cell(row=row, column=1, value='                  МП')
    ws.cell(row=row, column=1).alignment = Alignment(horizontal='left')
    
    # Автоширина
    column_widths = {'A': 25, 'B': 8, 'C': 8, 'D': 8, 'E': 8, 'F': 8, 'G': 8, 
                     'H': 8, 'I': 8, 'J': 8, 'K': 8, 'L': 8, 'M': 8}
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output

def create_class_report_excel(class_data, class_name, year, semester):
    """Створити Excel звіт по класу"""
    
    wb = Workbook()
    ws = wb.active
    ws.title = f"{class_name}"
    
    # Заголовок
    ws.merge_cells('A1:M1')
    title_cell = ws['A1']
    title_cell.value = f'Коломийський ліцей "Коломийська гімназія імені Михайла Грушевського"'
    title_cell.font = Font(size=14, bold=True)
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    ws.merge_cells('A2:M2')
    subtitle_cell = ws['A2']
    subtitle_cell.value = f'Попредметний звіт за {semester} семестр {year} н.р. ({class_name})'
    subtitle_cell.font = Font(size=12, bold=True)
    subtitle_cell.alignment = Alignment(horizontal='center')
    
    # Заголовки колонок
    headers = ['№', 'Предмет', 'н/а (%)', 'початковий', 'середній', 'достатній', 
               'високий', 'СБ', 'СН(%)', 'СН', 'КЯЗ', 'ЯЗ', 'КР']
    
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col, value=header)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
    
    # Дані
    row = 5
    filled_data = [item for item in class_data if item.get('filled', False)]
    
    for idx, item in enumerate(filled_data, start=1):
        stats = item['statistics']
        grades = item['grades']
        student_count = item['student_count']
        
        # Розрахунок відсотків
        g3 = int(grades.get('grade3', 0))
        g2 = int(grades.get('grade2', 0))
        g1 = int(grades.get('grade1', 0))
        initial = g3 + g2 + g1
        initial_pct = f"{(initial / student_count * 100):.2f}%"
        
        g6 = int(grades.get('grade6', 0))
        g5 = int(grades.get('grade5', 0))
        g4 = int(grades.get('grade4', 0))
        average = g6 + g5 + g4
        average_pct = f"{(average / student_count * 100):.2f}%"
        
        g9 = int(grades.get('grade9', 0))
        g8 = int(grades.get('grade8', 0))
        g7 = int(grades.get('grade7', 0))
        sufficient = g9 + g8 + g7
        sufficient_pct = f"{(sufficient / student_count * 100):.2f}%"
        
        g12 = int(grades.get('grade12', 0))
        g11 = int(grades.get('grade11', 0))
        g10 = int(grades.get('grade10', 0))
        high = g12 + g11 + g10
        high_pct = f"{(high / student_count * 100):.2f}%"
        
        total_graded = initial + average + sufficient + high
        not_assessed = student_count - total_graded
        not_assessed_pct = f"{(not_assessed / student_count * 100):.2f}%"
        
        # СН текст
        learning_level_num = float(stats['learningLevel'].replace('%', ''))
        if learning_level_num >= 64:
            sn_text = 'високий ступінь навченості'
        elif learning_level_num >= 36:
            sn_text = 'достатній ступінь навченості'
        else:
            sn_text = 'середній ступінь навченості'
        
        row_data = [
            idx,
            item['subject'],
            not_assessed_pct,
            initial_pct,
            average_pct,
            sufficient_pct,
            high_pct,
            stats['avgScore'],
            stats['learningLevel'],
            sn_text,
            stats['qualityCoeff'],
            stats['qualityPercent'],
            stats['resultCoeff']
        ]
        
        for col, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.alignment = Alignment(horizontal='center' if col > 2 else 'left', vertical='center')
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        
        row += 1
    
    # Підпис директора
    row += 2
    ws.merge_cells(f'A{row}:M{row}')
    ws.cell(row=row, column=1, value='Директор                          /підпис/              Володимир ТКАЧУК')
    ws.cell(row=row, column=1).alignment = Alignment(horizontal='left')
    row += 1
    ws.merge_cells(f'A{row}:M{row}')
    ws.cell(row=row, column=1, value='                  МП')
    ws.cell(row=row, column=1).alignment = Alignment(horizontal='left')
    
    # Автоширина колонок
    column_widths = {'A': 5, 'B': 30, 'C': 10, 'D': 12, 'E': 12, 'F': 12, 'G': 12,
                     'H': 8, 'I': 10, 'J': 30, 'K': 8, 'L': 8, 'M': 8}
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output

def create_school_report_excel(school_data, all_monitoring, year, semester):
    """Створити Excel звіт по школі з усіма показниками"""
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Звіт по школі"
    
    # Заголовок
    ws.merge_cells('A1:M1')
    title_cell = ws['A1']
    title_cell.value = 'Звіт по класах'
    title_cell.font = Font(size=14, bold=True)
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    ws.merge_cells('A2:M2')
    subtitle_cell = ws['A2']
    subtitle_cell.value = f'за {year} навчальний рік'
    subtitle_cell.font = Font(size=12, bold=True)
    subtitle_cell.alignment = Alignment(horizontal='center')
    
    # Заголовки колонок
    headers = ['Клас', 'н/а (%)', 'початковий (%)', 'середній (%)', 'достатній (%)', 
               'високий (%)', 'СБ', 'СН(%)', 'СН', 'КЯЗ', 'ЯЗ', 'КР']
    
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col, value=header)
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
    
    # Підготовка даних по класах
    class_stats = {}
    
    for record in all_monitoring:
        class_name = record['class']
        if class_name not in class_stats:
            class_stats[class_name] = {
                'subjects': [],
                'total_students': 0
            }
        
        class_stats[class_name]['subjects'].append(record)
        class_stats[class_name]['total_students'] = record['student_count']
    
    # Дані по класах
    row = 5
    
    # Обчислення середніх показників
    overall_stats = {
        'not_assessed': [],
        'initial': [],
        'average': [],
        'sufficient': [],
        'high': [],
        'avg_score': [],
        'learning_level': [],
        'quality_coeff': [],
        'quality_percent': [],
        'result_coeff': []
    }
    
    for class_name in sorted(class_stats.keys()):
        class_data = class_stats[class_name]
        subjects = class_data['subjects']
        student_count = class_data['total_students']
        
        if not subjects or student_count == 0:
            continue
        
        # Розрахунок середніх для класу
        total_not_assessed = 0
        total_initial = 0
        total_average = 0
        total_sufficient = 0
        total_high = 0
        sum_avg_score = 0
        sum_learning_level = 0
        sum_quality_coeff = 0
        sum_quality_percent = 0
        sum_result_coeff = 0
        
        for subject in subjects:
            grades = subject['grades']
            
            # Рівні
            g3 = int(grades.get('grade3', 0))
            g2 = int(grades.get('grade2', 0))
            g1 = int(grades.get('grade1', 0))
            initial = g3 + g2 + g1
            
            g6 = int(grades.get('grade6', 0))
            g5 = int(grades.get('grade5', 0))
            g4 = int(grades.get('grade4', 0))
            average = g6 + g5 + g4
            
            g9 = int(grades.get('grade9', 0))
            g8 = int(grades.get('grade8', 0))
            g7 = int(grades.get('grade7', 0))
            sufficient = g9 + g8 + g7
            
            g12 = int(grades.get('grade12', 0))
            g11 = int(grades.get('grade11', 0))
            g10 = int(grades.get('grade10', 0))
            high = g12 + g11 + g10
            
            total_graded = initial + average + sufficient + high
            not_assessed = student_count - total_graded
            
            total_not_assessed += (not_assessed / student_count * 100)
            total_initial += (initial / student_count * 100)
            total_average += (average / student_count * 100)
            total_sufficient += (sufficient / student_count * 100)
            total_high += (high / student_count * 100)
            
            # Статистика
            stats = subject['statistics']
            sum_avg_score += float(stats.get('avgScore', 0))
            sum_learning_level += float(stats.get('learningLevel', '0%').replace('%', ''))
            sum_quality_coeff += float(stats.get('qualityCoeff', '0%').replace('%', ''))
            sum_quality_percent += float(stats.get('qualityPercent', '0%').replace('%', ''))
            sum_result_coeff += float(stats.get('resultCoeff', '0%').replace('%', ''))
        
        num_subjects = len(subjects)
        
        avg_not_assessed = total_not_assessed / num_subjects
        avg_initial = total_initial / num_subjects
        avg_average = total_average / num_subjects
        avg_sufficient = total_sufficient / num_subjects
        avg_high = total_high / num_subjects
        avg_score = sum_avg_score / num_subjects
        avg_learning_level = sum_learning_level / num_subjects
        avg_quality_coeff = sum_quality_coeff / num_subjects
        avg_quality_percent = sum_quality_percent / num_subjects
        avg_result_coeff = sum_result_coeff / num_subjects
        
        # СН текст
        if avg_learning_level >= 64:
            sn_text = 'високий ступінь навченості'
        elif avg_learning_level >= 36:
            sn_text = 'достатній ступінь навченості'
        else:
            sn_text = 'середній ступінь навченості'
        
        # Записати дані
        row_data = [
            class_name,
            f"{avg_not_assessed:.2f}%",
            f"{avg_initial:.2f}%",
            f"{avg_average:.2f}%",
            f"{avg_sufficient:.2f}%",
            f"{avg_high:.2f}%",
            f"{avg_score:.2f}",
            f"{avg_learning_level:.2f}%",
            sn_text,
            f"{avg_quality_coeff:.2f}%",
            f"{avg_quality_percent:.2f}%",
            f"{avg_result_coeff:.2f}%"
        ]
        
        for col, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.alignment = Alignment(horizontal='center' if col > 1 else 'left', vertical='center')
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        
        # Накопичення для загального
        overall_stats['not_assessed'].append(avg_not_assessed)
        overall_stats['initial'].append(avg_initial)
        overall_stats['average'].append(avg_average)
        overall_stats['sufficient'].append(avg_sufficient)
        overall_stats['high'].append(avg_high)
        overall_stats['avg_score'].append(avg_score)
        overall_stats['learning_level'].append(avg_learning_level)
        overall_stats['quality_coeff'].append(avg_quality_coeff)
        overall_stats['quality_percent'].append(avg_quality_percent)
        overall_stats['result_coeff'].append(avg_result_coeff)
        
        row += 1
    
    # Рядок "середні дані по ліцею"
    if overall_stats['avg_score']:
        avg_row = ws.cell(row=row, column=1, value='середні дані по ліцею')
        avg_row.font = Font(bold=True)
        avg_row.fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
        
        overall_data = [
            f"{sum(overall_stats['not_assessed'])/len(overall_stats['not_assessed']):.2f}%",
            f"{sum(overall_stats['initial'])/len(overall_stats['initial']):.2f}%",
            f"{sum(overall_stats['average'])/len(overall_stats['average']):.2f}%",
            f"{sum(overall_stats['sufficient'])/len(overall_stats['sufficient']):.2f}%",
            f"{sum(overall_stats['high'])/len(overall_stats['high']):.2f}%",
            f"{sum(overall_stats['avg_score'])/len(overall_stats['avg_score']):.2f}",
            f"{sum(overall_stats['learning_level'])/len(overall_stats['learning_level']):.2f}%",
            'високий ступінь навченості',
            f"{sum(overall_stats['quality_coeff'])/len(overall_stats['quality_coeff']):.2f}%",
            f"{sum(overall_stats['quality_percent'])/len(overall_stats['quality_percent']):.2f}%",
            f"{sum(overall_stats['result_coeff'])/len(overall_stats['result_coeff']):.2f}%"
        ]
        
        for col, value in enumerate(overall_data, start=2):
            cell = ws.cell(row=row, column=col, value=value)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
    
    # Підпис директора
    row += 2
    ws.merge_cells(f'A{row}:M{row}')
    ws.cell(row=row, column=1, value='Директор                          /підпис/              Володимир ТКАЧУК')
    ws.cell(row=row, column=1).alignment = Alignment(horizontal='left')
    row += 1
    ws.merge_cells(f'A{row}:M{row}')
    ws.cell(row=row, column=1, value='                  МП')
    ws.cell(row=row, column=1).alignment = Alignment(horizontal='left')
    
    # Автоширина
    column_widths = {'A': 20, 'B': 10, 'C': 15, 'D': 13, 'E': 14, 'F': 13,
                     'G': 8, 'H': 10, 'I': 30, 'J': 10, 'K': 10, 'L': 10, 'M': 10}
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output