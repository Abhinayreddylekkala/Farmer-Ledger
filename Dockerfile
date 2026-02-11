# Inside your Dockerfile
FROM python:3.10-slim
WORKDIR /app
RUN pip install flask flask-sqlalchemy flask-login authlib requests
COPY . .
CMD ["python", "app.py"]