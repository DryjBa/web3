@echo off
chcp 65001 >nul
echo ========================================
echo Запуск локального сервера
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.10 или выше с https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python найден
python --version

echo.
echo Проверка зависимостей...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Зависимости не найдены, устанавливаю...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить зависимости!
        echo Попробуйте вручную: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo [OK] Зависимости установлены
) else (
    echo [OK] Зависимости уже установлены
)

echo.
echo ========================================
echo Запуск сервера...
echo ========================================
echo.
echo Сервер будет доступен на: http://localhost:5000
echo Swagger UI: http://localhost:5000/apidocs
echo Нажмите Ctrl+C для остановки
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Сервер завершился с ошибкой
    echo Проверьте сообщения выше для диагностики
    pause
    exit /b 1
)

