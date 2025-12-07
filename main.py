import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from dotenv import load_dotenv
import requests

from utils import draw_cross, create_histogram, validate_image

# Загружаем переменные окружения
load_dotenv()

app = FastAPI(title="Image Cross Processor", version="1.0")

# Настройка путей
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
GENERATED_DIR = os.path.join(BASE_DIR, "static", "generated")

# Создаем директории, если их нет
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Конфигурация reCAPTCHA
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "your-secret-key-here")
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "your-site-key-here")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница с формой загрузки"""
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "recaptcha_site_key": RECAPTCHA_SITE_KEY,
            "max_file_size": 5  # МБ
        }
    )

@app.post("/process", response_class=HTMLResponse)
async def process_image(
    request: Request,
    image: UploadFile = File(...),
    cross_type: str = Form(...),
    color_r: int = Form(..., ge=0, le=255),
    color_g: int = Form(..., ge=0, le=255),
    color_b: int = Form(..., ge=0, le=255),
    recaptcha_response: str = Form(...)
):
    """Обработка загруженного изображения"""
    
    # 1. Проверка reCAPTCHA
    if not await verify_recaptcha(recaptcha_response):
        raise HTTPException(status_code=400, detail="Не пройдена проверка reCAPTCHA")
    
    # 2. Валидация файла
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")
    
    # 3. Генерация уникальных имен файлов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    # Исходное изображение
    original_filename = f"original_{timestamp}_{unique_id}.jpg"
    original_path = os.path.join(UPLOAD_DIR, original_filename)
    
    # Обработанное изображение
    processed_filename = f"processed_{timestamp}_{unique_id}.jpg"
    processed_path = os.path.join(GENERATED_DIR, processed_filename)
    
    # Гистограммы
    hist_original_filename = f"hist_original_{timestamp}_{unique_id}.png"
    hist_original_path = os.path.join(GENERATED_DIR, hist_original_filename)
    
    hist_processed_filename = f"hist_processed_{timestamp}_{unique_id}.png"
    hist_processed_path = os.path.join(GENERATED_DIR, hist_processed_filename)
    
    try:
        # 4. Сохраняем загруженное изображение
        contents = await image.read()
        with open(original_path, "wb") as f:
            f.write(contents)
        
        # 5. Валидируем и обрабатываем изображение
        img, error = validate_image(original_path)
        if error:
            os.remove(original_path)
            raise HTTPException(status_code=400, detail=error)
        
        # 6. Рисуем крест
        color = (color_r, color_g, color_b)
        processed_img = draw_cross(img, cross_type, color)
        processed_img.save(processed_path, "JPEG")
        
        # 7. Создаем гистограммы
        create_histogram(img, hist_original_path, "Исходное изображение")
        create_histogram(processed_img, hist_processed_path, "Изображение с крестом")
        
        # 8. Подготавливаем данные для шаблона
        result_data = {
            "request": request,
            "original_image": f"/static/uploads/{original_filename}",
            "processed_image": f"/static/generated/{processed_filename}",
            "hist_original": f"/static/generated/{hist_original_filename}",
            "hist_processed": f"/static/generated/{hist_processed_filename}",
            "cross_type": "вертикальный" if cross_type == "vertical" else "горизонтальный",
            "color": f"RGB({color_r}, {color_g}, {color_b})",
            "image_name": image.filename,
            "timestamp": timestamp
        }
        
        return templates.TemplateResponse("result.html", result_data)
        
    except Exception as e:
        # Очистка в случае ошибки
        for path in [original_path, processed_path, hist_original_path, hist_processed_path]:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=f"Ошибка обработки: {str(e)}")

async def verify_recaptcha(recaptcha_response: str) -> bool:
    """Проверка Google reCAPTCHA"""
    if not RECAPTCHA_SECRET_KEY or RECAPTCHA_SECRET_KEY == "your-secret-key-here":
        # В режиме разработки пропускаем проверку
        return True
    
    try:
        payload = {
            "secret": RECAPTCHA_SECRET_KEY,
            "response": recaptcha_response
        }
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data=payload,
            timeout=10
        )
        result = response.json()
        return result.get("success", False)
    except:
        return False

@app.get("/health")
async def health_check():
    """Эндпоинт для проверки работы приложения"""
    return {"status": "ok", "service": "image-processor"}

# Для локального запуска
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)