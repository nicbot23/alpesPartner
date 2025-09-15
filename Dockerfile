FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api_simple.py .
EXPOSE 5000
CMD ["python", "api_simple.py"]
