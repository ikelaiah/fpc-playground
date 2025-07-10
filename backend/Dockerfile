FROM debian:12

# Install FPC and other dependencies
# Note: Using 'fpc' instead of 'fp-compiler' for the main compiler package
# Note: Added 'python3-venv' to avoid PEP 668 restrictions when installing Python packages
RUN apt-get update && apt-get install -y \
    fpc \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory and copy files
# Note: Copy requirements.txt first for better Docker layer caching
WORKDIR /app
COPY requirements.txt ./

# Create and activate virtual environment, then install packages
# Note: Using virtual environment to comply with PEP 668 and avoid --break-system-packages
# Note: This prevents "externally-managed-environment" error in modern Python installations
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy app code after installing dependencies (better layer caching)
COPY app/ ./

# Expose port 5000
EXPOSE 5000

# Run the server using the virtual environment Python interpreter
# Note: Must use /app/venv/bin/python instead of system python3 to access installed packages
CMD ["/app/venv/bin/python", "main.py"]