FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY lead_api.py .

EXPOSE 5060

CMD ["gunicorn", "--bind", "0.0.0.0:5060", "lead_api:app"]
