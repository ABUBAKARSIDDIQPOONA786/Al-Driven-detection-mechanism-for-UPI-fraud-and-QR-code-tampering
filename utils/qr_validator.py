import os
import re
import pandas as pd
import logging
from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import datetime
import requests
from bs4 import BeautifulSoup
import whois
import tldextract
import cv2
from pyzbar.pyzbar import decode
import joblib

logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
npci_df = pd.read_excel(os.path.join(BASE_DIR, "../data/npci_registered_upi_apps.xlsx"))
mcc_df = pd.read_csv(os.path.join(BASE_DIR, "../data/mcc.csv"))

TRAIN_MODE = False
  
HEADERS = {"User-Agent": "Mozilla/5.0"}

def extract_qr_text(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    decoded = decode(gray)
    return decoded[0].data.decode("utf-8") if decoded else None

def parse_upi_qr(image_path):
    qr_text = extract_qr_text(image_path)
    if not qr_text or not qr_text.startswith("upi://pay?"):
        return None
    query = qr_text.split("?", 1)[1]
    return dict(param.split("=") for param in query.split("&") if "=" in param)

def validate_upi_id(upi_id):
    pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+$"
    handle = '@' + upi_id.split('@')[-1]
    if handle in npci_df['Handle Name'].values:
        return True
    return False

def verify_mcc(mcc):
    if not mcc or mcc == "0000":
        return "Individual Receiver"
    match = mcc_df[mcc_df['MCC'].astype(str) == str(mcc)]
    return match['Description'].iloc[0] if not match.empty else "Unknown MCC"

def extract_features(url):
    parsed = urlparse(url)
    domain = parsed.netloc
    whois_feat = [730, 365, 1]  # Skipping WHOIS lookup for faster performance
    return [
        len(url),
        1 if parsed.scheme == "https" else 0,
        url.count('-') + url.count('.') + url.count('?'),
        sum(c.isdigit() for c in url),
        tldextract.extract(url).subdomain.count('.'),
        len(tldextract.extract(url).domain),
        1 if any(s in domain for s in ["bit.ly", "tinyurl", "t.co"]) else 0
    ] + whois_feat

def get_genuine_urls():
    try:
        response = requests.get("https://moz.com/top500", headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        sites = []
        for row in soup.select("table tbody tr"):
            cols = row.find_all("td")
            if len(cols) > 1:
                site = cols[1].text.strip()
                sites.append(f"https://{site}")
        return sites[:100]
    except Exception as e:
        logging.warning(f"Error scraping genuine URLs: {e}")
        return ["https://example.com", "https://google.com", "https://github.com"]

def train_models():
    logging.info("Training phishing detection models...")
    genuine_urls = get_genuine_urls()

    try:
        phishing = requests.get("https://openphish.com/feed.txt").text
        phishing_urls = phishing.split("\n")[:100]
    except:
        logging.warning("Unable to fetch phishing URLs. Using dummy phishing URLs.")
        phishing_urls = ["http://phishing-attack.com", "http://malware-link.biz"]

    data = [extract_features(url) for url in genuine_urls + phishing_urls]
    labels = [0]*len(genuine_urls) + [1]*len(phishing_urls)

    if len(set(labels)) < 2:
        raise ValueError("⚠️ Not enough class diversity in training data. Got only one class.")

    df = pd.DataFrame(data)
    X_train, X_test, y_train, y_test = train_test_split(df, labels, test_size=0.2)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)

    rf = RandomForestClassifier().fit(X_train, y_train)
    xgb = XGBClassifier(eval_metric='logloss').fit(X_train, y_train)
    iso = IsolationForest().fit(X_train)

    joblib.dump(rf, 'rf_model.pkl')
    joblib.dump(xgb, 'xgb_model.pkl')
    joblib.dump(iso, 'iso_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')

    return rf, xgb, iso, scaler

if TRAIN_MODE:
    rf_model, xgb_model, iso_model, scaler = train_models()
else:
    rf_model = joblib.load("rf_model.pkl")
    xgb_model = joblib.load("xgb_model.pkl")
    iso_model = joblib.load("iso_model.pkl")
    scaler = joblib.load("scaler.pkl")

def predict_phishing(url):
    f = extract_features(url)
    x = scaler.transform([f])
    rf = rf_model.predict(x)[0]
    xgb = xgb_model.predict(x)[0]
    iso = iso_model.decision_function(x)[0]
    score = (rf + xgb - iso) / 3
    return "Phishing" if score > 0.6 else "Safe"

def predict_qr_code_safety(qr_data):
    upi_id = qr_data.get("pa", "")
    ref_url = qr_data.get("refUrl", "")
    mcc = qr_data.get("mc", "")

    is_valid_upi = validate_upi_id(upi_id)
    phishing_status = predict_phishing(ref_url) if ref_url else "Safe"
    mcc_description = verify_mcc(mcc)

    risk = 0
    if not is_valid_upi:
        risk += 50
    if phishing_status == "Phishing":
        risk += 40
    if mcc_description == "Unknown MCC":
        risk += 20

    summary = f"""
✅ UPI ID: {'Valid' if is_valid_upi else 'Invalid'}
🔗 Ref URL: {phishing_status}
🏷️ MCC: {mcc_description}
📊 Risk Score: {risk}/100
⚠️ Risk Level: {'HIGH' if risk > 70 else 'MODERATE' if risk > 40 else 'LOW'}
"""
    return summary