# Streamlit image. Implemented in Phase 5.
FROM python:3.12-slim

WORKDIR /app
COPY dashboard/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY dashboard /app

CMD ["python", "-c", "print('Dashboard image placeholder — Streamlit is implemented in Phase 5')"]
