# SIP Doorphone on OpenIPC
## English

### Complete Guide to Building a SIP Doorphone with OpenIPC

This project turns an IP camera with OpenIPC firmware into a full-featured SIP doorphone with RFID key access, web interface, and remote door control.

### 📋 Table of Contents
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Step 1: Flash OpenIPC with VoIP Support](#step-1-flash-openipc-with-voip-support)
- [Step 2: Initial Camera Setup](#step-2-initial-camera-setup)
- [Step 3: ESP32/ESP8266 Controller](#step-3-esp32esp8266-controller)
- [Step 4: Web Interface Installation](#step-4-web-interface-installation)
- [Step 5: SIP Configuration](#step-5-sip-configuration)
- [Step 6: Testing](#step-6-testing)
- [Troubleshooting](#troubleshooting)
- [File Structure](#file-structure)

### Hardware Requirements

| Component | Recommended | Notes |
|-----------|------------|-------|
| IP Camera | Uniview C1L-2WN-G with SSC335DE | "People's camera for $5" |
| Microcontroller | ESP32 (LilyGo T-Call) or ESP8266 (Wemos D1 mini) | For door control |
| RFID Reader | Wiegand 26/34 (3.3V or 5V) | Any standard reader |
| Relay Module | 1-channel 5V relay | For door lock control |
| Reed Switch | NC magnetic contact | Door position sensor |
| Buttons | 2x momentary buttons | Exit and call buttons |
| Power Supply | 12V for lock, 5V for ESP | External power |

### Software Requirements

- OpenIPC firmware with VoIP support (`ssc335de_ultimate_uniview-c1l-2wn-g-voip-nor.tgz`)
- Arduino IDE for ESP32/ESP8266
- Python 3 (for initial setup)
- Web browser for configuration

---

### Step 1: Flash OpenIPC with VoIP Support

#### 1.1 Download the firmware
```bash
# Download the base firmware
wget https://github.com/OpenIPC/firmware/releases/download/image/openipc-ssc335de-nor-ultimate.bin

# Download the VoIP update
wget https://github.com/OpenIPC/builder/releases/download/latest/ssc335de_ultimate_uniview-c1l-2wn-g-voip-nor.tgz

1.2 Flash using programmer
Use a SPI programmer (CH341A, etc.) to flash openipc-ssc335de-nor-ultimate.bin to the camera's NOR flash.

1.3 First boot and network connection
Connect camera via Ethernet (DHCP required). Find its IP address from router DHCP leases.

1.4 Update to VoIP firmware

# SSH into camera (default password: 123456)
ssh root@192.168.1.x

# Update firmware (DO NOT use web interface!)
sysupgrade -k -r -f -n -z --url=https://github.com/OpenIPC/builder/releases/download/latest/ssc335de_ultimate_uniview-c1l-2wn-g-voip-nor.tgz


1.5 Configure WiFi (if needed)

bash
fw_setenv wlanssid "YourWiFiSSID"
fw_setenv wlanpass "YourWiFiPassword"
reboot



Step 2: Initial Camera Setup
2.1 Connect via SSH

bash
ssh root@192.168.1.4  # Use your camera's IP

2.2 Configure UART

bash
# Set permissions for UART
chmod 666 /dev/ttyS0
echo 'chmod 666 /dev/ttyS0' >> /etc/rc.local




2.3 Check UART ports

bash
ls -la /dev/tty*
# Should show ttyS0, ttyS1, ttyS2


Step 3: ESP32/ESP8266 Controller
3.1 Wiring Diagram

text
ESP32 (LilyGo T-Call)    Connected Devices
---------------------    -----------------
GPIO4  ----------------> RFID Reader DATA0
GPIO5  ----------------> RFID Reader DATA1
3.3V/5V ---------------> RFID Reader VCC
GND    ----------------> RFID Reader GND

GPIO32 ----------------> Exit Button (other pin to GND)
GPIO33 ----------------> Call Button (other pin to GND)

GPIO14 ----------------> Relay Module IN
5V    ----------------> Relay Module VCC
GND   ----------------> Relay Module GND

GPIO12 ----------------> Reed Switch (other pin to GND)

GPIO13 (RX2) -----------> Camera TX (GPIO13)
GPIO15 (TX2) -----------> Camera RX (GPIO15)
GND   -------------------> Camera GND

External 12V -----------> Lock (via relay contacts)


3.2 ESP32 Firmware
Download the complete firmware from the /firmware folder or copy the code below:

cpp
// Full ESP32 firmware is available in /firmware/esp32_sip_doorphone.ino

3.3 Install in Arduino IDE
Install ESP32 board support in Arduino IDE

Select board: "LilyGo T-Call" or "ESP32 Dev Module"

Copy the firmware code

Set correct GPIO pins for your board

Upload to ESP32

3.4 Verify connection
On the camera, check logs:


bash
tail -f /var/log/door_monitor.log

You should see: ESP reported ready

Step 4: Web Interface Installation
4.1 Create directory structure

bash
mkdir -p /var/www/cgi-bin/p
mkdir -p /var/www/a

4.2 Install web files
Copy all files from the /www folder to /var/www/ on the camera.

Main files:

cgi-bin/p/door_api.cgi - API for key management

cgi-bin/p/door_keys.cgi - Key management interface

cgi-bin/p/door_history.cgi - Event history

cgi-bin/p/sip_api.cgi - SIP API

cgi-bin/p/sip_manager.cgi - SIP settings interface

cgi-bin/p/sip_save.cgi - SIP settings saver

4.3 Set permissions
bash
chmod +x /var/www/cgi-bin/p/*.cgi
4.4 Add menu entry
Edit /var/www/cgi-bin/p/header.cgi and add:

html
<li><a class="dropdown-item" href="/cgi-bin/p/door_keys.cgi">🔑 Door Phone</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/sip_manager.cgi">📞 SIP</a></li>
4.5 Web Interface Screenshots
Key Management	SIP Settings
https:///screenshots/1.png?raw=true	https:///screenshots/2.png?raw=true
Manage RFID keys, view history, open door	Configure SIP account and call number
Door Status	Event History
https:///screenshots/3.png?raw=true	https:///screenshots/4.png?raw=true
Real-time door status with LED indicators	*View last 50 events with auto-refresh*
Step 5: SIP Configuration
5.1 Configure SIP account
Via web interface:

Open http://192.168.1.4/cgi-bin/p/sip_manager.cgi

Enter your SIP credentials:

Username (e.g., 101)

Server (e.g., 192.168.1.107)

Password

Transport (UDP usually)

5.2 Set call button number
In the same interface, set the number for the call button (default 100).

5.3 Test SIP
bash
# Test call manually
echo "/dial 100" | nc 127.0.0.1 3000
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
ln -sf /etc/init.d/S97baresip /etc/rc.d/S97baresip
Step 6: Testing
6.1 Check all components
Component	Test	Expected Result
ESP32 connection	tail -f /var/log/door_monitor.log	STATUS messages every 5s
Call button	Press button	Call to configured number
Exit button	Press button	Door opens
RFID key	Present key	Door opens if allowed
Door sensor	Open/close door	Status changes in web
Web interface	Open browser	All functions work
6.2 Useful commands
bash
# Check door monitor
ps aux | grep door_monitor

# Check SIP
ps aux | grep baresip

# View logs
tail -f /var/log/door_monitor.log
tail -f /var/log/baresip.log

# Add key manually
/usr/bin/door_monitor.sh add 12345678 "User Name"

# List keys
/usr/bin/door_monitor.sh list

# Set call number
/usr/bin/door_monitor.sh call_number 101
Troubleshooting
Problem	Solution
No communication with ESP	Check UART connections (TX->RX, RX->TX), verify common GND, check baud rate (115200)
SIP not registering	Check SIP server availability, verify credentials, check firewall (port 5060 UDP)
Web interface 500 error	Check file permissions (chmod +x *.cgi), check syntax: sh -n /path/to/file.cgi
False key readings	Add pull-up resistors to Wiegand lines, adjust MIN_KEY_LENGTH in door_monitor.sh
File Structure
text
/usr/bin/
├── door_monitor.sh          # Main door monitor script
├── dtmf_9.sh                # DTMF handler for door opening
└── start_baresip.sh         # SIP starter script

/etc/
├── baresip/
│   ├── accounts             # SIP account
│   ├── config               # SIP configuration
│   └── call_number          # Call button number
├── door_keys.conf           # Allowed keys database
└── rc.local                 # Autostart commands

/var/www/cgi-bin/p/
├── door_api.cgi             # Key management API
├── door_keys.cgi            # Key management UI
├── door_history.cgi         # Event history
├── sip_api.cgi              # SIP API
├── sip_manager.cgi          # SIP management UI
└── sip_save.cgi             # SIP settings saver

/var/log/
├── door_monitor.log         # Door events
└── baresip.log              # SIP events

## License
MIT License - feel free to use and modify!

Contributors
Based on OpenIPC project




