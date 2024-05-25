# Static analysis controller

## ENG

Required environment:
- python3
- SonarQube
- Docker

Requirements install:
- pip3 install -r requirements.txt

Run server via command line:
- python3 main.py

Run server via Docker:
- docker build -t static-analysis .
- docker run -p 8000:8000 static-analysis

Start with:
- GET /help - info about
- GET /docs/openapi - documentation

-----

## RU

Необходимое окружение:
- python3
- SonarQube
- Docker

Установка зависимостей:
- pip3 install -r requirements.txt

Запуск сервера напрямую:
- python3 main.py

Запуск сервера с помощью Docker:
- docker build -t static-analysis .
- docker run -p 8000:8000 static-analysis

Начните с запросов:
- GET /help - общая информация
- GET /docs/openapi - документация
