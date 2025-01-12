# Use the official Python image as a base
ARG VARIANT="3.10"
FROM python:${VARIANT}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y \
    fonts-ipafont-gothic \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*    

# Create a working directory
WORKDIR /workspace

# Install Python dependencies
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set up a non-root user for VSCode
ARG USERNAME=vscode
RUN useradd -m $USERNAME \
    && chown -R $USERNAME /workspace

# Set default user
USER $USERNAME