FROM gitpod/workspace-full-vnc

# Install dependencies
RUN sudo apt-get update
RUN sudo apt-get install -y libgtk-3-dev libsdl-dev python-pygame
RUN sudo apt-get install -y \
  python-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev
RUN sudo apt-get install -y \
  libsdl1.2-dev libsmpeg-dev python-numpy subversion libportmidi-dev
RUN sudo apt-get install -y \
  libfreetype6-dev
RUN sudo apt-get install -y \
   python3-tk
RUN sudo apt-get clean \
    && sudo rm -rf /var/cache/apt/* \
    && sudo rm -rf /var/lib/apt/lists/* \
    && sudo rm -rf /tmp/*

RUN pip install pygame matplotlib opencv-python imgui[pygame] enum34 xxhash

# Change the default start-vnc-session.sh for a version with lower screen resolution
COPY tools/gitpod/start-vnc-session.sh /usr/bin/
RUN sudo chmod +x /usr/bin/start-vnc-session.sh
