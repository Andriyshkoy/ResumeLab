FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create unprivileged user and drop root
RUN groupadd -g 10001 app && useradd -m -u 10001 -g app app \
    && chown -R app:app /app
USER app:app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
