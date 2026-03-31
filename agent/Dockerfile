FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Updated to use relative path in the local context
COPY app.py .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "app.py"]
