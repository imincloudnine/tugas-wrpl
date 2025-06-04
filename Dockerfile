FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (jika requirements.txt ada di root)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh folder test-driven-dev ke dalam container
COPY test-driven-dev/ /app

EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]
CMD ["BouShopApp.py", "--server.port=8501", "--server.address=0.0.0.0"]
