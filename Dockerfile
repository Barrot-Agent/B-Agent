# Base image with Ubuntu
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy site files
COPY site/ /app/site/

# Expose port
EXPOSE 8080

# Serve static files with Python's built-in HTTP server
# Use PORT environment variable if set, otherwise default to 8080
CMD python3 -m http.server ${PORT:-8080} --directory site
