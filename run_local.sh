#!/bin/bash

echo "========================================"
echo "Запуск локального сервера"
echo "========================================"
echo ""

# Проверка наличия Python
if ! command -v python3 &> /dev/null; then
    echo "ОШИБКА: Python3 не найден! Установите Python 3.10 или выше."
    exit 1
fi

echo "Проверка зависимостей..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "Установка зависимостей..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ОШИБКА: Не удалось установить зависимости!"
        exit 1
    fi
fi

echo ""
echo "Запуск сервера на http://localhost:5000"
echo "Swagger UI: http://localhost:5000/apidocs"
echo "Нажмите Ctrl+C для остановки"
echo ""
python3 main.py


