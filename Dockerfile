FROM python:3.10-slim

# Устанавливаем полный набор локалей
RUN apt-get update && \
    apt-get install -y locales-all && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем локаль POSIX с русскими именами
ENV LANG ru_RU.UTF-8
ENV LC_TIME ru_RU.UTF-8

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]