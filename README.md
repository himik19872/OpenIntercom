
# SIP Doorphone on OpenIPC

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenIPC](https://img.shields.io/badge/OpenIPC-Compatible-brightgreen)](https://openipc.org)

Transform any compatible IP camera with OpenIPC firmware into a **full-featured SIP doorphone** with RFID/QR access, web management, remote door control, and backup system.


- [Updates & Changelog](#updates--changelog)
- [License](#license)

## ✨ Features

| Feature | Description | Status |
|---------|-------------|--------|
| **SIP Calling** | Make calls to SIP server when doorbell pressed | ✅ Stable |
| **RFID Keys** | Wiegand 26/34 RFID reader support | ✅ Stable |
| **QR Codes** | Generate and scan QR code keys | ✅ NEW |
| **Temporary Keys** | Time-limited access codes | ✅ NEW |
| **Sound Effects** | Play sounds on door events | ✅ NEW |
| **Backup System** | Full configuration backup/restore | ✅ NEW |
| **Web Interface** | Complete management via browser | ✅ Stable |
| **Door Sensor** | Magnetic contact for door status | ✅ Stable |
| **Exit Button** | Internal door release button | ✅ Stable |
| **Event History** | Log of all door events | ✅ Stable |

## Hardware Requirements

| Component | Recommended | Notes |
|-----------|-------------|-------|
| **IP Camera** | Uniview C1L-2WN-G with SSC335DE | "People's camera for $5" |
| **Microcontroller** | ESP32 (LilyGo T-Call) or ESP8266 | For door control |
| **RFID Reader** | Wiegand 26/34 (3.3V or 5V) | Any standard reader |
| **Relay Module** | 1-channel 5V relay | For door lock control |
| **Reed Switch** | NC magnetic contact | Door position sensor |
| **Buttons** | 2x momentary buttons | Exit and call buttons |
| **Power Supply** | 12V for lock, 5V for ESP | External power |
| **Speaker** | 8Ω 0.5W speaker | For sound effects |

## Software Requirements
- OpenIPC firmware with VoIP support
- Arduino IDE for ESP32/ESP8266
- Web browser (Chrome, Firefox, Yandex Browser)
- SSH client (PuTTY, Terminal)

---

# 🚀 One-Command Installation for OpenIPC Doorphone

Once you have OpenIPC firmware with VoIP support installed on your camera, you can turn it into a full-featured SIP doorphone with just one command.

## 📋 Prerequisites

- ✅ OpenIPC firmware with VoIP support installed
- ✅ Camera connected to network (DHCP recommended)
- ✅ SSH access to camera (default: root/123456)
- ✅ Internet connection for downloading files

## 🔧 Quick Installation

### Method 1: Using curl (recommended)

SSH into your camera and run:

```bash
curl -sL https://raw.githubusercontent.com/OpenIPC/intercom/main/install.sh | sh
Method 2: Using wget
bash
wget -qO- https://raw.githubusercontent.com/OpenIPC/intercom/main/install.sh | sh
Method 3: Manual download and run
bash
# Download the installer
wget -O /tmp/install.sh https://raw.githubusercontent.com/OpenIPC/intercom/main/install.sh

# Make it executable
chmod +x /tmp/install.sh

# Run the installer
/tmp/install.sh
📋 What the installer does
The installer will automatically:

Step	Action
1️⃣	Detect available UART ports (ttyS0, ttyS1, ttyS2, ttyAMA0)
2️⃣	Create necessary directories
3️⃣	Download all required files from GitHub
4️⃣	Install CGI scripts to /var/www/cgi-bin/p/
5️⃣	Install system scripts to /usr/bin/
6️⃣	Configure UART permissions in /etc/rc.local
7️⃣	Set up backup server on port 8080
8️⃣	Create keys database with test keys
9️⃣	Configure autostart for door monitor
🔟	Start all services
🌐 After Installation
Once installation is complete, you can access:

Interface	URL	Description
Main Web UI	http://CAMERA_IP	Standard OpenIPC interface
Door Phone	http://CAMERA_IP/cgi-bin/p/door_keys.cgi	Key management (in Extensions menu)
SIP Settings	http://CAMERA_IP/cgi-bin/p/sip_manager.cgi	SIP account configuration
QR Generator	http://CAMERA_IP/cgi-bin/p/qr_generator.cgi	Create QR code keys
Temporary Keys	http://CAMERA_IP/cgi-bin/p/temp_keys.cgi	Time-limited access codes
Sound Effects	http://CAMERA_IP/cgi-bin/p/sounds.cgi	Test door sounds
Event History	http://CAMERA_IP/cgi-bin/p/door_history.cgi	View all door events
Backup Manager	http://CAMERA_IP:8080/cgi-bin/p/backup_manager.cgi	Backup/restore configuration
🔑 Test Keys
The installer adds these test keys:

12345678 - Admin (RFID)

qrdemo - QR Test (QR code)

0000 - Master (RFID)

📋 Useful Commands
bash
# Check service status
ps | grep -E 'door_monitor|httpd|baresip'

# View door logs
tail -f /var/log/door_monitor.log

# Add a new key
echo "12345|User Name|$(date +%Y-%m-%d)" >> /etc/door_keys.conf

# Restart door monitor
/etc/init.d/S99door restart

# Update all files (re-run installer)
curl -sL https://raw.githubusercontent.com/OpenIPC/intercom/main/install.sh | sh
⚙️ Hardware Setup
UART Connection
The installer detects your UART port automatically. Connect your ESP32/ESP8266 to:

Camera	ESP32
TX (GPIO13)	RX (GPIO13)
RX (GPIO15)	TX (GPIO15)
GND	GND
Wiring Diagram
text
ESP32 (LilyGo T-Call)    Connected Devices
─────────────────────────────────────────────────
GPIO4  ────────────────► RFID Reader DATA0
GPIO5  ────────────────► RFID Reader DATA1
3.3V/5V ───────────────► RFID Reader VCC
GND    ────────────────► RFID Reader GND

GPIO32 ────────────────► Exit Button (to GND)
GPIO33 ────────────────► Call Button (to GND)

GPIO14 ────────────────► Relay Module IN
5V    ────────────────► Relay Module VCC
GND   ────────────────► Relay Module GND

GPIO12 ────────────────► Reed Switch (to GND)

GPIO13 (RX2) ──────────► Camera TX (GPIO13)
GPIO15 (TX2) ──────────► Camera RX (GPIO15)
GND   ─────────────────► Camera GND

External 12V ──────────► Lock (via relay contacts)
🔧 ESP32 Firmware
Upload the ESP32 firmware from the /firmware folder in the repository.

🐛 Troubleshooting
Problem	Solution
Installation fails	Check internet connection, re-run installer
404 errors during install	GitHub files missing - check repository
Services not starting	Run /etc/init.d/S99door restart
Backup manager 404	Check httpd on port 8080: ps | grep httpd
No UART found	Check connections: ls -la /dev/tty*
📦 Repository Structure
text
intercom/
├── install.sh                 # Main installer
├── www/
│   └── cgi-bin/
│       ├── backup.cgi         # Redirect to port 8080
│       └── p/                 # All doorphone CGI scripts
│           ├── door_keys.cgi
│           ├── sip_manager.cgi
│           ├── qr_generator.cgi
│           └── ...
├── usr/
│   └── bin/
│       ├── door_monitor.sh    # Main monitor script
│       └── check_temp_keys.sh  # Temp keys cleanup
├── etc/
│   ├── door_keys.conf         # Keys database template
│   └── baresip/               # SIP configuration
│       ├── accounts
│       └── call_number
└── sounds/                    # Sound effects (optional)
    ├── ring.pcm
    ├── door_open.pcm
    └── ...
🎉 Success!
After successful installation, you'll see:

text
==========================================
✅ Installation complete!
==========================================

📱 Main web interface: http://192.168.1.28
💾 Backup manager:     http://192.168.1.28:8080/cgi-bin/p/backup_manager.cgi
🔌 UART device:        /dev/ttyAMA0

🔑 Test keys:
  - 12345678 (Admin)
  - qrdemo (QR Test)
  - 0000 (Master)

==========================================
Enjoy your OpenIPC Doorphone!
==========================================
