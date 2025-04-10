import pandas as pd
import re
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Load transaction dataset
df = pd.read_csv("data/transactions_with_majority_voting.csv")
upi_handles_df = pd.read_excel("data/npci_registered_upi_apps.xlsx")


# Train RandomForest model
features = ['Amount', 'Hours', 'Minutes', 'Seconds', 'Sender Fraud Label', 'Receiver Fraud Label']
target = 'Final_Anomaly'

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

def validate_upi_id(upi_id):
    upi_pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+$"
    if "@" not in upi_id:
        return {"Valid": False, "Error": "Missing '@' symbol"}

    handle = '@' + upi_id.split("@")[1]
    if handle in upi_handles_df['Handle Name'].values:
        match = re.match(upi_pattern, upi_id)
        if not match:
            return {"Valid": False, "Error": "Invalid UPI ID format"}
        return {"Valid": True, "Error": None}
    return {"Valid": False, "Error": "Handle not found"}

def detect_upi_fraud(form_data):
    sender = form_data["sender"]
    receiver = form_data["receiver"]
    amount = form_data["amount"]
    hour = form_data["hour"]
    minute = form_data["minute"]
    second = form_data["second"]

    # Validate UPI IDs
    sender_valid = validate_upi_id(sender)
    receiver_valid = validate_upi_id(receiver)

    sender_label = 1 if not sender_valid["Valid"] else 0
    receiver_label = 1 if not receiver_valid["Valid"] else 0

    input_data = pd.DataFrame([{
        "Amount": amount,
        "Hours": hour,
        "Minutes": minute,
        "Seconds": second,
        "Sender Fraud Label": sender_label,
        "Receiver Fraud Label": receiver_label
    }])

    prediction = model.predict(input_data)[0]

    risk = []
    if sender_label:
        risk.append(f"Sender UPI Issue: {sender_valid['Error']}")
    if receiver_label:
        risk.append(f"Receiver UPI Issue: {receiver_valid['Error']}")
    if prediction == 1 and not risk:
        risk.append("Behavioral anomaly detected in transaction.")

    return {
        "is_fraud": prediction == 1,
        "risks": risk
    }
