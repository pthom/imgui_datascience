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
# RUN sudo apt-get install -y \  
#   ffmpeg libswscale-dev libavformat-dev libavcodec-dev install

RUN pip install pygame matplotlib opencv-python imgui[pygame] enum34 xxhash

# RUN sudo apt-get clean \
#     && sudo rm -rf /var/cache/apt/* \
#     && sudo rm -rf /var/lib/apt/lists/* \ 
#     && sudo rm -rf /tmp/*

