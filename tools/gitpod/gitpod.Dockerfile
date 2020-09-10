FROM gitpod/workspace-full-vnc

# Install dependencies
RUN sudo apt-get update \
    && sudo apt-get install -y libgtk-3-dev \
    && sudo apt-get clean && sudo rm -rf /var/cache/apt/* && sudo  rm -rf /var/lib/apt/lists/* && sudo rm -rf /tmp/*

