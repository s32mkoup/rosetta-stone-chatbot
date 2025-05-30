#!/usr/bin/env python3
"""
Deployment script for Rosetta Stone Agent
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any

def create_docker_files():
    """Create Docker deployment files"""
    
    dockerfile_content = """
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/knowledge_base data/conversation_logs data/persona_memories data/templates

# Expose port
EXPOSE 7860

# Set environment variables
ENV PYTHONPATH=/app
ENV HF_TOKEN=""

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:7860/ || exit 1

# Run the application
CMD ["python", "main.py", "web", "--host", "0.0.0.0", "--port", "7860"]
"""
    
    docker_compose_content = """
version: '3.8'

services:
  rosetta-stone-agent:
    build: .
    ports:
      - "7860:7860"
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - PROVIDER=nebius
      - MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
"""
    
    # Write Dockerfile
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    print("✅ Created Dockerfile")
    
    # Write docker-compose.yml
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose_content)
    print("✅ Created docker-compose.yml")

def create_systemd_service():
    """Create systemd service file for Linux deployment"""
    
    current_dir = Path.cwd()
    python_path = shutil.which("python3") or shutil.which("python")
    
    service_content = f"""
[Unit]
Description=Rosetta Stone Agent
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'rosetta')}
WorkingDirectory={current_dir}
Environment=PYTHONPATH={current_dir}
Environment=HF_TOKEN={os.getenv('HF_TOKEN', '')}
ExecStart={python_path} main.py web --host 0.0.0.0 --port 7860
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "rosetta-stone-agent.service"
    with open(service_file, "w") as f:
        f.write(service_content)
    
    print(f"✅ Created {service_file}")
    print("To install as system service:")
    print(f"  sudo cp {service_file} /etc/systemd/system/")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable rosetta-stone-agent")
    print("  sudo systemctl start rosetta-stone-agent")

def create_nginx_config():
    """Create nginx configuration for reverse proxy"""
    
    nginx_config = """
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
"""
    
    with open("nginx-rosetta-stone.conf", "w") as f:
        f.write(nginx_config)
    
    print("✅ Created nginx-rosetta-stone.conf")
    print("To use with nginx:")
    print("  sudo cp nginx-rosetta-stone.conf /etc/nginx/sites-available/")
    print("  sudo ln -s /etc/nginx/sites-available/nginx-rosetta-stone.conf /etc/nginx/sites-enabled/")
    print("  sudo nginx -t && sudo systemctl reload nginx")

def create_heroku_files():
    """Create Heroku deployment files"""
    
    # Procfile
    procfile_content = "web: python main.py web --host 0.0.0.0 --port $PORT"
    with open("Procfile", "w") as f:
        f.write(procfile_content)
    print("✅ Created Procfile")
    
    # runtime.txt
    python_version = f"python-{sys.version.split()[0]}"
    with open("runtime.txt", "w") as f:
        f.write(python_version)
    print(f"✅ Created runtime.txt ({python_version})")
    
    # app.json
    app_json = {
        "name": "Rosetta Stone Agent",
        "description": "Ancient wisdom meets modern AI - An intelligent chatbot embodying the Rosetta Stone",
        "keywords": ["ai", "chatbot", "history", "education", "huggingface"],
        "website": "https://github.com/yourusername/rosetta-stone-agent",
        "repository": "https://github.com/yourusername/rosetta-stone-agent",
        "env": {
            "HF_TOKEN": {
                "description": "Hugging Face API token",
                "required": True
            },
            "PROVIDER": {
                "description": "LLM provider",
                "value": "nebius"
            },
            "MODEL_NAME": {
                "description": "Model name to use",
                "value": "meta-llama/Llama-3.1-8B-Instruct"
            }
        },
        "buildpacks": [
            {"url": "heroku/python"}
        ]
    }
    
    with open("app.json", "w") as f:
        json.dump(app_json, f, indent=2)
    print("✅ Created app.json")

def create_huggingface_space_files():
    """Create Hugging Face Spaces deployment files"""
    
    # app.py for Spaces
    app_py_content = """
#!/usr/bin/env python3
import os
from interfaces.gradio_app import create_gradio_app

# Create the Gradio app
app = create_gradio_app()

# Launch the app
if __name__ == "__main__":
    app.launch()
"""
    
    with open("app.py", "w") as f:
        f.write(app_py_content)
    print("✅ Created app.py for Hugging Face Spaces")
    
    # README for Spaces
    readme_content = """---
title: Rosetta Stone Agent
emoji: 🏺
colorFrom: yellow
colorTo: orange
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# 🏺 Rosetta Stone Agent

An intelligent AI agent that embodies the ancient Rosetta Stone, combining historical wisdom with modern AI capabilities.

## Features

- 🎭 Rich personality with millennia of memories
- 🧠 Advanced reasoning with tool integration
- 🛠️ Wikipedia, historical timeline, and translation tools
- 💾 Persistent memory and conversation tracking
- 🌐 Beautiful web interface

## Usage

Simply start a conversation and ask about:
- Ancient Egyptian history and culture
- Hieroglyphic translations
- Historical events and timelines
- Archaeological discoveries
- Cultural insights from antiquity

The agent responds as the actual Rosetta Stone with authentic personality and wisdom accumulated over millennia.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("✅ Created README.md for Hugging Face Spaces")

def deploy_to_docker():
    """Deploy using Docker"""
    print("🐳 Deploying with Docker...")
    
    try:
        # Build the image
        subprocess.run(["docker", "build", "-t", "rosetta-stone-agent", "."], check=True)
        print("✅ Docker image built successfully")
        
        # Provide run instructions
        print("\nTo run the container:")
        print("docker run -p 7860:7860 -e HF_TOKEN=your_token_here rosetta-stone-agent")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker build failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker first.")
        return False

def deploy_to_heroku():
    """Deploy to Heroku"""
    print("🚀 Deploying to Heroku...")
    
    try:
        # Check if Heroku CLI is installed
        subprocess.run(["heroku", "--version"], check=True, capture_output=True)
        
        print("Heroku CLI detected. Follow these steps:")
        print("1. heroku create your-app-name")
        print("2. heroku config:set HF_TOKEN=your_token_here")
        print("3. git add . && git commit -m 'Deploy to Heroku'")
        print("4. git push heroku main")
        
        return True
    except subprocess.CalledProcessError:
        print("❌ Heroku CLI not found. Please install Heroku CLI first.")
        return False
    except FileNotFoundError:
        print("❌ Heroku CLI not found. Please install Heroku CLI first.")
        return False

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Rosetta Stone Agent")
    parser.add_argument(
        "target",
        choices=["docker", "heroku", "systemd", "nginx", "hf-spaces", "files-only"],
        help="Deployment target"
    )
    parser.add_argument("--build", action="store_true", help="Build/deploy immediately")
    
    args = parser.parse_args()
    
    print("🏺 Rosetta Stone Agent - Deployment Script")
    print("=" * 50)
    
    if args.target == "docker":
        create_docker_files()
        if args.build:
            deploy_to_docker()
    
    elif args.target == "heroku":
        create_heroku_files()
        if args.build:
            deploy_to_heroku()
    
    elif args.target == "systemd":
        create_systemd_service()
    
    elif args.target == "nginx":
        create_nginx_config()
    
    elif args.target == "hf-spaces":
        create_huggingface_space_files()
    
    elif args.target == "files-only":
        create_docker_files()
        create_heroku_files()
        create_systemd_service()
        create_nginx_config()
        create_huggingface_space_files()
        print("✅ All deployment files created")
    
    print("\n🎉 Deployment preparation complete!")

if __name__ == "__main__":
    main()