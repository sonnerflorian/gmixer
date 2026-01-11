# Getränkemischer
Software für den Getränkemixer der Technischen Hochschule Nürnberg

# Anleitung zur Einrichtung des Raspberry Pis und erstellen eines neuen Rezepts

## 1. EInrichten des Raspberry Pis

### Image auf SD-Karte schreiben

1. **Raspberry Pi Imager** von der offiziellen Seite herunterladen und installieren.
2. SD-Karte des Raspberry Pis in den Computer einstecken
3. Im Imager:
   - Betriebssystem auswählen  
     - `Raspberry Pi OS (32-bit)` (Bookworm)
   - SD-Karte auswählen.
   - Hostname wählen (gmixer)
   - Lokaliserung einrichten
   - Benutzername mit Passort wählen (Benutzername: gmixer, Passwort: pw)
   - WLAN-Daten eingeben
   - SSH-Aktivieren (Passwort zur Authentifizierung verwenden)
4. Image schreiben
5. SD-Karte in den Raspberry Pi stecken und Pi starten (durch Stromzufuhr).

---

### Erster Start und Grundkonfiguration

Beim ersten Start kann dies etwas länger Dauern.

**Fernzugriff per SSH**

Wichtig ist dass beide Geräte in einem Netzwerk sind, Eduroam funktioniert nicht.

Herausfinden der IP-Adresse
- Möglichkeit 1: Nach dem Start wird die Aktuelle IP-Adresse oben rechts kurz angezeigt
- Möglichkeit 2: über einen IP Scanner

Ist die IP-Adresse bekannt kann mit folgendem Befehl in einem Terminal eine SSH-Verbindung hergestellt werden:

```bash
ssh benutzername@<ip-des-pis>
# Beispiel:
ssh gmixer@10.252.252.114

```
Nun muss der Sicherheitschlüssel bestätigt werden und das zuvor gewählte Passwort eingegeben werden

Besteht eine verbindung wird im Terminal folgendes angezeigt

```
gmixer@gmixer:~$ 
```

Jetzt kann das aktuelle Github-Repo geklont werden

```bash
git clone https://github.com/sonnerflorian/gmixer.git
```
als nächstes wird die Datei setup.sh installiert, dafür muss zunächst in den eben geklonten Ordner gewechselt werden und anschließend die Datein installiert werden. DIes kann einen kurzen Moment Dauern:

```bash
cd gmixer/
sudo chmod +x setup.sh
./setup.sh
```
nun sollten der Raspberry Pi konfiguriert sein

### VNC Verbindung (Fernzugriff grafischer Steuerung)

***aktivieren des VNC-Servers auf dem Raspberry Pi (eigentlich nicht nötig)***

auf dem Raspi über SSH:

```bash
sudo raspi-config
```
Es öffnet sich ein Menü:

Interface options--> VNC --> enable

Warten bis VNC aktiviert wurde

**VNC Verbindung herstellen**
- Installieren eines VNC-Viewers z.b. von RealVNC
- Verninden via Eingabe der IP-Adresse
- Benutzername und Passwort eingeben
- Häckchen bei: Passwort merken

### Display drehen (eventuell nötig)

Über VNC
- Start Icon anklicken
-> Preferences
-> Screen configuration
- Screens (unten rechts)
-> Orientation
-> right
- Ausführen und Bestätigen 

## Programm starten

Das Hauptprogramm kann über das Icon auf dem Homescreen gestartet werden, es öffnet sich im Vollbildmodus
(schließen durch ESC)

[Install]
WantedBy=multi-user.target
Dann:

bash
Code kopieren
sudo systemctl daemon-reload
sudo systemctl enable gmixer.service
sudo systemctl start gmixer.service
