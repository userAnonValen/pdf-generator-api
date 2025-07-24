FROM python:3.10-slim

WORKDIR /app
COPY . /app
COPY fonts /app/fonts


RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libcairo2 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000

CMD ["python", "servidor.py"]
