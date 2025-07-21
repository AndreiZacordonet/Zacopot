FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/logs

EXPOSE 2222

# update the timezone
ENV TZ=Europe/Bucharest
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

CMD ["python", "main.py"]
