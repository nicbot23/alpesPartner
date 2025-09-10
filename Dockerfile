FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
ENV PYTHONPATH=/app/src
EXPOSE 5000
CMD ["flask","--app","src/alpespartner/api/app.py","run","--host","0.0.0.0","--port","5000"]
