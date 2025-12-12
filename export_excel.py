from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime
import io

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
    
    # Автоширина колонок
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Зберегти у пам'ять
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output

def create_school_report_excel(school_data, year, semester):
    """Створити Excel звіт по школі"""
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Звіт по школі"
    
    # Заголовок
    ws.merge_cells('A1:M1')
    title_cell = ws['A1']
    title_cell.value = f'Коломийський ліцей "Коломийська гімназія імені Михайла Грушевського"'
    title_cell.font = Font(size=14, bold=True)
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    ws.merge_cells('A2:M2')
    subtitle_cell = ws['A2']
    subtitle_cell.value = f'Звіт по класах за {semester} семестр {year} н.р.'
    subtitle_cell.font = Font(size=12, bold=True)
    subtitle_cell.alignment = Alignment(horizontal='center')
    
    # Заголовки
    headers = ['Клас', 'Заповнено', 'Всього', 'Прогрес (%)']
    
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
    
    # Дані по класах
    row = 5
    for class_name, data in sorted(school_data.items()):
        ws.cell(row=row, column=1, value=class_name).alignment = Alignment(horizontal='center')
        ws.cell(row=row, column=2, value=data['filled']).alignment = Alignment(horizontal='center')
        ws.cell(row=row, column=3, value=data['total']).alignment = Alignment(horizontal='center')
        ws.cell(row=row, column=4, value=f"{data['progress']}%").alignment = Alignment(horizontal='center')
        row += 1
    
    # Автоширина
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = min(max_length + 2, 30)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output