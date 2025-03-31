from flask import Flask, render_template, request, jsonify
import aiohttp
import asyncio
import json
import configparser
import uuid
import threading
import time
from queue import Queue
import webbrowser
import logging
import sys
import subprocess

def install_dependencies():
    required = {'flask', 'aiohttp', 'configparser'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])

try:
    import pkg_resources
    install_dependencies()
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'setuptools'])
    install_dependencies()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Загрузка конфигурации
config = configparser.ConfigParser()
try:
    config.read('settings.ini')
except Exception as e:
    logging.error(f"Ошибка загрузки settings.ini: {str(e)}")
    exit()

# Загрузка словаря стран
def load_countries():
    try:
        with open("countries.json", "r", encoding="utf-8") as f:
            return {int(k): v for k, v in json.load(f).items()}
    except Exception as e:
        logging.error(f"Ошибка загрузки countries.json: {str(e)}")
        return {}

countries_dict = load_countries()

# Потокобезопасные структуры
task_queue = Queue()
progress_data = {}
progress_lock = threading.Lock()

# Чтение параметров из конфига
try:
    MAX_ATTEMPTS = max(1, config['API'].getint('max_attempts', 2))
    REQUEST_DELAY = max(0.5, config['API'].getfloat('request_delay', 1))
    RESPONSE_TIMEOUT = max(5, config['API'].getint('response_timeout', 15))
    MAX_THREADS = max(1, config['Settings'].getint('max_threads', 5))
except KeyError as e:
    logging.error(f"Отсутствует секция или параметр в settings.ini: {str(e)}")
    exit()

async def fetch(session, params):
    try:
        async with session.get(
            config['API']['api_url'],
            params=params,
            timeout=RESPONSE_TIMEOUT
        ) as response:
            text = (await response.text()).strip()
            
            # Детекция ошибок
            if response.status != 200:
                return (False, f"HTTP_ERROR_{response.status}")
                
            if text.startswith("ACCESS_NUMBER"):
                return (True, "SUCCESS")
            elif "NO_NUMBERS" in text:
                return (False, "NO_NUMBERS")
            elif "BAD_KEY" in text:
                return (False, "INVALID_API_KEY")
            else:
                return (False, "UNKNOWN_RESPONSE")
                
    except asyncio.TimeoutError:
        return (False, "TIMEOUT")
    except aiohttp.ClientError as e:
        return (False, f"NETWORK_ERROR: {str(e)}")
    except Exception as e:
        return (False, f"UNEXPECTED_ERROR: {str(e)}")

async def process_country(session, task_id, service, country):
    success_count = 0
    for attempt in range(MAX_ATTEMPTS):
        params = {
            "api_key": config['API']['api_key'],
            "action": "getNumber",
            "service": service,
            "country": country,
            "maxPrice": config['API'].getint('max_price')
        }
        
        start_time = time.time()
        success, error_type = await fetch(session, params)
        
        # Логирование с детализацией
        log_message = (
            f"[{service}] Запрос {country} "
            f"({attempt+1}/{MAX_ATTEMPTS}) "
            f"{'✅ Успех' if success else '❌ Ошибка: ' + error_type} "
            f"({time.time() - start_time:.2f} сек)"
        )
        logging.info(log_message)
        
        if success:
            success_count += 1
        
        with progress_lock:
            if task_id in progress_data:
                progress_data[task_id]["processed"] += 1
        
        await asyncio.sleep(REQUEST_DELAY)
    
    if success_count == MAX_ATTEMPTS:
        with progress_lock:
            progress_data[task_id]["results"].append({
                "country_code": country,
                "country_name": countries_dict.get(country, "Unknown")
            })

async def worker():
    while True:
        task = task_queue.get()
        task_id = task["task_id"]
        service = task["service"]
        
        with progress_lock:
            progress_data[task_id] = {
                "processed": 0,
                "total": len(countries_dict) * MAX_ATTEMPTS,
                "results": []
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = [
                    process_country(session, task_id, service, country)
                    for country in countries_dict.keys()
                ]
                await asyncio.gather(*tasks)
        except Exception as e:
            logging.error(f"Критическая ошибка в worker: {str(e)}")
        
        task_queue.task_done()

# Запуск потоков
for _ in range(MAX_THREADS):
    threading.Thread(
        target=lambda: asyncio.run(worker()),
        daemon=True
    ).start()

@app.route('/')
def index():
    return render_template(
        'index.html',
        services=config['API']['services'].split(',')
    )

@app.route('/check', methods=['POST'])
def check_numbers():
    task_id = str(uuid.uuid4())
    service = request.json.get('service')
    
    if service not in config['API']['services'].split(','):
        return jsonify({"error": "Недопуступный сервис"}), 400
    
    task_queue.put({"task_id": task_id, "service": service})
    return jsonify({"task_id": task_id})

@app.route('/progress/<task_id>')
def get_progress(task_id):
    with progress_lock:
        data = progress_data.get(task_id, {})
    return jsonify({
        "progress": data.get("processed", 0),
        "total": data.get("total", 1),
        "results": data.get("results", [])
    })

if __name__ == '__main__':
    webbrowser.open('http://localhost:5000')
    app.run(debug=False, threaded=True)