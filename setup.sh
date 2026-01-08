#!/bin/bash
set -euo pipefail

echo "🔧 GMixer Setup (Bookworm-kompatibel) startet..."

# ----------------------------
# Helpers / User / Paths
# ----------------------------
if [[ "${EUID}" -ne 0 ]]; then
  echo "❌ Bitte als root ausführen: sudo ./setup.sh"
  exit 1
fi

# Realer Nutzer (wenn via sudo gestartet), sonst root
REAL_USER="${SUDO_USER:-root}"
REAL_HOME="$(eval echo "~$REAL_USER")"

# Installationsordner = Ordner dieser setup.sh (robust, egal wo du sie startest)
INSTALL_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MAIN_SCRIPT="${INSTALL_DIR}/main.py"
ICON_PATH="${INSTALL_DIR}/icon.png"

echo "📁 INSTALL_DIR: ${INSTALL_DIR}"
echo "👤 REAL_USER:   ${REAL_USER}"
echo "🏠 REAL_HOME:   ${REAL_HOME}"

if [[ ! -f "${MAIN_SCRIPT}" ]]; then
  echo "❌ main.py nicht gefunden unter: ${MAIN_SCRIPT}"
  echo "   Lege main.py in den gleichen Ordner wie setup.sh oder passe MAIN_SCRIPT an."
  exit 1
fi

# ----------------------------
# 1) Pakete installieren
# ----------------------------
echo "📦 Installiere Systemabhängigkeiten..."
apt update
apt install -y git python3 python3-pip python3-tk pigpio python3-gpiozero

# Optional (nur wenn du wirklich GUI/VNC willst):
# apt install -y raspberrypi-ui-mods

# ----------------------------
# 2) VNC aktivieren (wenn raspi-config vorhanden)
# ----------------------------
echo "⚙️ Konfiguriere VNC (falls möglich)..."
if command -v raspi-config >/dev/null 2>&1; then
  # 0 = enable
  raspi-config nonint do_vnc 0 || true
else
  echo "ℹ️ raspi-config nicht gefunden – überspringe VNC-Aktivierung."
fi

# ----------------------------
# 3) Display Rotation konfigurieren (Bookworm: /boot/firmware/config.txt)
# ----------------------------
echo "🖥️ Setze Display-Rotation (display_rotate=3)..."
CONFIG_FILE="/boot/firmware/config.txt"
if [[ -f "/boot/config.txt" && ! -f "${CONFIG_FILE}" ]]; then
  CONFIG_FILE="/boot/config.txt"
fi

if [[ -f "${CONFIG_FILE}" ]]; then
  if grep -qE '^\s*display_rotate=' "${CONFIG_FILE}"; then
    sed -i 's/^\s*display_rotate=.*/display_rotate=3/' "${CONFIG_FILE}"
  else
    echo "" >> "${CONFIG_FILE}"
    echo "# GMixer: rotate display 270°" >> "${CONFIG_FILE}"
    echo "display_rotate=3" >> "${CONFIG_FILE}"
  fi
else
  echo "⚠️ Konnte config.txt nicht finden – Rotation übersprungen."
fi

# ----------------------------
# 4) systemd Service erstellen
# ----------------------------
echo "🛠️ Erstelle systemd Service gmixer.service..."
SERVICE_PATH="/etc/systemd/system/gmixer.service"

cat > "${SERVICE_PATH}" <<EOF
[Unit]
Description=GMixer Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
ExecStart=/usr/bin/python3 ${MAIN_SCRIPT}
Restart=always
RestartSec=2
User=${REAL_USER}
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# ----------------------------
# 5) pigpiod + gmixer aktivieren
# ----------------------------
echo "🚀 Aktiviere Dienste (pigpiod, gmixer)..."
systemctl daemon-reload
systemctl enable --now pigpiod
systemctl enable --now gmixer.service

# ----------------------------
# 6) Desktop-Icon erstellen (Bookworm-sicher)
# ----------------------------
echo "🖥️ Erstelle Desktop-Icon (Bookworm-trusted)..."

# Desktop-Ordner sauber ermitteln (Desktop / Schreibtisch etc.)
DESKTOP_DIR=""
if command -v xdg-user-dir >/dev/null 2>&1; then
  DESKTOP_DIR="$(sudo -u "${REAL_USER}" xdg-user-dir DESKTOP 2>/dev/null || true)"
fi
# Fallbacks
if [[ -z "${DESKTOP_DIR}" || "${DESKTOP_DIR}" == "DESKTOP" ]]; then
  if [[ -d "${REAL_HOME}/Desktop" ]]; then
    DESKTOP_DIR="${REAL_HOME}/Desktop"
  elif [[ -d "${REAL_HOME}/Schreibtisch" ]]; then
    DESKTOP_DIR="${REAL_HOME}/Schreibtisch"
  else
    DESKTOP_DIR="${REAL_HOME}/Desktop"
  fi
fi

sudo -u "${REAL_USER}" mkdir -p "${DESKTOP_DIR}"
DESKTOP_FILE="${DESKTOP_DIR}/Getraenkemixer.desktop"

sudo -u "${REAL_USER}" bash -c "cat > '${DESKTOP_FILE}' <<EOF
[Desktop Entry]
Type=Application
Name=Getränkemixer
Comment=Startet das Getränkemixer-Programm
Exec=/usr/bin/python3 ${MAIN_SCRIPT}
Path=${INSTALL_DIR}
Icon=${ICON_PATH}
Terminal=false
Categories=Utility;
EOF"

chmod +x "${DESKTOP_FILE}"
chown "${REAL_USER}:${REAL_USER}" "${DESKTOP_FILE}"

# Bookworm: .desktop muss "trusted" sein, sonst wird's oft nicht als Launcher angezeigt
if command -v gio >/dev/null 2>&1; then
  sudo -u "${REAL_USER}" gio set "${DESKTOP_FILE}" metadata::trusted true 2>/dev/null || true
fi

# Hinweis falls Icon-Datei fehlt
if [[ ! -f "${ICON_PATH}" ]]; then
  echo "ℹ️ Hinweis: icon.png nicht gefunden unter ${ICON_PATH} – Desktop nutzt dann ein Standard-Icon."
fi

echo "✅ Setup abgeschlossen."
echo "➡️ Bitte einmal neu starten: sudo reboot"
