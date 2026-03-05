📝 README.md (English)
markdown
# SIP Doorphone on OpenIPC

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenIPC](https://img.shields.io/badge/OpenIPC-Compatible-brightgreen)](https://openipc.org)

Transform any compatible IP camera with OpenIPC firmware into a **full-featured SIP doorphone** with RFID/QR access, web management, remote door control, and backup system.

## 📋 Table of Contents
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Quick Start](#quick-start)
- [Step 1: Flash OpenIPC with VoIP](#step-1-flash-openipc-with-voip)
- [Step 2: Initial Camera Setup](#step-2-initial-camera-setup)
- [Step 3: ESP32/ESP8266 Controller](#step-3-esp32esp8266-controller)
- [Step 4: Web Interface Installation](#step-4-web-interface-installation)
- [Step 5: SIP Configuration](#step-5-sip-configuration)
- [Step 6: Advanced Features](#step-6-advanced-features)
  - [6.1 QR Code Keys](#61-qr-code-keys)
  - [6.2 Temporary Keys](#62-temporary-keys)
  - [6.3 Sound Effects](#63-sound-effects)
  - [6.4 Backup System](#64-backup-system)
- [Step 7: Testing](#step-7-testing)
- [Troubleshooting](#troubleshooting)
- [File Structure](#file-structure)
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

## Quick Start

```bash
# 1. SSH into camera
ssh root@192.168.1.4  # password: 123456

# 2. Download and install web interface
wget -O /tmp/intercom.tar.gz https://github.com/OpenIPC/intercom/archive/main.tar.gz
tar -xzf /tmp/intercom.tar.gz -C /tmp
cp -r /tmp/intercom-main/cgi-bin/* /var/www/cgi-bin/
chmod +x /var/www/cgi-bin/p/*.cgi

# 3. Start HTTP server for backups
httpd -p 8080 -h /var/www &
echo 'httpd -p 8080 -h /var/www &' >> /etc/rc.local

# 4. Open web interface
# Main UI: http://192.168.1.4
# Backup manager: http://192.168.1.4:8080/cgi-bin/p/backup_manager.cgi
Step 1: Flash OpenIPC with VoIP Support
1.1 Download firmware
bash
# Base firmware
wget https://github.com/OpenIPC/firmware/releases/download/image/openipc-ssc335de-nor-ultimate.bin

# VoIP update for Uniview C1L
wget https://github.com/OpenIPC/builder/releases/download/latest/ssc335de_ultimate_uniview-c1l-2wn-g-voip-nor.tgz
1.2 Flash using programmer
Use SPI programmer (CH341A, etc.) to flash openipc-ssc335de-nor-ultimate.bin to the camera's NOR flash.

1.3 First boot and network connection
Connect camera via Ethernet (DHCP required). Find its IP address from router DHCP leases.

1.4 Update to VoIP firmware
bash
# SSH into camera
ssh root@192.168.1.x  # default password: 123456

# Update firmware (DO NOT use web interface!)
sysupgrade -k -r -f -n -z --url=https://github.com/OpenIPC/builder/releases/download/latest/ssc335de_ultimate_uniview-c1l-2wn-g-voip-nor.tgz

# Reboot
reboot
1.5 Configure WiFi (if needed)
bash
fw_setenv wlanssid "YourWiFiSSID"
fw_setenv wlanpass "YourWiFiPassword"
reboot
Step 2: Initial Camera Setup
2.1 Connect via SSH
bash
ssh root@192.168.1.4  # Use your camera's IP
2.2 Configure UART for ESP communication
bash
# Set permissions for UART
chmod 666 /dev/ttyS0
chmod 666 /dev/ttyAMA0 2>/dev/null

# Add to autostart
echo 'chmod 666 /dev/ttyS0' >> /etc/rc.local
echo 'chmod 666 /dev/ttyAMA0' >> /etc/rc.local 2>/dev/null
2.3 Check UART ports
bash
ls -la /dev/tty*
# Should show ttyS0, ttyS1, ttyS2 (or ttyAMA0)
2.4 Install required packages
bash
# Update and install (if needed)
opkg update
opkg install coreutils-stat coreutils-stty 2>/dev/null
Step 3: ESP32/ESP8266 Controller
3.1 Wiring Diagram
text
ESP32 (LilyGo T-Call)    Connected Devices
─────────────────────────────────────────────────
GPIO4  ────────────────► RFID Reader DATA0
GPIO5  ────────────────► RFID Reader DATA1
3.3V/5V ───────────────► RFID Reader VCC
GND    ────────────────► RFID Reader GND

GPIO32 ────────────────► Exit Button (other pin to GND)
GPIO33 ────────────────► Call Button (other pin to GND)

GPIO14 ────────────────► Relay Module IN
5V    ────────────────► Relay Module VCC
GND   ────────────────► Relay Module GND

GPIO12 ────────────────► Reed Switch (other pin to GND)

GPIO13 (RX2) ──────────► Camera TX (GPIO13)
GPIO15 (TX2) ──────────► Camera RX (GPIO15)
GND   ─────────────────► Camera GND

GPIO25 ────────────────► Speaker + (via 100µF capacitor)
GND   ────────────────► Speaker -

External 12V ──────────► Lock (via relay contacts)
3.2 ESP32 Firmware
<details> <summary>📁 Click to expand ESP32 full code</summary>
cpp
/*
 * OpenIPC SIP Doorphone - ESP32 Controller
 * Supports: RFID (Wiegand), Buttons, Relay, Reed Switch, Speaker
 */

#include <Arduino.h>

// Pin Definitions
#define PIN_RFID_D0    4
#define PIN_RFID_D1    5
#define PIN_BUTTON_EXIT 32
#define PIN_BUTTON_CALL 33
#define PIN_RELAY      14
#define PIN_REED_SWITCH 12
#define PIN_SPEAKER     25

// UART for camera communication
#define CAMERA_BAUD    115200

// RFID Wiegand variables
volatile unsigned long rfidCardNum = 0;
volatile int rfidBitCount = 0;
volatile unsigned long rfidLastBitTime = 0;
bool rfidReading = false;

// Button states
bool lastExitState = HIGH;
bool lastCallState = HIGH;
bool doorState = false;
bool lastDoorState = false;

// Timing
unsigned long lastStatusTime = 0;
const unsigned long STATUS_INTERVAL = 5000; // Send status every 5 seconds

//==============================================================================
// RFID Wiegand Interrupt Handlers
//==============================================================================
void IRAM_ATTR rfidD0Interrupt() {
  rfidLastBitTime = millis();
  rfidCardNum = (rfidCardNum << 1) | 0;
  rfidBitCount++;
  rfidReading = true;
}

void IRAM_ATTR rfidD1Interrupt() {
  rfidLastBitTime = millis();
  rfidCardNum = (rfidCardNum << 1) | 1;
  rfidBitCount++;
  rfidReading = true;
}

//==============================================================================
// Send command to camera
//==============================================================================
void sendToCamera(const char* cmd) {
  Serial2.println(cmd);
  Serial2.flush();
  Serial.print("[CAM] ");
  Serial.println(cmd);
}

//==============================================================================
// Play tone on speaker
//==============================================================================
void playTone(int frequency, int duration) {
  ledcWriteTone(0, frequency);
  delay(duration);
  ledcWriteTone(0, 0);
}

//==============================================================================
// Play sound effects
//==============================================================================
void playSound(const char* sound) {
  if (strcmp(sound, "door_open") == 0) {
    // Success sound
    playTone(1000, 100);
    delay(50);
    playTone(1500, 200);
  } else if (strcmp(sound, "door_close") == 0) {
    // Door closed sound
    playTone(500, 100);
  } else if (strcmp(sound, "key_denied") == 0) {
    // Denied sound
    playTone(300, 300);
  } else if (strcmp(sound, "button_beep") == 0) {
    // Button press sound
    playTone(800, 50);
  }
}

//==============================================================================
// Process RFID card
//==============================================================================
void processRFID() {
  if (rfidBitCount > 0 && rfidBitCount <= 64) {
    unsigned long now = millis();
    if (now - rfidLastBitTime > 50) { // 50ms no new bits = card read complete
      
      char cardStr[20];
      sprintf(cardStr, "KEY:%lu", rfidCardNum);
      sendToCamera(cardStr);
      
      // Reset for next card
      rfidCardNum = 0;
      rfidBitCount = 0;
      rfidReading = false;
    }
  }
}

//==============================================================================
// Setup
//==============================================================================
void setup() {
  Serial.begin(115200);
  Serial.println("\n==================================");
  Serial.println("OpenIPC SIP Doorphone - ESP32");
  Serial.println("==================================");
  
  // Configure pins
  pinMode(PIN_RFID_D0, INPUT_PULLUP);
  pinMode(PIN_RFID_D1, INPUT_PULLUP);
  pinMode(PIN_BUTTON_EXIT, INPUT_PULLUP);
  pinMode(PIN_BUTTON_CALL, INPUT_PULLUP);
  pinMode(PIN_RELAY, OUTPUT);
  pinMode(PIN_REED_SWITCH, INPUT_PULLUP);
  pinMode(PIN_SPEAKER, OUTPUT);
  
  digitalWrite(PIN_RELAY, LOW);
  
  // Configure speaker PWM
  ledcSetup(0, 1000, 8);
  ledcAttachPin(PIN_SPEAKER, 0);
  
  // Attach RFID interrupts
  attachInterrupt(digitalPinToInterrupt(PIN_RFID_D0), rfidD0Interrupt, FALLING);
  attachInterrupt(digitalPinToInterrupt(PIN_RFID_D1), rfidD1Interrupt, FALLING);
  
  // Initialize camera UART
  Serial2.begin(CAMERA_BAUD, SERIAL_8N1, 13, 15);
  Serial.println("Camera UART initialized");
  
  // Test beep
  playSound("door_open");
  
  Serial.println("ESP32 ready!");
  sendToCamera("ESP32_READY");
  
  lastStatusTime = millis();
}

//==============================================================================
// Main loop
//==============================================================================
void loop() {
  unsigned long now = millis();
  
  //--------------------------------------------------------------------------
  // Process RFID
  //--------------------------------------------------------------------------
  if (rfidReading) {
    processRFID();
  }
  
  //--------------------------------------------------------------------------
  // Read buttons
  //--------------------------------------------------------------------------
  bool exitState = digitalRead(PIN_BUTTON_EXIT);
  if (exitState == LOW && lastExitState == HIGH) {
    Serial.println("Exit button pressed");
    playSound("button_beep");
    sendToCamera("BUTTON:EXIT");
    digitalWrite(PIN_RELAY, HIGH);
    delay(500);
    digitalWrite(PIN_RELAY, LOW);
  }
  lastExitState = exitState;
  
  bool callState = digitalRead(PIN_BUTTON_CALL);
  if (callState == LOW && lastCallState == HIGH) {
    Serial.println("Call button pressed");
    playSound("button_beep");
    sendToCamera("CALL:");
  }
  lastCallState = callState;
  
  //--------------------------------------------------------------------------
  // Read door sensor
  //--------------------------------------------------------------------------
  doorState = (digitalRead(PIN_REED_SWITCH) == LOW);
  if (doorState != lastDoorState) {
    if (doorState) {
      Serial.println("Door closed");
      playSound("door_close");
      sendToCamera("DOOR:CLOSED");
    } else {
      Serial.println("Door opened");
      playSound("door_open");
      sendToCamera("DOOR:OPEN");
    }
    lastDoorState = doorState;
  }
  
  //--------------------------------------------------------------------------
  // Read commands from camera
  //--------------------------------------------------------------------------
  while (Serial2.available()) {
    String cmd = Serial2.readStringUntil('\n');
    cmd.trim();
    
    if (cmd.length() > 0) {
      Serial.print("[CAM] Received: ");
      Serial.println(cmd);
      
      if (cmd == "OPEN") {
        digitalWrite(PIN_RELAY, HIGH);
        delay(500);
        digitalWrite(PIN_RELAY, LOW);
        playSound("door_open");
      }
      else if (cmd == "KEY_ACCEPTED") {
        playSound("door_open");
      }
      else if (cmd == "KEY_DENIED") {
        playSound("key_denied");
      }
      else if (cmd == "OPENIPC_READY") {
        playSound("door_open");
      }
      else if (cmd.startsWith("PLAY:")) {
        String sound = cmd.substring(5);
        if (sound == "ring") playTone(800, 500);
        else if (sound == "beep") playTone(1000, 100);
      }
    }
  }
  
  //--------------------------------------------------------------------------
  // Send periodic status
  //--------------------------------------------------------------------------
  if (now - lastStatusTime > STATUS_INTERVAL) {
    char status[50];
    snprintf(status, sizeof(status), "STATUS:%s,%s",
             doorState ? "CLOSED" : "OPEN",
             rfidReading ? "READING" : "IDLE");
    sendToCamera(status);
    lastStatusTime = now;
  }
  
  delay(10);
}
</details>
3.3 Install in Arduino IDE
Install ESP32 board support in Arduino IDE

Select board: "LilyGo T-Call" or "ESP32 Dev Module"

Copy the firmware code above

Adjust pins for your specific board

Upload to ESP32

3.4 Verify connection
bash
# On camera, check logs
tail -f /var/log/door_monitor.log
# Should see: ESP reported ready
Step 4: Web Interface Installation
4.1 Create directory structure
bash
mkdir -p /var/www/cgi-bin/p
mkdir -p /var/www/a
4.2 Download web files
bash
# Download from GitHub
wget -O /tmp/intercom.tar.gz https://github.com/OpenIPC/intercom/archive/main.tar.gz
tar -xzf /tmp/intercom.tar.gz -C /tmp

# Copy all files
cp -r /tmp/intercom-main/cgi-bin/* /var/www/cgi-bin/

# Set permissions
chmod +x /var/www/cgi-bin/p/*.cgi
chmod +x /var/www/cgi-bin/backup.cgi 2>/dev/null
4.3 Install Bootstrap (if missing)
bash
# Create assets directory
mkdir -p /var/www/a

# Download Bootstrap
wget -O /var/www/a/bootstrap.min.css https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
wget -O /var/www/a/bootstrap.bundle.min.js https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js
4.4 Add menu entry
Edit /var/www/cgi-bin/p/header.cgi and add these lines to the Extensions dropdown:

html
<!-- DOORPHONE MENU ITEMS -->
<li><a class="dropdown-item" href="/cgi-bin/p/door_keys.cgi">🔑 Door Phone</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/sip_manager.cgi">📞 SIP</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/qr_generator.cgi">🎯 QR Keys</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/temp_keys.cgi">⏱️ Temp Keys</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/sounds.cgi">🔊 Sounds</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/door_history.cgi">📋 History</a></li>
<li><a class="dropdown-item" href="/cgi-bin/backup.cgi">💾 Backups</a></li>
4.5 Install door monitor script
bash
# Download door monitor
wget -O /usr/bin/door_monitor.sh https://raw.githubusercontent.com/OpenIPC/intercom/main/scripts/door_monitor.sh
chmod +x /usr/bin/door_monitor.sh

# Add to autostart
cat > /etc/init.d/S99door << 'EOF'
#!/bin/sh
START=99
NAME=door_monitor
DAEMON=/usr/bin/door_monitor.sh
PIDFILE=/var/run/$NAME.pid

start() {
    printf "Starting $NAME: "
    start-stop-daemon -S -b -m -p $PIDFILE -x $DAEMON -- start
    echo "OK"
}

stop() {
    printf "Stopping $NAME: "
    start-stop-daemon -K -p $PIDFILE
    rm -f $PIDFILE
    echo "OK"
}

case "$1" in
    start|stop) $1 ;;
    restart) stop; start ;;
    *) echo "Usage: $0 {start|stop|restart}"; exit 1 ;;
esac
exit 0
EOF

chmod +x /etc/init.d/S99door
/etc/init.d/S99door start
4.6 Web Interface Screenshots
Key Management	SIP Settings
https://screenshots/keys.png	https://screenshots/sip.png
QR Generator	Temporary Keys
https://screenshots/qr.png	https://screenshots/temp.png
Sound Effects	Backup Manager
https://screenshots/sounds.png	https://screenshots/backup.png
Door Status	Event History
https://screenshots/status.png	https://screenshots/history.png
Step 5: SIP Configuration
5.1 Configure SIP account
Open http://192.168.1.4/cgi-bin/p/sip_manager.cgi and enter:

Field	Example	Description
Username	101	Your SIP extension number
Server	192.168.1.107	SIP server IP or domain
Password	your_password	SIP account password
Transport	UDP	Usually UDP (try TCP if issues)
5.2 Set call button number
In the same interface, set the number for the call button (default: 100).

5.3 Test SIP manually
bash
# Test call
echo "/dial 100" | nc 127.0.0.1 3000

# Hang up
echo "/hangup" | nc 127.0.0.1 3000
5.4 Configure autostart
bash
cat > /etc/init.d/S97baresip << 'EOF'
#!/bin/sh
DAEMON="baresip"
PIDFILE="/var/run/$DAEMON.pid"
LOGFILE="/var/log/baresip.log"
DAEMON_ARGS="-f /etc/baresip -d"

start() {
    echo -n "Starting $DAEMON: "
    touch "$LOGFILE"
    chmod 666 "$LOGFILE"
    > "$LOGFILE"
    start-stop-daemon -b -m -S -q -p "$PIDFILE" -x "$DAEMON" -- $DAEMON_ARGS >> "$LOGFILE" 2>&1
    echo "OK"
}

stop() {
    echo -n "Stopping $DAEMON: "
    start-stop-daemon -K -q -p "$PIDFILE"
    rm -f "$PIDFILE"
    echo "OK"
}

case "$1" in
    start|stop) $1 ;;
    restart) stop; sleep 1; start ;;
    *) echo "Usage: $0 {start|stop|restart}"; exit 1 ;;
esac
exit 0
EOF

chmod +x /etc/init.d/S97baresip
/etc/init.d/S97baresip start
Step 6: Advanced Features
6.1 QR Code Keys
Generate QR codes that can be scanned by the camera's main sensor or external reader.

Features:

Generate printable QR codes

Scan via camera (requires motion detection)

Assign to users with expiration dates

Bulk generation for visitors

How to use:

Open http://192.168.1.4/cgi-bin/p/qr_generator.cgi

Enter key number and owner name

Click "Generate QR" to create QR code

Print or save the QR image

Click "Save Key" to add to database

QR Code Format:

text
QR:12345678|User Name|2026-12-31
6.2 Temporary Keys
Create time-limited access codes for guests, service personnel, or deliveries.

Features:

Set expiration time (hours/days)

Auto-delete after expiry

Email/SMS notification (optional)

Usage tracking

How to use:

Open http://192.168.1.4/cgi-bin/p/temp_keys.cgi

Enter key number and owner name

Set validity period (hours)

Click "Create Temporary Key"

Key automatically expires after set time

Expiry check script (runs every hour via cron):

bash
cat > /usr/bin/check_temp_keys.sh << 'EOF'
#!/bin/sh
KEYS_FILE="/etc/door_keys.conf"
TEMP_FILE="/tmp/keys.tmp"
NOW=$(date +%s)

while IFS='|' read key owner expiry; do
    if [ -n "$expiry" ] && [ "$expiry" -lt "$NOW" ] 2>/dev/null; then
        echo "Removing expired key: $key ($owner)"
        grep -v "^$key|" "$KEYS_FILE" > "$TEMP_FILE"
        mv "$TEMP_FILE" "$KEYS_FILE"
    fi
done < "$KEYS_FILE"
EOF

chmod +x /usr/bin/check_temp_keys.sh
echo "0 * * * * /usr/bin/check_temp_keys.sh" >> /etc/crontabs/root
6.3 Sound Effects
Play sounds through connected speaker for door events.

Available sounds:

Sound File	Event	Description
ring.pcm	Doorbell pressed	Ringtone when call button pressed
door_open.pcm	Door opened	Success sound when door opens
door_close.pcm	Door closed	Door closed notification
denied.pcm	Access denied	Error sound for invalid key
beep.pcm	Button press	Short beep for button feedback
Sound format requirements:

PCM format (raw audio)

8kHz, 16-bit, mono

No headers, just raw data

Convert MP3 to PCM:

bash


# Convert MP3 to PCM
sox input.mp3 -r 8000 -c 1 -b 16 output.pcm
Upload sounds:

bash
# Copy PCM files to camera
scp *.pcm root@192.168.1.4:/usr/share/sounds/doorphone/

# Test sound
echo "/play ring.pcm" | nc 127.0.0.1 3000
6.4 Backup System
Complete backup and restore system for all configurations.

Features:

✅ Create backups with component selection

✅ Upload backups via drag & drop

✅ Download backups with proper filename

✅ Restore backups with verification

✅ Delete old backups (keeps last 10)

Components that can be backed up:

Component	Path	Description
CGI scripts	/var/www/cgi-bin/p/*.cgi	All web interface files
SIP config	/etc/baresip/	SIP accounts and settings
Keys database	/etc/door_keys.conf	All RFID and QR keys
Monitor scripts	/usr/bin/door_monitor.sh	Main door script
Init scripts	/etc/init.d/S99door	Autostart configuration
Majestic config	/etc/majestic.yaml	Camera settings
UART settings	/etc/rc.local	Serial port configuration
Storage locations:

Location	Path	Availability
Internal	/root/backups/	Always available
SD Card	/mnt/mmcblk0p1/backups/	If SD card inserted
USB Drive	/mnt/sdX/backups/	If USB drive connected
Setup backup server:

bash
# Start HTTP server on port 8080 (required for uploads)
httpd -p 8080 -h /var/www &

# Add to autostart
sed -i '/exit 0/i httpd -p 8080 -h /var/www \&' /etc/rc.local
Access backup manager:

Method	URL
Direct	http://192.168.1.4:8080/cgi-bin/p/backup_manager.cgi
Via menu	Extensions → 💾 Backups
Backup file naming:

Created: doorphone_backup_YYYYMMDD_HHMMSS.tar.gz

Uploaded: uploaded_backup_YYYYMMDD_HHMMSS.tar (auto-converted)

Manual backup commands:

bash
# Create backup manually
tar -czf /root/backups/manual_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  /var/www/cgi-bin/p/ \
  /etc/baresip/ \
  /etc/door_keys.conf \
  /usr/bin/door_monitor.sh \
  /etc/init.d/S99door \
  /etc/majestic.yaml \
  /etc/rc.local

# List backups
ls -la /mnt/mmcblk0p1/backups/

# Restore from backup
cd /tmp
tar -xzf /mnt/mmcblk0p1/backups/doorphone_backup_20260306_123456.tar.gz
cp -rf doorphone_backup_*/* /
Step 7: Testing
7.1 Check all components
Component	Test Command	Expected Result
ESP32	tail -f /var/log/door_monitor.log	STATUS messages every 5s
SIP	ps aux | grep baresip	Process running
HTTP (80)	curl -I http://localhost	200 OK
HTTP (8080)	curl -I http://localhost:8080	200 OK
Keys DB	cat /etc/door_keys.conf	List of keys
Backups	ls -la /mnt/mmcblk0p1/backups/	List backup files
7.2 Functional tests
Test	Action	Expected Result
Call button	Press physical button	Call to configured number
Exit button	Press physical button	Relay clicks, door opens
RFID key	Present valid key	Relay clicks, door opens
RFID key	Present invalid key	Error sound, door stays closed
QR code	Scan QR with camera	Key added, door opens
Door sensor	Open/close door	Status changes in web UI
Web login	Open browser	All pages load
Create backup	Click "Create backup"	File appears in list
Upload backup	Drag & drop file	Progress bar, success message
Download backup	Click download	File saves locally
Restore backup	Click restore	Files restored, confirm reboot
7.3 Useful commands
bash
# Check all services
ps aux | grep -E "door_monitor|baresip|httpd|majestic"

# View logs
tail -f /var/log/door_monitor.log
tail -f /var/log/baresip.log
tail -f /tmp/upload_debug.log

# Manual key management
/usr/bin/door_monitor.sh add 12345678 "John Doe"
/usr/bin/door_monitor.sh list
/usr/bin/door_monitor.sh remove 12345678
/usr/bin/door_monitor.sh call_number 101

# Test relay
echo "OPEN" > /dev/ttyS0

# Test sound
echo "/play ring.pcm" | nc 127.0.0.1 3000

# Check disk space
df -h
du -sh /mnt/mmcblk0p1/backups/
Troubleshooting
Common Issues and Solutions
Problem	Possible Cause	Solution
No communication with ESP	Wrong wiring	Check TX→RX, RX→TX, common GND
Wrong baud rate	Set both to 115200
UART not enabled	chmod 666 /dev/ttyS0
SIP not registering	Wrong credentials	Verify username/password
Firewall blocking	Open UDP port 5060
Server unreachable	Ping SIP server
Web interface 500 error	File permissions	chmod +x /var/www/cgi-bin/p/*.cgi
Syntax error	sh -n /path/to/file.cgi
Missing dependencies	Install required packages
False key readings	No pull-up resistors	Add 10kΩ pull-ups to D0/D1
Electrical noise	Shield wires, add capacitors
Reader incompatible	Try different RFID reader
Backup upload fails	HTTP server not running	httpd -p 8080 -h /var/www &
Port 8080 blocked	Check firewall
File too large	Max 100MB
Connection refused on 8080	HTTPD not started	Run start command
Already in use	killall httpd; httpd -p 8080 -h /var/www &
Not in autostart	Add to /etc/rc.local
Uploaded file shows 0 bytes	Multipart parsing error	Check /tmp/upload_debug.log
No disk space	df -h to check
Wrong storage path	Verify selected device
QR code not scanning	Camera focus	Adjust lens
Resolution too low	Enable high-res stream
Wrong format	Use format QR:KEY|NAME|DATE
Temporary keys not expiring	Cron not running	crond start
Wrong expiry format	Use Unix timestamp
Script permissions	chmod +x /usr/bin/check_temp_keys.sh
No sound	Speaker not connected	Check wiring
Sound files missing	Copy PCM files
Wrong format	Convert to 8kHz PCM
Debug Mode
Enable debug logging for troubleshooting:

bash
# Enable debug in door_monitor.sh
sed -i 's/DEBUG=0/DEBUG=1/' /usr/bin/door_monitor.sh
/etc/init.d/S99door restart

# Watch all logs
tail -f /var/log/door_monitor.log /var/log/baresip.log /tmp/upload_debug.log
Reset to defaults
bash
# Reset keys database
rm /etc/door_keys.conf
touch /etc/door_keys.conf
chmod 666 /etc/door_keys.conf

# Reset SIP config
rm -rf /etc/baresip
mkdir -p /etc/baresip

# Reset web files
rm -rf /var/www/cgi-bin/p/*
# Reinstall from GitHub

# Reboot
reboot
File Structure
text
/
├── usr/
│   └── bin/
│       ├── door_monitor.sh          # Main door monitor script
│       ├── dtmf_9.sh                # DTMF handler for door opening
│       ├── start_baresip.sh         # SIP starter script
│       └── check_temp_keys.sh       # Temporary keys expiry checker
│
├── etc/
│   ├── baresip/
│   │   ├── accounts                 # SIP account configuration
│   │   ├── config                   # SIP general configuration
│   │   └── call_number              # Call button target number
│   ├── door_keys.conf               # ⭐ KEYS DATABASE (RFID, QR, temp)
│   ├── rc.local                     # Autostart commands
│   ├── init.d/
│   │   ├── S97baresip               # SIP autostart
│   │   └── S99door                   # Door monitor autostart
│   └── crontabs/
│       └── root                      # Cron jobs (temp keys cleanup)
│
├── var/
│   └── www/
│       ├── a/                        # Assets (Bootstrap, CSS, JS)
│       │   ├── bootstrap.min.css
│       │   └── bootstrap.bundle.min.js
│       └── cgi-bin/
│           ├── backup.cgi            # Redirect to port 8080
│           └── p/
│               ├── backup_manager.cgi # Backup management UI
│               ├── backup_api.cgi     # Backup API backend
│               ├── upload_final.cgi   # File upload handler
│               ├── door_api.cgi       # Key management API
│               ├── door_keys.cgi      # Key management UI
│               ├── door_history.cgi   # Event history UI
│               ├── sip_api.cgi        # SIP API backend
│               ├── sip_manager.cgi    # SIP configuration UI
│               ├── qr_api.cgi         # QR code API
│               ├── qr_generator.cgi   # QR code generator UI
│               ├── sounds.cgi         # Sound effects UI
│               ├── play_sound.cgi     # Sound player
│               ├── temp_keys.cgi      # Temporary keys UI
│               └── header.cgi         # Menu configuration
│
└── var/
    └── log/
        ├── door_monitor.log          # Door events log
        ├── baresip.log               # SIP events log
        └── upload_debug.log          # Upload debug log

/mnt/
├── mmcblk0p1/
│   └── backups/                      # SD card backups
└── sdX/
    └── backups/                      # USB drive backups

/root/
└── backups/                          # Internal memory backups

/usr/share/
└── sounds/
    └── doorphone/                    # Sound effects
        ├── ring.pcm
        ├── door_open.pcm
        ├── door_close.pcm
        ├── denied.pcm
        └── beep.pcm
Updates & Changelog
Version 2.0 (March 2026)
🚀 New Features
Feature	Description	Added in
QR Code Keys	Generate and scan QR codes for access	v2.0
Temporary Keys	Time-limited access codes	v2.0
Sound Effects	Audio feedback for door events	v2.0
Backup System	Full configuration backup/restore	v2.0
Drag & Drop Upload	Easy file uploads with progress bar	v2.0
HTTP Server on 8080	Separate port for uploads	v2.0
Multipart Parsing	Automatic extraction of uploaded files	v2.0
🔧 Improvements
Better error handling in all CGI scripts

Progress bar for file uploads

Automatic cleanup of old backups (keeps last 10)

Debug logging for troubleshooting

Improved UART configuration

Support for multiple storage devices (SD, USB, internal)

🐛 Bug Fixes
Fixed POST data handling in CGI scripts

Fixed multipart/form-data parsing

Fixed file permissions issues

Fixed autostart configuration

Fixed CORS issues with separate port

Updating from v1.x
If you have an existing installation, update with:

bash
# 1. Backup current configuration
cp /etc/door_keys.conf /root/door_keys.conf.bak
cp -r /etc/baresip /root/baresip.bak

# 2. Download new files
wget -O /tmp/intercom.tar.gz https://github.com/OpenIPC/intercom/archive/main.tar.gz
tar -xzf /tmp/intercom.tar.gz -C /tmp

# 3. Update web files
cp -r /tmp/intercom-main/cgi-bin/* /var/www/cgi-bin/
chmod +x /var/www/cgi-bin/p/*.cgi

# 4. Add new scripts
cp /tmp/intercom-main/scripts/check_temp_keys.sh /usr/bin/
chmod +x /usr/bin/check_temp_keys.sh

# 5. Set up cron for temp keys
echo "0 * * * * /usr/bin/check_temp_keys.sh" >> /etc/crontabs/root

# 6. Start HTTP server for backups
httpd -p 8080 -h /var/www &
echo 'httpd -p 8080 -h /var/www &' >> /etc/rc.local

# 7. Update header.cgi (add Backup menu item)
# Edit /var/www/cgi-bin/p/header.cgi manually

# 8. Restart services
/etc/init.d/S99door restart
/etc/init.d/S97baresip restart
License
MIT License - feel free to use and modify!

Copyright (c) 2026 OpenIPC Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Contributors
OpenIPC Team - Initial work and SIP integration

Community Contributors - Features, bug fixes, translations

Want to contribute? Feel free to:

Submit pull requests

Report bugs

Suggest features

Improve documentation

Translate to other languages

⭐ Star this repo if you find it useful!

Happy building! 🚀
