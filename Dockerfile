FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt .
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3","./ddns.py"]

