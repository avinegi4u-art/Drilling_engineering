FROM python:3.12-slim

WORKDIR /opt
COPY engine /opt/engine
COPY dashboard /opt/dashboard
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e /opt/engine \
    && pip install --no-cache-dir -r /opt/dashboard/requirements.txt

WORKDIR /opt/dashboard
ENV PYTHONUNBUFFERED=1
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
