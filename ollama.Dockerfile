FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    git \
    ca-certificates \
    && apt-get clean

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Pull the model ahead of time (optional; can also be done in entrypoint)
RUN ollama serve & \
    sleep 5 && \
    ollama pull codellama:7b && \
    pkill ollama

# Expose port
EXPOSE 11434

# Run Ollama in foreground
CMD ["ollama", "serve"]
