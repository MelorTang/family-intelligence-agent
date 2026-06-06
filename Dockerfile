FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --create-home --shell /bin/bash appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/raw /app/data/processed /app/data/logs /app/obsidian_output \
    && chown -R appuser:appuser /app

USER appuser

CMD ["python", "main.py", "schedule"]
