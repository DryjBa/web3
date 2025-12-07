import os
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Для работы без GUI

def validate_image(image_path: str, max_size_mb: int = 5, max_dimension: int = 2000):
    """Проверяет изображение на валидность"""
    try:
        # Проверка размера файла
        file_size = os.path.getsize(image_path) / (1024 * 1024)  # МБ
        if file_size > max_size_mb:
            return None, f"Размер файла превышает {max_size_mb} МБ"
        
        # Открываем изображение
        img = Image.open(image_path)
        
        # Проверка формата
        if img.format not in ['JPEG', 'PNG', 'JPG']:
            return None, "Поддерживаются только JPEG и PNG форматы"
        
        # Проверка размеров
        if max(img.size) > max_dimension:
            return None, f"Размер изображения превышает {max_dimension}px"
        
        # Конвертируем в RGB, если нужно
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        return img, None
        
    except Exception as e:
        return None, f"Ошибка при чтении изображения: {str(e)}"

def draw_cross(image: Image.Image, cross_type: str, color: tuple) -> Image.Image:
    """
    Рисует крест на изображении
    
    Args:
        image: Исходное изображение
        cross_type: 'vertical' или 'horizontal'
        color: Кортеж RGB (r, g, b)
    
    Returns:
        Изображение с крестом
    """
    # Создаем копию изображения
    result = image.copy()
    draw = ImageDraw.Draw(result)
    width, height = result.size
    
    # Определяем параметры креста
    thickness = min(width, height) // 20  # Толщина 5% от меньшей стороны
    cross_color = color
    
    if cross_type == "vertical":
        # Вертикальный крест: вертикальная и горизонтальная линии
        # Вертикальная линия
        vertical_x = width // 2
        draw.rectangle(
            [(vertical_x - thickness//2, 0), 
             (vertical_x + thickness//2, height)],
            fill=cross_color
        )
        
        # Горизонтальная линия
        horizontal_y = height // 2
        draw.rectangle(
            [(0, horizontal_y - thickness//2),
             (width, horizontal_y + thickness//2)],
            fill=cross_color
        )
        
    elif cross_type == "horizontal":
        # Горизонтальный крест (буква X)
        # Левая верхняя - правая нижняя диагональ
        for i in range(-thickness//2, thickness//2):
            draw.line([(0 + i, 0), (width + i, height)], fill=cross_color, width=1)
        
        # Правая верхняя - левая нижняя диагональ
        for i in range(-thickness//2, thickness//2):
            draw.line([(width + i, 0), (0 + i, height)], fill=cross_color, width=1)
    
    return result

def create_histogram(image: Image.Image, save_path: str, title: str):
    """
    Создает гистограмму распределения цветов
    
    Args:
        image: Изображение PIL
        save_path: Путь для сохранения гистограммы
        title: Заголовок гистограммы
    """
    # Конвертируем в numpy array
    img_array = np.array(image)
    
    # Разделяем на каналы
    red = img_array[:, :, 0].flatten()
    green = img_array[:, :, 1].flatten()
    blue = img_array[:, :, 2].flatten()
    
    # Создаем график
    plt.figure(figsize=(10, 6))
    
    # Гистограммы для каждого канала
    plt.hist(red, bins=256, color='red', alpha=0.5, label='Red', density=True)
    plt.hist(green, bins=256, color='green', alpha=0.5, label='Green', density=True)
    plt.hist(blue, bins=256, color='blue', alpha=0.5, label='Blue', density=True)
    
    # Настройки графика
    plt.title(f'Распределение цветов: {title}', fontsize=14, fontweight='bold')
    plt.xlabel('Значение цвета (0-255)', fontsize=12)
    plt.ylabel('Частота (нормированная)', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 255])
    
    # Сохраняем
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return save_path

def clean_old_files(directory: str, max_age_hours: int = 24):
    """Очистка старых файлов"""
    import time
    current_time = time.time()
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            if file_age > max_age_hours * 3600:  # Конвертируем часы в секунды
                os.remove(filepath)