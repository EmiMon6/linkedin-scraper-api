FROM python:3.11-slim

ENV APP_VERSION=2.0

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python3", "main.py"]
