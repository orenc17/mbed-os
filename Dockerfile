FROM gitpod/workspace-full:latest

USER root
# Install custom tools, runtime, etc.
RUN add-apt-repository -y ppa:team-gcc-arm-embedded/ppa && \
    apt-get update && \
    apt-get install -y gcc-arm-embedded && \
    apt-get clean && \
    rm -rf /var/cache/apt/* && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*
    
