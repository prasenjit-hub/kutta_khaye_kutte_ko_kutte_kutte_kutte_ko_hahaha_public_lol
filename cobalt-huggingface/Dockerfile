FROM ghcr.io/imputnet/cobalt:latest

# API URL - required for Cobalt to start
ENV API_URL=https://raju014-cobalt-api.hf.space/

# HuggingFace uses port 7860
ENV API_PORT=7860
ENV API_LISTEN_ADDRESS=0.0.0.0

# Disable authentication (this makes it public - no API key needed)
ENV API_AUTH_REQUIRED=0

# Enable CORS for external access
ENV CORS_WILDCARD=1
ENV CORS_URL=*

# Expose the port HuggingFace expects
EXPOSE 7860
