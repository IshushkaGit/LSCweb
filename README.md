# LSCweb

# 📱 SMS Number Availability Checker

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![aiohttp](https://img.shields.io/badge/aiohttp-3.0+-yellowgreen.svg)

Проект для проверки доступности номеров на SMS-сервисах через API smslive.pro. Включает веб-интерфейс, многопоточную обработку и мониторинг прогресса.

## 🔍 Функционал

- Проверка доступности номеров для 200+ стран
- Поддержка нескольких сервисов (Telegram, VK, WhatsApp и др.)
- Многопоточная обработка запросов
- Веб-интерфейс с отображением прогресса
- Логирование операций
- Настройка параметров через конфигурационный файл

## ⚙️ Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/ваш-username/sms-number-checker.git
cd sms-number-checker
```

2. Установите зависимости:
```bash
install_dependencies.bat
```
Или вручную:
```bash
pip install -r requirements.txt
```

## 🚀 Запуск

```bash
start.bat
```

После запуска автоматически откроется браузер с веб-интерфейсом по адресу:
```
http://localhost:5000
```

## ⚙️ Конфигурация

Настройки редактируются в файле `settings.ini`:

```ini
[API]
api_url = https://smslive.pro/stubs/handler_api.php
api_key = ваш_api_ключ  ; Получите на smslive.pro
services = tg,vk,ok,wa,vi  ; Доступные сервисы
max_price = 100  ; Максимальная цена номера
max_attempts = 1  ; Попыток на страну
request_delay = 2  ; Задержка между запросами (сек)
response_timeout = 15  ; Таймаут запроса (сек)

[Settings]
max_threads = 5  ; Количество потоков обработки
log_file = LiveSMS_Log.txt  ; Файл логов
```

## 📂 Структура проекта

```
sms-number-checker/
├── app.py              # Основное приложение
├── countries.json      # Словарь стран
├── settings.ini        # Конфигурационный файл
├── requirements.txt    # Зависимости Python
├── install_dependencies.bat # Скрипт установки
├── start.bat           # Скрипт запуска
└── templates/          # Шаблоны Flask
    └── index.html      # Веб-интерфейс
```

## 📊 Как использовать

1. Введите ваш API-ключ от smslive.pro в `settings.ini`
2. Запустите приложение через `start.bat`
3. В веб-интерфейсе выберите сервис для проверки
4. Наблюдайте за прогрессом проверки
5. Получите список стран с доступными номерами

## 📝 Логирование

Все операции записываются в файл `LiveSMS_Log.txt` в формате:
```
[дата] [уровень] - [сообщение]
```

Пример:
```
2023-05-15 14:30:45 - INFO - [tg] Запрос 0 (1/1) ✅ Успех (1.23 сек)
```

## ⚠️ Ограничения

- Для работы требуется API-ключ от smslive.pro или другого сервиса
- При `reset --hard` в скрипте обновления теряются локальные изменения
- Большое количество потоков может привести к блокировке IP

## 📜 Лицензия

MIT License

---
