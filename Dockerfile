# Use a slim Python image
FROM python:3.11-slim

# Install zbar and other system dependencies
RUN apt-get update && apt-get install -y libzbar0

# Set working directory
WORKDIR /app

# Copy dependencies and install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy all app files
COPY . .

# Expose port (Render provides PORT env variable)
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
