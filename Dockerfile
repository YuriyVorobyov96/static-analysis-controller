FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY documentation documentation
COPY src src
COPY main.py main.py

EXPOSE 8000

CMD [ "python3", "main.py" ]
