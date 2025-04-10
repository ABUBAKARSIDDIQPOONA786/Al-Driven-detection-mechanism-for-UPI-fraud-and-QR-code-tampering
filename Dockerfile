FROM python:3.11-slim

# Install system dependencies: libzbar0 (for pyzbar) and libgl1 (for OpenCV)
RUN apt-get update && apt-get install -y libzbar0 libgl1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
