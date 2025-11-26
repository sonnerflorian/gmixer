# Getränkemixer
Software für den Getränkemixer der Technischen Hochschule Nürnberg

# GMixer – Getränkemixer mit Raspberry Pi

Dieses Projekt steuert einen Getränkemixer mit einem Raspberry Pi (z.B. Raspberry Pi Zero W / Zero 2).  
In dieser Anleitung wird beschrieben, wie du:

1. Einen neuen Raspberry Pi aufsetzt  
2. Display um 90° drehst  
3. WLAN einrichtest  
4. Das `gmixer`-Repository clonest und startklar machst  

---

## 1. Raspberry Pi vorbereiten

### 1.1. Image auf SD-Karte schreiben

1. **Raspberry Pi Imager** herunterladen und installieren (für Windows, macOS oder Linux).
2. SD-Karte einstecken.
3. Im Imager:
   - Betriebssystem auswählen, z.B.  
     - `Raspberry Pi OS (32-bit)` oder  
     - `Raspberry Pi OS Lite (32-bit)` (ohne Desktop)
   - SD-Karte auswählen.
4. Vor dem Schreiben auf das **Zahnradsymbol (Einstellungen)** klicken:
   - **Hostname** setzen (z.B. `gmixer`)
   - **SSH aktivieren** (z.B. “Enable SSH”)
   - **Benutzername & Passwort** setzen
   - **WLAN konfigurieren** (SSID, Passwort, Land – z.B. `DE`)
   - Tastaturlayout auf `de` / `German` stellen (optional, aber empfohlen)
5. Image schreiben und SD-Karte sicher entfernen.
6. SD-Karte in den Raspberry Pi stecken und Pi starten.

---

## 2. Erster Start und Grundkonfiguration

Verbinde dich entweder:

- mit Monitor, Tastatur und Maus **direkt am Pi**, oder  
- per **SSH** von deinem Rechner:

```bash
ssh benutzername@<ip-des-pis>
# Beispiel:
ssh pi@gmixer.local
2.1. System aktualisieren
bash
Code kopieren
sudo apt update
sudo apt upgrade -y
3. WLAN einrichten (falls noch nicht konfiguriert)
Falls WLAN nicht über den Imager gesetzt wurde, kannst du es nachträglich einrichten.

Variante 1: Über raspi-config
bash
Code kopieren
sudo raspi-config
Dann:

System Options → Wireless LAN

SSID (WLAN-Name) eingeben

Passwort eingeben

Beenden und neu starten:

bash
Code kopieren
sudo reboot
Variante 2: Direkt in wpa_supplicant.conf
bash
Code kopieren
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
Am Ende einfügen (falls noch nicht vorhanden):

conf
Code kopieren
network={
    ssid="DEIN_WLAN_NAME"
    psk="DEIN_WLAN_PASSWORT"
}
Speichern (Strg + O, Enter) und schließen (Strg + X), dann:

bash
Code kopieren
sudo wpa_cli -i wlan0 reconfigure
4. Display um 90° drehen
Je nach Raspberry-Pi-OS-Version liegt die Konfigurationsdatei unter:

/boot/firmware/config.txt (neue Raspberry Pi OS Versionen) oder

/boot/config.txt (ältere Versionen)

4.1. Datei öffnen
Versuche zuerst:

bash
Code kopieren
sudo nano /boot/firmware/config.txt
Falls es diese Datei nicht gibt, stattdessen:

bash
Code kopieren
sudo nano /boot/config.txt
4.2. Rotation setzen
Füge am Ende der Datei folgende Zeile ein:

c
Code kopieren
display_rotate=1
Bedeutung:

0 = 0° (Standard)

1 = 90°

2 = 180°

3 = 270°

Datei speichern und Pi neu starten:

bash
Code kopieren
sudo reboot
5. Git und Python installieren
Stelle sicher, dass git und Python installiert sind:

bash
Code kopieren
sudo apt update
sudo apt install -y git python3 python3-pip
(Optional, falls benötigt: weitere Pakete wie python3-venv)

6. gmixer-Repository clonen
Wechsle in ein Verzeichnis, in dem du das Projekt ablegen möchtest, z.B. ins Home-Verzeichnis:

bash
Code kopieren
cd ~
git clone https://github.com/sonnerflorian/gmixer.git
cd gmixer
7. Python-Abhängigkeiten installieren
Falls es eine requirements.txt im Repo gibt:

bash
Code kopieren
pip3 install -r requirements.txt
Alternativ können Abhängigkeiten auch direkt im README oder in der Projektbeschreibung aufgeführt sein – ggf. dort nachlesen.

8. Programm starten
(Anpassen an dein tatsächliches Startskript – Beispiel:)

bash
Code kopieren
python3 main.py
oder

bash
Code kopieren
python3 gmixer.py
Je nach Projektstruktur bitte den konkreten Dateinamen verwenden.

9. Autostart einrichten (optional)
Wenn der GMixer beim Systemstart automatisch starten soll, kannst du z.B. einen systemd-Service oder einen Eintrag in rc.local verwenden. Beispiel systemd (Platzhalter):

bash
Code kopieren
sudo nano /etc/systemd/system/gmixer.service
Inhalt (Beispiel, anpassen!):

ini
Code kopieren
[Unit]
Description=GMixer Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/gmixer/main.py
WorkingDirectory=/home/pi/gmixer
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
Dann:

bash
Code kopieren
sudo systemctl daemon-reload
sudo systemctl enable gmixer.service
sudo systemctl start gmixer.service