#!/bin/bash

Xvfb :0 -screen 0 1280x960x24 -listen tcp -ac +extension GLX +extension RENDER &

export DISPLAY=:0

fluxbox &

x11vnc -display :0 -forever -shared -rfbauth /root/.vnc/passwd -rfbport 5900 &

websockify --web=/usr/share/novnc 80 localhost:5900
