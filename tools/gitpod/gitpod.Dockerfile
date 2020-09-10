FROM gitpod/workspace-full-vnc

# Install dependencies
RUN sudo apt-get update \
    && sudo apt-get install -y libgtk-3-dev libsdl-dev python-pygame\
    && sudo sudo apt-get install python-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev python-numpy subversion libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev install libfreetype6-dev \
    && sudo apt-get clean && sudo rm -rf /var/cache/apt/* && sudo  rm -rf /var/lib/apt/lists/* && sudo rm -rf /tmp/*

