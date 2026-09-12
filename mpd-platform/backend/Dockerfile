FROM python:3.12-slim

WORKDIR /opt
COPY engine /opt/engine
COPY backend /opt/backend
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e /opt/engine -e /opt/backend

WORKDIR /opt/backend
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
