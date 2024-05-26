# Static analysis controller

## ENG

Required environment:
- [python 3.12.2 or higher](https://www.python.org/downloads/)
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

Testing env examples for pipelines:
- [GitLab](https://gitlab.com/YuriyVorobyov96/static-analysis-test)
- [GitHub](https://github.com/YuriyVorobyov96/static-analysis-test)

-----

## RU

Необходимое окружение:
- [python 3.12.2 или выше](https://www.python.org/downloads/)
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

Примеры тестовых окружений для пайплайнов:
- [GitLab](https://gitlab.com/YuriyVorobyov96/static-analysis-test)
- [GitHub](https://github.com/YuriyVorobyov96/static-analysis-test)
