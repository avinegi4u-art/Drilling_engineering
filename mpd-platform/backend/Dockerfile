# FastAPI image. Implemented in Phase 4.
FROM python:3.12-slim

WORKDIR /app
COPY engine /engine
COPY backend /app
RUN pip install --no-cache-dir -e /engine -e /app

CMD ["python", "-c", "print('Backend image placeholder — FastAPI is implemented in Phase 4')"]
