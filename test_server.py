"""
Простой скрипт для проверки доступности сервера Flask
"""
import requests
import sys
import time

def test_server(base_url="http://127.0.0.1:5000"):
    """Проверяет доступность сервера"""
    print(f"Проверка сервера на {base_url}...")
    
    endpoints = [
        ("/", "Главная страница"),
        ("/beverages/", "Список напитков"),
        ("/statistics/", "Статистика"),
        ("/apidocs", "Swagger UI"),
    ]
    
    all_ok = True
    for endpoint, name in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 301, 302]:
                print(f"OK {name}: (статус {response.status_code})")
            else:
                print(f"WARNING {name}: Статус {response.status_code}")
                all_ok = False
        except requests.exceptions.ConnectionError:
            print(f"X {name}: Сервер не отвечает")
            print(f"  Убедитесь, что сервер запущен: python main.py")
            all_ok = False
        except Exception as e:
            print(f"X {name}: Ошибка - {e}")
            all_ok = False
    
    # Тест API
    try:
        response = requests.get(f"{base_url}/beverages/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"OK API работает: получено {len(data)} напитков")
        else:
            print(f"WARNING API вернул статус {response.status_code}")
            all_ok = False
    except Exception as e:
        print(f"X Ошибка при тестировании API: {e}")
        all_ok = False
    
    return all_ok

if __name__ == "__main__":
    # Даем серверу время на запуск, если он только что был запущен
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        print("Ожидание запуска сервера (5 секунд)...")
        time.sleep(5)
    
    success = test_server()
    sys.exit(0 if success else 1)
