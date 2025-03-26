FROM python:3.13.1

WORKDIR /app
COPY ./requirenments.txt .
COPY ./octopus-9f9f7-firebase-adminsdk-fbsvc-e33998ade7.json .
RUN pip install --no-cache-dir -r requirenments.txt
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
