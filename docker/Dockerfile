# Use Selenium + Chromium image for ARM64 (Apple Silicon) or Linux
FROM seleniarm/standalone-chromium:latest

# Become root so we can install Python
USER root

# Install Python + venv + pip
RUN apt-get update && \
    apt-get install -y python3 python3-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Create app folder
WORKDIR /app

# Copy your Python code
COPY lib/ ./lib/

# Create a virtual environment for Python packages
RUN python3 -m venv /opt/venv

# Upgrade pip inside venv
RUN /opt/venv/bin/pip install --upgrade pip

# Install your requirements inside the virtual environment
RUN /opt/venv/bin/pip install --no-cache-dir -r lib/requirements.txt

# Ensure Python uses the virtual environment
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app

# Run the scraper module
CMD ["python3", "-m", "lib.pitchfork_scraper"]
