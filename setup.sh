#!/bin/bash

echo "🔧 Installiere Getränkemixer..."

# 1. System updaten
sudo apt update
sudo apt install -y python3 python3-pip python3-tk


# 2. Desktop-Icon erstellen
echo "[Desktop Entry]
Type=Application
Name=Getränkemixer
Comment=Startet das Getränkemixer-Programm
Exec=/usr/bin/python3 /home/gmixer/gmixer/main.py
Path=/home/gmixer/gmixer
Icon=/home/gmixer/gmixer/icon.png
Terminal=false" > /home/gmixer/Desktop/Getraenkemixer.desktop

chmod +x /home/gmixer/Desktop/Getraenkemixer.desktop


sudo systemctl daemon-reload
sudo systemctl enable getraenkemixer.service

echo "✅ Installation abgeschlossen!"
