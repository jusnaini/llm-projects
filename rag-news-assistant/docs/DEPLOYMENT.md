# Deployment Guide

## Overview

This guide covers deploying the RAG News Assistant in various environments, from local development to production systems.

## Local Development

### Prerequisites
- Python 3.10+
- Conda or pip
- 4GB+ RAM
- Stable internet connection (for model downloads)

### Quick Start
```bash
# Clone or navigate to project
cd rag-news-assistant

# Setup environment
conda create -y -p ./condaenv python=3.10
conda activate ./condaenv
conda install -y -c conda-forge faiss-cpu
pip install -r requirements.txt

# Run application
streamlit run app.py
```

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install FAISS
RUN pip install faiss-cpu

# Copy application files
COPY . .

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  rag-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped
```

### Build and Run
```bash
# Build image
docker build -t rag-news-assistant .

# Run container
docker run -p 8501:8501 rag-news-assistant

# Or use docker-compose
docker-compose up -d
```

## Cloud Deployment

### Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/rag-news-assistant.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set deployment settings:
     - Python version: 3.10
     - Requirements file: requirements.txt
   - Deploy

### Heroku

1. **Create Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Create runtime.txt**
   ```
   python-3.10.18
   ```

3. **Deploy**
   ```bash
   heroku create your-app-name
   git push heroku main
   heroku open
   ```

### AWS EC2

1. **Launch EC2 Instance**
   - Ubuntu 20.04 LTS
   - t3.medium or larger (4GB+ RAM)
   - Security group: allow port 8501

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv
   sudo apt install build-essential
   ```

3. **Setup Application**
   ```bash
   git clone https://github.com/yourusername/rag-news-assistant.git
   cd rag-news-assistant
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install faiss-cpu
   ```

4. **Run with Systemd**
   ```bash
   # Create service file
   sudo nano /etc/systemd/system/rag-app.service
   ```

   ```ini
   [Unit]
   Description=RAG News Assistant
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/rag-news-assistant
   Environment=PATH=/home/ubuntu/rag-news-assistant/venv/bin
   ExecStart=/home/ubuntu/rag-news-assistant/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   # Start service
   sudo systemctl enable rag-app
   sudo systemctl start rag-app
   ```

### Google Cloud Platform

1. **Create App Engine**
   ```yaml
   # app.yaml
   runtime: python310
   entrypoint: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0

   env_variables:
     STREAMLIT_SERVER_PORT: "8080"
     STREAMLIT_SERVER_ADDRESS: "0.0.0.0"
   ```

2. **Deploy**
   ```bash
   gcloud app deploy
   ```

## Production Considerations

### Performance Optimization

1. **Model Caching**
   ```python
   import os
   os.environ['TRANSFORMERS_CACHE'] = '/app/models'
   os.environ['HF_HOME'] = '/app/models'
   ```

2. **Memory Management**
   ```python
   # In rag_pipeline.py
   import gc
   
   def __del__(self):
       del self.embedder
       del self.generator
       gc.collect()
   ```

3. **Load Balancing**
   - Use multiple instances behind a load balancer
   - Implement health checks
   - Use sticky sessions for conversation history

### Security

1. **Environment Variables**
   ```bash
   export STREAMLIT_SERVER_HEADLESS=true
   export STREAMLIT_SERVER_ENABLE_CORS=false
   export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
   ```

2. **Authentication**
   ```python
   # Add to app.py
   import streamlit_authenticator as stauth
   
   names = ['admin']
   usernames = ['admin']
   passwords = ['password123']
   
   hashed_passwords = stauth.Hasher(passwords).generate()
   authenticator = stauth.Authenticate(names, usernames, hashed_passwords, 'cookie_name', 'key', cookie_expiry_days=30)
   ```

3. **HTTPS**
   - Use reverse proxy (nginx) with SSL certificates
   - Configure Streamlit for HTTPS

### Monitoring

1. **Logging**
   ```python
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.FileHandler('app.log'),
           logging.StreamHandler()
       ]
   )
   ```

2. **Health Checks**
   ```python
   # Add health check endpoint
   if st.button("Health Check"):
       try:
           test_answer = pipeline.answer("test")
           st.success("System healthy")
       except Exception as e:
           st.error(f"System error: {e}")
   ```

3. **Metrics**
   - Response time monitoring
   - Error rate tracking
   - Memory usage monitoring
   - User activity analytics

## Scaling Strategies

### Horizontal Scaling

1. **Multiple Instances**
   - Deploy multiple containers/instances
   - Use load balancer for distribution
   - Implement session management

2. **Microservices**
   - Separate embedding service
   - Separate generation service
   - Use message queues for communication

### Vertical Scaling

1. **Resource Allocation**
   - Increase CPU cores
   - Add more RAM
   - Use GPU acceleration

2. **Model Optimization**
   - Model quantization
   - Model distillation
   - Batch processing

## Backup and Recovery

### Data Backup
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Backup models (if cached locally)
tar -czf models-backup-$(date +%Y%m%d).tar.gz ~/.cache/huggingface/
```

### Disaster Recovery
1. **Automated Backups**
   - Schedule regular backups
   - Store in multiple locations
   - Test recovery procedures

2. **Rollback Strategy**
   - Version control for code
   - Database snapshots
   - Blue-green deployment

## Cost Optimization

### Cloud Cost Management
1. **Resource Right-sizing**
   - Monitor usage patterns
   - Scale down during low usage
   - Use spot instances where possible

2. **Caching Strategies**
   - Cache models locally
   - Implement CDN for static assets
   - Use Redis for session storage

3. **Model Selection**
   - Use smaller models for development
   - Optimize model size vs. quality trade-offs
   - Consider model hosting services

## Troubleshooting

### Common Issues

1. **Memory Issues**
   ```bash
   # Monitor memory usage
   htop
   free -h
   
   # Increase swap space
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

2. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep 8501
   
   # Kill process using port
   sudo kill -9 <PID>
   ```

3. **Model Download Issues**
   ```bash
   # Clear cache
   rm -rf ~/.cache/huggingface/
   
   # Set proxy if needed
   export HTTP_PROXY=http://proxy:port
   export HTTPS_PROXY=http://proxy:port
   ```

### Support and Maintenance

1. **Regular Updates**
   - Update dependencies monthly
   - Monitor security advisories
   - Test updates in staging environment

2. **Performance Monitoring**
   - Set up alerts for high response times
   - Monitor error rates
   - Track user satisfaction metrics

3. **Documentation**
   - Keep deployment docs updated
   - Document configuration changes
   - Maintain runbooks for common issues 