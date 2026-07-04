# SPS -> MQTT publisher for the Brauanlage Digital Twin.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY project/ap2/mqtt_publisher/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY project ./project

WORKDIR /app/project/ap2/mqtt_publisher

CMD ["python", "publisher.py"]
