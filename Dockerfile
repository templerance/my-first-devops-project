FROM python:3.9-alpine
WORKDIR /app
RUN pip install flask psycopg2-binary requests prometheus_client
COPY app_unified.py .
CMD ["python", "app_unified.py"]

