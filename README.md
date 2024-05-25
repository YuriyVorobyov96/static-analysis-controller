# Static analysis controller

## ENG

Required environment:
- [python3](https://www.python.org/downloads/)
- [SonarQube](https://www.sonarsource.com/products/sonarqube/)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Ngrok](https://ngrok.com/) (optional: for emulate different hosts)

Requirements install:
- pip3 install -r requirements.txt

Run server via command line:
- python3 main.py

Run server via Docker:
- docker-compose up -d --build

Start with:
- GET /help - info about
- GET /docs/openapi - documentation

-----

## RU

Необходимое окружение:
- [python3](https://www.python.org/downloads/)
- [SonarQube](https://www.sonarsource.com/products/sonarqube/)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Ngrok](https://ngrok.com/) (опционально: для эмуляции различных хостов)

Установка зависимостей:
- pip3 install -r requirements.txt

Запуск сервера напрямую:
- python3 main.py

Запуск сервера с помощью Docker:
- docker-compose up -d --build

Начните с запросов:
- GET /help - общая информация
- GET /docs/openapi - документация
