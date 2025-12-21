from flask import Flask, Blueprint, jsonify, request
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# Хранилище данных в памяти
BEVERAGES = [
    {'id': '1', 'name': 'Кока-Кола', 'manufacturer': 'Coca-Cola', 'type': 'Газированный', 'volume': 500.0, 'price': 89.0, 'stock': 150},
    {'id': '2', 'name': 'Апельсиновый сок', 'manufacturer': 'Добрый', 'type': 'Сок', 'volume': 1000.0, 'price': 120.0, 'stock': 80},
    {'id': '3', 'name': 'Минеральная вода', 'manufacturer': 'Боржоми', 'type': 'Вода', 'volume': 500.0, 'price': 95.0, 'stock': 200},
    {'id': '4', 'name': 'Энергетик', 'manufacturer': 'Red Bull', 'type': 'Энергетический', 'volume': 250.0, 'price': 150.0, 'stock': 60}
]

# Главный Blueprint
main_bp = Blueprint('main', __name__, template_folder='templates', static_folder='static')

@main_bp.route('/beverages/', methods=['GET'])
def list_beverages():
    """Получить список всех напитков с возможностью сортировки
    ---
    tags:
      - Напитки
    parameters:
      - name: sort_by
        in: query
        type: string
        enum: ['id', 'name', 'manufacturer', 'type', 'volume', 'price', 'stock']
        required: false
        description: Поле для сортировки
      - name: order
        in: query
        type: string
        enum: ['asc', 'desc']
        default: asc
        required: false
        description: Порядок сортировки
    responses:
      200:
        description: Список напитков
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
              name:
                type: string
              manufacturer:
                type: string
              type:
                type: string
              volume:
                type: number
              price:
                type: number
              stock:
                type: integer
    """
    beverages = BEVERAGES.copy()
    sort_by = request.args.get('sort_by')
    order = request.args.get('order', 'asc')
    
    if sort_by:
        reverse = order == 'desc'
        try:
            beverages.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse)
        except:
            pass
    
    return jsonify(beverages)

@main_bp.route('/beverages/', methods=['POST'])
def create_beverage():
    """Добавить новый напиток
    ---
    tags:
      - Напитки
    parameters:
      - in: body
        name: beverage
        required: true
        schema:
          type: object
          required:
            - id
            - name
            - manufacturer
            - type
            - volume
            - price
            - stock
          properties:
            id:
              type: string
              description: Идентификатор напитка
            name:
              type: string
              description: Название напитка
            manufacturer:
              type: string
              description: Производитель
            type:
              type: string
              description: Тип напитка
            volume:
              type: number
              description: Объем в мл
            price:
              type: number
              description: Цена в рублях
            stock:
              type: integer
              description: Количество в наличии
    responses:
      201:
        description: Напиток создан
      400:
        description: Напиток с таким ID уже существует
    """
    data = request.get_json()
    if any(b['id'] == data['id'] for b in BEVERAGES):
        return jsonify({'error': 'Напиток с таким ID уже существует'}), 400
    BEVERAGES.append(data)
    return jsonify(data), 201

@main_bp.route('/beverages/<id>', methods=['GET'])
def get_beverage(id):
    """Получить напиток по ID
    ---
    tags:
      - Напитки
    parameters:
      - name: id
        in: path
        type: string
        required: true
        description: Идентификатор напитка
    responses:
      200:
        description: Напиток найден
      404:
        description: Напиток не найден
    """
    beverage = next((b for b in BEVERAGES if b['id'] == id), None)
    if not beverage:
        return jsonify({'error': 'Напиток не найден'}), 404
    return jsonify(beverage)

@main_bp.route('/beverages/<id>', methods=['PUT'])
def update_beverage(id):
    """Обновить напиток по ID
    ---
    tags:
      - Напитки
    parameters:
      - name: id
        in: path
        type: string
        required: true
        description: Идентификатор напитка
      - in: body
        name: beverage
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            manufacturer:
              type: string
            type:
              type: string
            volume:
              type: number
            price:
              type: number
            stock:
              type: integer
    responses:
      200:
        description: Напиток обновлен
      404:
        description: Напиток не найден
    """
    beverage = next((b for b in BEVERAGES if b['id'] == id), None)
    if not beverage:
        return jsonify({'error': 'Напиток не найден'}), 404
    
    data = request.get_json()
    beverage.update(data)
    return jsonify(beverage)

@main_bp.route('/beverages/<id>', methods=['DELETE'])
def delete_beverage(id):
    """Удалить напиток по ID
    ---
    tags:
      - Напитки
    parameters:
      - name: id
        in: path
        type: string
        required: true
        description: Идентификатор напитка
    responses:
      204:
        description: Напиток удален
      404:
        description: Напиток не найден
    """
    global BEVERAGES
    beverage = next((b for b in BEVERAGES if b['id'] == id), None)
    if not beverage:
        return jsonify({'error': 'Напиток не найден'}), 404
    BEVERAGES.remove(beverage)
    return '', 204

@main_bp.route('/statistics/<field>', methods=['GET'])
def get_statistics(field):
    """Получить статистику по числовому полю
    ---
    tags:
      - Статистика
    parameters:
      - name: field
        in: path
        type: string
        enum: ['volume', 'price', 'stock']
        required: true
        description: Числовое поле
    responses:
      200:
        description: Статистика по полю
        schema:
          type: object
          properties:
            field:
              type: string
            min:
              type: number
            max:
              type: number
            avg:
              type: number
      400:
        description: Некорректное поле
    """
    numeric_fields = ['volume', 'price', 'stock']
    if field not in numeric_fields:
        return jsonify({'error': f'Поле должно быть одним из: {", ".join(numeric_fields)}'}), 400
    
    values = [float(b[field]) for b in BEVERAGES if field in b]
    if not values:
        return jsonify({'field': field, 'min': 0, 'max': 0, 'avg': 0})
    
    return jsonify({
        'field': field,
        'min': min(values),
        'max': max(values),
        'avg': sum(values) / len(values)
    })

@main_bp.route('/statistics/', methods=['GET'])
def get_all_statistics():
    """Получить статистику по всем числовым полям
    ---
    tags:
      - Статистика
    responses:
      200:
        description: Статистика по всем полям
        schema:
          type: object
          additionalProperties:
            type: object
            properties:
              min:
                type: number
              max:
                type: number
              avg:
                type: number
    """
    result = {}
    for field in ['volume', 'price', 'stock']:
        values = [float(b[field]) for b in BEVERAGES if field in b]
        if values:
            result[field] = {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values)
            }
    return jsonify(result)

@main_bp.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Продажа напитков</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .info { background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>API Продажа напитков</h1>
        <div class="info">
            <h2>Документация API</h2>
            <p><a href="/apidocs">Swagger UI</a> - Интерактивная документация API</p>
        </div>
        <div class="info">
            <h2>Доступные эндпоинты:</h2>
            <ul>
                <li><strong>GET /beverages/</strong> - Список всех напитков (с сортировкой)</li>
                <li><strong>POST /beverages/</strong> - Добавить напиток</li>
                <li><strong>GET /beverages/&lt;id&gt;</strong> - Получить напиток по ID</li>
                <li><strong>PUT /beverages/&lt;id&gt;</strong> - Обновить напиток</li>
                <li><strong>DELETE /beverages/&lt;id&gt;</strong> - Удалить напиток</li>
                <li><strong>GET /statistics/</strong> - Статистика по всем полям</li>
                <li><strong>GET /statistics/&lt;field&gt;</strong> - Статистика по полю (volume, price, stock)</li>
            </ul>
        </div>
    </body>
    </html>
    '''

app.register_blueprint(main_bp)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"\n{'='*50}")
    print(f"🚀 Запуск сервера Flask...")
    print(f"📡 Сервер будет доступен на: http://{host}:{port}")
    print(f"📝 Swagger UI: http://{host}:{port}/apidocs")
    print(f"🔍 Главная страница: http://{host}:{port}/")
    print(f"{'='*50}\n")
    
    app.run(debug=debug, host='0.0.0.0' if port != 5000 else host, port=port)
