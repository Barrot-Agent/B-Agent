# Base image with Ubuntu
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Add GitHub Actions runner
WORKDIR /actions-runner
RUN curl -o actions-runner-linux-x64-2.329.0.tar.gz -L \
    https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz \
    && tar xzf ./actions-runner-linux-x64-2.329.0.tar.gz \
    && rm actions-runner-linux-x64-2.329.0.tar.gz

# Add entrypoint
ENTRYPOINT ["./run.sh"]
