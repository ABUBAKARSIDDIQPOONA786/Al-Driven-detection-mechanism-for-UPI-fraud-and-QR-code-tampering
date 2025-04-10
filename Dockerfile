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
COPY rf_model.pkl /app/rf_model.pkl
COPY xgb_model.pkl /app/xgb_model.pkl
COPY iso_model.pkl /app/iso_model.pkl
COPY scaler.pkl /app/scaler.pkl
