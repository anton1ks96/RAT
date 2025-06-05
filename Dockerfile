FROM python:3.13.2-slim

WORKDIR /app

COPY requirements.txt .
COPY formal-guru-447320-t9-4d011c14e1be.json .
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "--mode", "tg"]