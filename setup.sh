#!/bin/bash

# --- Fehlerprüfung und Konfiguration ---
set -e # Beende das Skript bei Fehlern sofort

# Hole das Installationsverzeichnis (wird der Ort sein, von dem aus das Skript gestartet wird)
INSTALL_DIR=$(pwd) 
USER_NAME=$(whoami)

echo "🔧 Installiere und konfiguriere Getränkemixer-System..."

# 1. System updaten und notwendige Pakete installieren
echo "📦 Installiere Systemabhängigkeiten..."
sudo apt update
# Installiere git, Python-Tools, Tkinter, pigpio-Daemon und gpiozero
sudo apt install -y git python3 python3-pip python3-tk pigpio python3-gpiozero


# 2. VNC und Display-Rotation konfigurieren
echo "⚙️ Konfiguriere Display und VNC..."
# VNC aktivieren (non-interactive)
sudo raspi-config nonint do_vnc 0

# Display Rotation auf 270° setzen (display_rotate=3)
CONFIG_FILE="/boot/config.txt"
if [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
fi

if grep -q "display_rotate=" "$CONFIG_FILE"; then
    sudo sed -i 's/display_rotate=.*/display_rotate=3/' "$CONFIG_FILE"
else
    # Fügt die Zeile am Ende hinzu
    echo "display_rotate=3" | sudo tee -a "$CONFIG_FILE" > /dev/null
fi

# 3. systemd Service für den Autostart erstellen
SERVICE_PATH="/etc/systemd/system/gmixer.service"
MAIN_SCRIPT_PATH="$INSTALL_DIR/main.py" 

echo "🛠️ Erstelle systemd Service ($SERVICE_PATH) für Autostart..."
sudo tee $SERVICE_PATH > /dev/null <<EOF
[Unit]
Description=GMixer Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 $MAIN_SCRIPT_PATH
WorkingDirectory=$INSTALL_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$USER_NAME

[Install]
WantedBy=multi-user.target
EOF

# 4. systemd Service und pigpiod Daemon aktivieren und starten
echo "🚀 Aktiviere Autostart-Dienste (pigpiod, gmixer)..."
sudo systemctl daemon-reload
# Starte den pigpio-Daemon (notwendig für gpiozero/PiGPIOFactory)
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
# Starte den Gmixer-Service
sudo systemctl enable gmixer.service
sudo systemctl start gmixer.service 

# 5. Desktop-Icon erstellen (für einfachen Start, falls Autostart deaktiviert wird)
echo "🖥️ Erstelle Desktop-Icon..."
DESKTOP_PATH="/home/$USER_NAME/Desktop/Getraenkemixer.desktop"

echo "[Desktop Entry]
Type=Application
Name=Getränkemixer
Comment=Startet das Getränkemixer-Programm
Exec=/usr/bin/python3 $MAIN_SCRIPT_PATH
Path=$INSTALL_DIR
Icon=$INSTALL_DIR/icon.png
Terminal=false" | sudo tee $DESKTOP_PATH > /dev/null

sudo chmod +x $DESKTOP_PATH
sudo chown $USER_NAME:$USER_NAME $DESKTOP_PATH

echo "✅ Installation abgeschlossen!"
echo "Bitte starten Sie den Raspberry Pi einmal neu (sudo reboot), um die Display-Änderungen anzuwenden und den Gmixer automatisch zu starten."