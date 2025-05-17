# 🛡️ Al Driven detection mechanism for UPI fraud and QR code tampering

An intelligent Flask-based web app to detect potential UPI transaction fraud and digital QR code phishing using AI and Machine Learning.

## 🚀 Features
- ✅ UPI ID validation (NPCI handle check)
- 🔍 Real-time QR code phishing detection
- 📊 Merchant Category Code (MCC) verification
- 💰 Transaction risk analysis with AI models
- 📱 Mobile responsive & live input validation

## 📁 Tech Stack
- Python + Flask
- Scikit-learn, XGBoost, TensorFlow
- OpenCV, pyzbar for QR decoding
- HTML5, CSS3 (Modern UI)
- Trained phishing models & synthetic fraud dataset

## ⚙️ System Requirements

To run this AI-Driven Detection System for UPI Fraud and QR Code Tampering, ensure your system meets the following requirements:

### 💻 Operating System:
- Windows 10 / 11, macOS, or Linux (Ubuntu recommended)

### 🧠 Hardware:
- Processor: Intel i5/i7 (8th gen or higher) / AMD Ryzen 5 or better
- RAM: 8 GB minimum (16 GB recommended)
- Storage: At least 500 MB of free disk space
- GPU (Optional): NVIDIA GPU for faster model training (not mandatory)

### 🛠️ Software Requirements:

| Tool / Library        | Version       |
|------------------------|----------------|
| Python                | 3.9 or higher  |
| Flask                 | 2.0+           |
| scikit-learn          | 1.0+           |
| XGBoost               | 1.6+           |
| OpenCV                | 4.5+           |
| pyzbar                | 0.1.8+         |
| pandas                | 1.3+           |
| numpy                 | 1.21+          |
| joblib                | 1.1+           |
| requests              | 2.26+          |
| BeautifulSoup         | 4.10+          |
| whois                 | 0.7+           |

To install all dependencies:
```bash
pip install -r requirements.txt


## 📷 Screenshots
![full app architecture](https://github.com/user-attachments/assets/7e157b29-70e8-401b-94f9-ddfb54666ae0)


## 🧪 Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/upi-fraud-detector.git
cd upi-fraud-detector
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python app.py


