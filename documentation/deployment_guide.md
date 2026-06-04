# Deployment Guide
## AI-Based Cryptocurrency Market Behavior Analyzer and Risk Predictor

---

## 1. Local Development

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Step-by-Step Setup

```bash
# 1. Clone the repository (or navigate to the project directory)
git clone <repository-url>
cd crypto_analyzer

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment variables template
cp .env.example .env
# Edit .env if you have API keys (optional — public endpoints work without keys)

# 6. Run the application
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure virtual environment is activated and `pip install -r requirements.txt` completed |
| Port 8501 in use | Use `streamlit run app.py --server.port=8502` |
| Binance API blocked | The app automatically falls back to Yahoo Finance |
| SSL certificate errors | Set `PYTHONHTTPSVERIFY=0` or update certificates |

---

## 2. Docker Deployment

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models/saved logs data/sample

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

### Docker Commands

```bash
# Build the image
docker build -t crypto-analyzer .

# Run the container
docker run -d \
    --name crypto-analyzer \
    -p 8501:8501 \
    -e LOG_LEVEL=INFO \
    crypto-analyzer

# View logs
docker logs -f crypto-analyzer

# Stop the container
docker stop crypto-analyzer

# Remove the container
docker rm crypto-analyzer
```

### Docker Compose (Optional)

```yaml
version: '3.8'
services:
  crypto-analyzer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./data/sample:/app/data/sample
      - ./models/saved:/app/models/saved
    restart: unless-stopped
```

```bash
# Start with docker-compose
docker-compose up -d

# Stop
docker-compose down
```

---

## 3. Streamlit Cloud Deployment

### Prerequisites
- GitHub account
- Repository pushed to GitHub

### Step-by-Step

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/<username>/<repo>.git
   git push -u origin main
   ```

2. **Connect to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set the main file path to `app.py`

3. **Configure Secrets**
   - In the Streamlit Cloud dashboard, go to **Settings → Secrets**
   - Add any environment variables:
     ```toml
     LOG_LEVEL = "INFO"
     BINANCE_API_KEY = "your_key_here"  # Optional
     ```

4. **Deploy**
   - Click "Deploy"
   - The app will be available at `https://<your-app>.streamlit.app`

### Streamlit Cloud Requirements
- Ensure `requirements.txt` is in the repository root
- The app must not exceed Streamlit Cloud's resource limits (1GB RAM, 1 CPU)
- API calls to external services (Binance, Yahoo Finance) must work from Streamlit Cloud's servers

---

## 4. Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging verbosity: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `BINANCE_API_KEY` | (empty) | Optional Binance API key for authenticated endpoints |
| `BINANCE_API_SECRET` | (empty) | Optional Binance API secret |
| `DEFAULT_COIN` | `BTCUSDT` | Default cryptocurrency symbol |
| `DEFAULT_INTERVAL` | `1d` | Default candlestick interval |
| `DEFAULT_LIMIT` | `500` | Default number of candles to fetch |

---

## 5. Resource Requirements

| Deployment | RAM | CPU | Storage |
|-----------|-----|-----|---------|
| Local Development | 2 GB | 2 cores | 500 MB |
| Docker | 2 GB | 2 cores | 1 GB (image) |
| Streamlit Cloud | 1 GB (limit) | 1 core (limit) | 500 MB |

---

## 6. Monitoring

### Logs
- Application logs are written to `logs/crypto_analyzer.log`
- Log rotation: 5 MB max file size, 3 backup files
- Docker: View logs with `docker logs -f crypto-analyzer`

### Health Check
- Streamlit provides a built-in health endpoint at `/_stcore/health`
- The Docker HEALTHCHECK directive monitors this endpoint
