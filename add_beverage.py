"""
Скрипт для добавления нового напитка в систему
"""
import requests
import json
import sys

def add_beverage():
    """Интерактивное добавление напитка"""
    print("=" * 50)
    print("Добавление нового напитка")
    print("=" * 50)
    print()
    
    # Ввод данных
    beverage = {}
    
    beverage['id'] = input("Введите ID (уникальный номер): ").strip()
    beverage['name'] = input("Введите название напитка: ").strip()
    beverage['manufacturer'] = input("Введите производителя: ").strip()
    beverage['type'] = input("Введите тип (Газированный/Сок/Вода/Энергетический): ").strip()
    
    try:
        beverage['volume'] = float(input("Введите объем в мл (например: 500.0): ").strip())
        beverage['price'] = float(input("Введите цену в рублях (например: 89.0): ").strip())
        beverage['stock'] = int(input("Введите количество в наличии (целое число): ").strip())
    except ValueError:
        print("\nОШИБКА: Неправильный формат числовых данных!")
        print("volume и price должны быть числами с точкой (например: 500.0)")
        print("stock должен быть целым числом (например: 100)")
        return False
    
    # Отправка запроса
    try:
        print("\nОтправка запроса...")
        response = requests.post(
            "http://127.0.0.1:5000/beverages/",
            json=beverage,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 201:
            print("\n✓ Напиток успешно добавлен!")
            print("\nДанные добавленного напитка:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return True
        else:
            print(f"\n✗ Ошибка: {response.status_code}")
            error_data = response.json()
            if 'error' in error_data:
                print(f"Сообщение: {error_data['error']}")
            else:
                print(f"Ответ сервера: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n✗ ОШИБКА: Не удалось подключиться к серверу!")
        print("Убедитесь, что сервер запущен: python main.py")
        return False
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        return False

def add_beverage_from_args():
    """Добавление напитка из аргументов командной строки"""
    if len(sys.argv) < 8:
        print("Использование:")
        print("python add_beverage.py <id> <name> <manufacturer> <type> <volume> <price> <stock>")
        print("\nПример:")
        print('python add_beverage.py "5" "Лимонад" "Фанта" "Газированный" 330.0 75.0 100')
        return False
    
    beverage = {
        'id': sys.argv[1],
        'name': sys.argv[2],
        'manufacturer': sys.argv[3],
        'type': sys.argv[4],
        'volume': float(sys.argv[5]),
        'price': float(sys.argv[6]),
        'stock': int(sys.argv[7])
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/beverages/",
            json=beverage,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 201:
            print("Напиток успешно добавлен!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return True
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Режим с аргументами командной строки
        success = add_beverage_from_args()
    else:
        # Интерактивный режим
        success = add_beverage()
    
    sys.exit(0 if success else 1)

