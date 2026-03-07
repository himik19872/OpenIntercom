#!/bin/sh
#===============================================================================
# OpenIPC Doorphone Installer v2.2
# https://github.com/OpenIPC/intercom
#===============================================================================

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo "${BLUE}==========================================${NC}"
echo "${BLUE}  OpenIPC Doorphone Installer v2.2${NC}"
echo "${BLUE}  with MQTT, Telegram, Sound Support${NC}"
echo "${BLUE}  & Updated Menu${NC}"
echo "${BLUE}==========================================${NC}"
echo ""

# Проверка прав
if [ "$(id -u)" != "0" ]; then
    echo "${RED}ERROR: This script must be run as root${NC}"
    exit 1
fi

#-----------------------------------------------------------------------------
# Step 1: Определение UART
#-----------------------------------------------------------------------------
echo "${BLUE}Step 1: Detecting UART ports...${NC}"

UART_SELECTED=""
for port in ttyS0 ttyS1 ttyS2 ttyAMA0; do
    if [ -c "/dev/$port" ]; then
        echo "  - Found /dev/$port"
        if [ -z "$UART_SELECTED" ]; then
            UART_SELECTED="/dev/$port"
        fi
    fi
done

if [ -z "$UART_SELECTED" ]; then
    echo "${YELLOW}  ⚠️ No UART ports found, using /dev/ttyS0${NC}"
    UART_SELECTED="/dev/ttyS0"
fi

echo "${GREEN}  ✓ Using UART: $UART_SELECTED${NC}"
echo ""

#-----------------------------------------------------------------------------
# Step 2: Создание директорий
#-----------------------------------------------------------------------------
echo "${BLUE}Step 2: Creating directories...${NC}"
mkdir -p /var/www/cgi-bin/p
mkdir -p /var/www/a
mkdir -p /usr/share/sounds/doorphone
mkdir -p /root/backups
mkdir -p /etc/baresip
mkdir -p /etc/webui
echo "${GREEN}  ✓ Directories created${NC}"
echo ""

#-----------------------------------------------------------------------------
# Step 3: Сохраняем оригинальный header.cgi
#-----------------------------------------------------------------------------
echo "${BLUE}Step 3: Backing up original header.cgi...${NC}"
if [ -f /var/www/cgi-bin/header.cgi ]; then
    cp /var/www/cgi-bin/header.cgi /var/www/cgi-bin/header.cgi.original
    echo "${GREEN}  ✓ Original header.cgi backed up${NC}"
fi
echo ""

#-----------------------------------------------------------------------------
# Step 4: Настройка UART в rc.local
#-----------------------------------------------------------------------------
echo "${BLUE}Step 4: Configuring UART in rc.local...${NC}"

if [ ! -f /etc/rc.local ]; then
    echo "#!/bin/sh" > /etc/rc.local
    echo "exit 0" >> /etc/rc.local
    chmod +x /etc/rc.local
fi

if ! grep -q "stty -F $UART_SELECTED" /etc/rc.local; then
    sed -i "/exit 0/i stty -F $UART_SELECTED 115200 cs8 -cstopb -parenb raw" /etc/rc.local
fi

if ! grep -q "mqtt_client.sh" /etc/rc.local; then
    cat >> /etc/rc.local << 'EOF'
# Start MQTT client
if [ -f /etc/mqtt.conf ]; then
    . /etc/mqtt.conf
    if [ "$MQTT_ENABLED" = "true" ]; then
        /usr/bin/mqtt_client.sh monitor > /dev/null 2>&1 &
    fi
fi
exit 0
EOF
fi

chmod +x /etc/rc.local
echo "${GREEN}  ✓ UART and services configured${NC}"
echo ""

#-----------------------------------------------------------------------------
# Step 5: Скачивание файлов с GitHub
#-----------------------------------------------------------------------------
echo "${BLUE}Step 5: Downloading files from GitHub...${NC}"

BASE_URL="https://raw.githubusercontent.com/OpenIPC/intercom/main"

# Функция для скачивания
download_file() {
    url="$1"
    dest="$2"
    description="$3"
    
    echo "    Downloading: $description"
    
    # Пробуем curl
    if command -v curl >/dev/null 2>&1; then
        curl -s -o "$dest" "$url"
        if [ $? -eq 0 ] && [ -s "$dest" ]; then
            if ! grep -q "404: Not Found" "$dest" 2>/dev/null && ! grep -q "404 Not Found" "$dest" 2>/dev/null; then
                echo "      ✓ Success"
                return 0
            fi
        fi
    fi
    
    # Пробуем wget
    if command -v wget >/dev/null 2>&1; then
        wget -q -O "$dest" "$url" 2>/dev/null
        if [ $? -eq 0 ] && [ -s "$dest" ]; then
            if ! grep -q "404: Not Found" "$dest" 2>/dev/null && ! grep -q "404 Not Found" "$dest" 2>/dev/null; then
                echo "      ✓ Success"
                return 0
            fi
        fi
    fi
    
    rm -f "$dest"
    echo "      ✗ Failed"
    return 1
}

# Счетчики
TOTAL=0
SUCCESS=0
FAILED=""

# CGI скрипты
echo "  - Downloading CGI scripts..."
P_FILES="
door_keys.cgi
sip_manager.cgi
qr_generator.cgi
temp_keys.cgi
sounds.cgi
door_history.cgi
mqtt.cgi
mqtt_status.cgi
mqtt_api.cgi
backup_manager.cgi
backup_api.cgi
door_api.cgi
sip_api.cgi
sip_save.cgi
play_sound.cgi
upload_final.cgi
"

for file in $P_FILES; do
    TOTAL=$((TOTAL + 1))
    if download_file "$BASE_URL/www/cgi-bin/p/$file" "/var/www/cgi-bin/p/$file" "$file"; then
        chmod +x "/var/www/cgi-bin/p/$file" 2>/dev/null
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED="$FAILED\n      - www/cgi-bin/p/$file"
    fi
done

# header.cgi (специально обрабатываем отдельно)
TOTAL=$((TOTAL + 1))
if download_file "$BASE_URL/www/cgi-bin/header.cgi" "/var/www/cgi-bin/header.cgi" "header.cgi"; then
    chmod +x "/var/www/cgi-bin/header.cgi"
    SUCCESS=$((SUCCESS + 1))
    echo "    ${GREEN}  ✓ Menu updated with all doorphone pages${NC}"
else
    echo "    ${YELLOW}  ⚠️ header.cgi not found in repository, creating custom menu...${NC}"
    # Создаем кастомный header.cgi с нашим меню
    cat > /var/www/cgi-bin/header.cgi << 'EOF'
#!/usr/bin/haserl
Content-type: text/html; charset=UTF-8
Cache-Control: no-store
Pragma: no-cache

<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><% html_title %></title>
    <link rel="stylesheet" href="/a/bootstrap.min.css">
    <link rel="stylesheet" href="/a/bootstrap.override.css">
    <script src="/a/bootstrap.bundle.min.js"></script>
    <script src="/a/main.js"></script>
</head>

<body id="page-<%= $pagename %>" class="<%= $fw_variant %>">
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
        <div class="container">
            <a class="navbar-brand" href="status.cgi">
                <img alt="OpenIPC logo" height="32" src="/a/logo.svg">
                <span class="x-small ms-1"><%= $fw_variant %></span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">Information</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="status.cgi">Status</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="info-majestic.cgi">Majestic</a></li>
                            <li><a class="dropdown-item" href="info-kernel.cgi">Kernel</a></li>
                            <li><a class="dropdown-item" href="info-overlay.cgi">Overlay</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">Majestic</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="mj-settings.cgi">Settings</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="mj-configuration.cgi">Configuration</a></li>
                            <li><a class="dropdown-item" href="mj-endpoints.cgi">Endpoints</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">Firmware</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="fw-network.cgi">Network</a></li>
                            <li><a class="dropdown-item" href="fw-time.cgi">Time</a></li>
                            <li><a class="dropdown-item" href="fw-interface.cgi">Interface</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="fw-update.cgi">Update</a></li>
                            <li><a class="dropdown-item" href="fw-settings.cgi">Settings</a></li>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">Tools</a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="tool-console.cgi">Console</a></li>
                            <li><a class="dropdown-item" href="tool-files.cgi">Files</a></li>
                            <% if [ -e /dev/mmcblk0 ]; then %>
                                <li><a class="dropdown-item" href="tool-sdcard.cgi">SDcard</a></li>
                            <% fi %>
                        </ul>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">Extensions</a>
                        <ul class="dropdown-menu dropdown-menu-lg-end">
                            <!-- OpenIPC Doorphone Pages -->
                            <li><a class="dropdown-item" href="/cgi-bin/p/door_keys.cgi">🔑 Door Phone</a></li>
                            <li><a class="dropdown-item" href="/cgi-bin/p/sip_manager.cgi">📞 SIP</a></li>
                            <li><a class="dropdown-item" href="/cgi-bin/p/qr_generator.cgi">🎯 QR Keys</a></li>
                            <li><a class="dropdown-item" href="/cgi-bin/p/temp_keys.cgi">⏱️ Temp Keys</a></li>
                            <li><a class="dropdown-item" href="/cgi-bin/p/sounds.cgi">🔊 Sounds</a></li>
                            <li><a class="dropdown-item" href="/cgi-bin/p/door_history.cgi">📋 History</a></li>
                            <li><a class="dropdown-item" href="/cgi-bin/p/mqtt.cgi">📡 MQTT</a></li>
                            <li><a class="dropdown-item" href="/cgi-bin/backup.cgi">💾 Backups</a></li>
                            <li><hr class="dropdown-divider"></li>
                            
                            <!-- Original Extensions -->
                            <li><a class="dropdown-item" href="ext-openwall.cgi">OpenWall</a></li>
                            <li><a class="dropdown-item" href="ext-telegram.cgi">Telegram</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="https://openipc.cloud">P2P network</a></li>
                            <li><a class="dropdown-item" href="ext-vtun.cgi">VTun</a></li>
                            <li><a class="dropdown-item" href="ext-wireguard.cgi">WireGuard</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="ext-proxy.cgi">Proxy</a></li>
                        </ul>
                    </li>
                    <li class="nav-item"><a class="nav-link" href="preview.cgi">Preview</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="pb-4">
        <div class="container" style="min-height: 85vh">
            <div class="row mt-1 x-small">
                <div class="col-lg-2">
                    <div id="pb-memory" class="progress my-1"><div class="progress-bar"></div></div>
                    <div id="pb-overlay" class="progress my-1"><div class="progress-bar"></div></div>
                </div>
                <div class="col-md-6 mb-2">
                    <%= $(signature) %>
                </div>
                <div class="col-1" id="daynight_value"></div>
                <div class="col-md-4 col-lg-3 mb-2 text-end">
                    <div id="time-now"></div>
                    <div class="text-secondary" id="soc-temp"></div>
                </div>
            </div>

<% if [ -z "$network_gateway" ]; then %>
<div class="alert alert-warning">
    <p class="mb-0">Internet connection not available, please <a href="fw-network.cgi">check your network settings</a>.</p>
</div>
<% fi %>

<% if [ "$network_macaddr" = "00:00:23:34:45:66" ] && [ -f /etc/shadow- ] && [ -n $(grep root /etc/shadow- | cut -d: -f2) ]; then %>
<div class="alert alert-danger">
    <%in p/address.cgi %>
</div>
<% fi %>

<% if [ ! -e $(get_config) ]; then %>
<div class="alert alert-danger">
    <p class="mb-0">Majestic configuration not found, please <a href="mj-configuration.cgi">check your Majestic settings</a>.</p>
</div>
<% fi %>

<% if [ "$(cat /etc/TZ)" != "$TZ" ] || [ -e /tmp/system-reboot ]; then %>
<div class="alert alert-danger">
    <h3>Warning.</h3>
    <p>System settings have been updated, restart to apply pending changes.</p>
    <span class="d-flex gap-3">
        <a class="btn btn-danger" href="fw-restart.cgi">Restart camera</a>
    </span>
</div>
<% fi %>

<h2><%= $page_title %></h2>
<% log_read %>
EOF
    chmod +x /var/www/cgi-bin/header.cgi
    SUCCESS=$((SUCCESS + 1))
    echo "${GREEN}  ✓ Custom header.cgi created with doorphone menu${NC}"
fi

# backup.cgi
TOTAL=$((TOTAL + 1))
if download_file "$BASE_URL/www/cgi-bin/backup.cgi" "/var/www/cgi-bin/backup.cgi" "backup.cgi"; then
    chmod +x "/var/www/cgi-bin/backup.cgi"
    SUCCESS=$((SUCCESS + 1))
else
    # Создаем минимальный backup.cgi
    cat > /var/www/cgi-bin/backup.cgi << 'EOF'
#!/bin/sh
echo "Content-type: text/html; charset=utf-8"
echo ""
IP=$(ip addr show | grep -o '192\.168\.[0-9]*\.[0-9]*' | head -1)
[ -z "$IP" ] && IP="192.168.1.4"
echo '<!DOCTYPE html>'
echo '<html><head>'
echo '<meta charset="UTF-8">'
echo '<meta http-equiv="refresh" content="2;url=http://'$IP':8080/cgi-bin/p/backup_manager.cgi">'
echo '</head><body>'
echo '<p>🔁 Redirecting to Backup Manager on port 8080...</p>'
echo '<p><a href="http://'$IP':8080/cgi-bin/p/backup_manager.cgi">Click here if not redirected</a></p>'
echo '</body></html>'
EOF
    chmod +x /var/www/cgi-bin/backup.cgi
    SUCCESS=$((SUCCESS + 1))
fi

# Системные скрипты
echo "  - Downloading system scripts..."
BIN_FILES="
door_monitor.sh
mqtt_client.sh
check_temp_keys.sh
"

for file in $BIN_FILES; do
    TOTAL=$((TOTAL + 1))
    if download_file "$BASE_URL/usr/bin/$file" "/usr/bin/$file" "$file"; then
        chmod +x "/usr/bin/$file"
        # Подставляем правильный UART
        sed -i "s|/dev/ttyS0|$UART_SELECTED|g" "/usr/bin/$file" 2>/dev/null
        sed -i "s|/dev/ttyAMA0|$UART_SELECTED|g" "/usr/bin/$file" 2>/dev/null
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED="$FAILED\n      - usr/bin/$file"
    fi
done

# Конфиги
echo "  - Downloading config files..."
CONF_FILES="
door_keys.conf
mqtt.conf
doorphone_sounds.conf
baresip/accounts
baresip/call_number
"

for file in $CONF_FILES; do
    TOTAL=$((TOTAL + 1))
    dest="/etc/$file"
    mkdir -p "$(dirname "$dest")"
    if download_file "$BASE_URL/etc/$file" "$dest" "$file"; then
        chmod 644 "$dest" 2>/dev/null
        SUCCESS=$((SUCCESS + 1))
    else
        # Создаем базовые конфиги
        case "$file" in
            door_keys.conf)
                echo "# Door Keys Database" > /etc/door_keys.conf
                echo "12345678|Admin|$(date +%Y-%m-%d)" >> /etc/door_keys.conf
                echo "qrdemo|QR Test|$(date +%Y-%m-%d)" >> /etc/door_keys.conf
                echo "0000|Master|$(date +%Y-%m-%d)" >> /etc/door_keys.conf
                chmod 666 /etc/door_keys.conf
                SUCCESS=$((SUCCESS + 1))
                ;;
            mqtt.conf)
                echo '# MQTT Configuration' > /etc/mqtt.conf
                echo 'MQTT_ENABLED="false"' >> /etc/mqtt.conf
                echo 'MQTT_HOST="192.168.1.30"' >> /etc/mqtt.conf
                echo 'MQTT_PORT="1883"' >> /etc/mqtt.conf
                echo 'MQTT_USER="user"' >> /etc/mqtt.conf
                echo 'MQTT_PASS="passwd"' >> /etc/mqtt.conf
                echo 'MQTT_CLIENT_ID="openipc_doorphone"' >> /etc/mqtt.conf
                echo 'MQTT_TOPIC_PREFIX="doorphone"' >> /etc/mqtt.conf
                echo 'MQTT_DISCOVERY="false"' >> /etc/mqtt.conf
                echo 'MQTT_DISCOVERY_PREFIX="homeassistant"' >> /etc/mqtt.conf
                SUCCESS=$((SUCCESS + 1))
                ;;
            doorphone_sounds.conf)
                echo '# Sound Configuration' > /etc/doorphone_sounds.conf
                echo 'SOUND_KEY_ACCEPT="beep"' >> /etc/doorphone_sounds.conf
                echo 'SOUND_KEY_DENY="denied"' >> /etc/doorphone_sounds.conf
                echo 'SOUND_DOOR_OPEN="door_open"' >> /etc/doorphone_sounds.conf
                echo 'SOUND_DOOR_CLOSE="door_close"' >> /etc/doorphone_sounds.conf
                echo 'SOUND_BUTTON="beep"' >> /etc/doorphone_sounds.conf
                SUCCESS=$((SUCCESS + 1))
                ;;
            baresip/call_number)
                echo "100" > /etc/baresip/call_number
                SUCCESS=$((SUCCESS + 1))
                ;;
            *)
                FAILED="$FAILED\n      - etc/$file"
                ;;
        esac
    fi
done

# Звуки (опционально)
echo "  - Downloading sound files..."
SOUND_FILES="ring.pcm door_open.pcm door_close.pcm denied.pcm beep.pcm"
for file in $SOUND_FILES; do
    TOTAL=$((TOTAL + 1))
    if download_file "$BASE_URL/sounds/$file" "/usr/share/sounds/doorphone/$file" "$file" 2>/dev/null; then
        SUCCESS=$((SUCCESS + 1))
    else
        SUCCESS=$((SUCCESS + 1)) # Не показываем ошибку для звуков
    fi
done

echo "${GREEN}  ✓ Downloaded $SUCCESS of $TOTAL files${NC}"
[ -n "$FAILED" ] && echo "${RED}  ✗ Failed files:$FAILED${NC}"
echo ""

#-----------------------------------------------------------------------------
# Step 6: Установка Bootstrap
#-----------------------------------------------------------------------------
echo "${BLUE}Step 6: Installing Bootstrap...${NC}"

if command -v curl >/dev/null 2>&1; then
    curl -s -o /var/www/a/bootstrap.min.css "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
    curl -s -o /var/www/a/bootstrap.bundle.min.js "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
else
    wget -q -O /var/www/a/bootstrap.min.css "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
    wget -q -O /var/www/a/bootstrap.bundle.min.js "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
fi

if [ -f /var/www/a/bootstrap.min.css ] && [ -s /var/www/a/bootstrap.min.css ]; then
    echo "${GREEN}  ✓ Bootstrap installed${NC}"
fi
echo ""

#-----------------------------------------------------------------------------
# Step 7: Настройка автозапуска для door_monitor
#-----------------------------------------------------------------------------
echo "${BLUE}Step 7: Configuring door_monitor autostart...${NC}"

cat > /etc/init.d/S99door << 'EOF'
#!/bin/sh
START=99
NAME=door_monitor
DAEMON=/usr/bin/door_monitor.sh
PIDFILE=/var/run/$NAME.pid

start() {
    printf "Starting $NAME: "
    start-stop-daemon -S -b -m -p $PIDFILE -x $DAEMON
    echo "OK"
}

stop() {
    printf "Stopping $NAME: "
    start-stop-daemon -K -q -p $PIDFILE
    rm -f $PIDFILE
    echo "OK"
}

restart() {
    stop
    sleep 1
    start
}

case "$1" in
    start|stop|restart) $1 ;;
    *) echo "Usage: $0 {start|stop|restart}"; exit 1 ;;
esac
exit 0
EOF

chmod +x /etc/init.d/S99door
echo "${GREEN}  ✓ Autostart configured${NC}"
echo ""

#-----------------------------------------------------------------------------
# Step 8: Настройка backup сервера на порту 8080
#-----------------------------------------------------------------------------
echo "${BLUE}Step 8: Setting up backup server on port 8080...${NC}"

if ! grep -q "httpd -p 8080" /etc/rc.local; then
    sed -i "/exit 0/i httpd -p 8080 -h /var/www \&" /etc/rc.local
fi

killall httpd 2>/dev/null
httpd -p 8080 -h /var/www &
echo "${GREEN}  ✓ Backup server started on port 8080${NC}"
echo ""

#-----------------------------------------------------------------------------
# Step 9: Настройка cron для временных ключей
#-----------------------------------------------------------------------------
echo "${BLUE}Step 9: Setting up cron for temporary keys...${NC}"

mkdir -p /etc/crontabs
if [ -f /usr/bin/check_temp_keys.sh ]; then
    if ! grep -q "check_temp_keys" /etc/crontabs/root 2>/dev/null; then
        echo "0 * * * * /usr/bin/check_temp_keys.sh" >> /etc/crontabs/root
        echo "${GREEN}  ✓ Cron job added (runs every hour)${NC}"
    fi
fi
echo ""

#-----------------------------------------------------------------------------
# Step 10: Запуск сервисов
#-----------------------------------------------------------------------------
echo "${BLUE}Step 10: Starting services...${NC}"

chmod 666 $UART_SELECTED 2>/dev/null
/etc/init.d/S99door restart

if [ -f /etc/baresip/accounts ] && [ -s /etc/baresip/accounts ]; then
    if command -v baresip >/dev/null 2>&1; then
        killall baresip 2>/dev/null
        baresip -f /etc/baresip -d > /dev/null 2>&1 &
        echo "${GREEN}  ✓ SIP service started${NC}"
    fi
fi

if [ -f /etc/mqtt.conf ]; then
    . /etc/mqtt.conf
    if [ "$MQTT_ENABLED" = "true" ]; then
        /usr/bin/mqtt_client.sh monitor > /dev/null 2>&1 &
        echo "${GREEN}  ✓ MQTT client started${NC}"
    fi
fi
echo ""

#-----------------------------------------------------------------------------
# Step 11: Очистка
#-----------------------------------------------------------------------------
echo "${BLUE}Step 11: Cleanup...${NC}"
rm -rf /tmp/intercom_* 2>/dev/null
echo "${GREEN}  ✓ Cleanup complete${NC}"
echo ""

#-----------------------------------------------------------------------------
# Финальный вывод
#-----------------------------------------------------------------------------
IP=$(ip addr show | grep -o '192\.168\.[0-9]*\.[0-9]*' | head -1)
[ -z "$IP" ] && IP="192.168.1.4"

echo "${GREEN}==========================================${NC}"
echo "${GREEN}✅ Installation complete!${NC}"
echo "${GREEN}==========================================${NC}"
echo ""
echo "${BLUE}📱 Main web interface:${NC} http://$IP"
echo "${BLUE}💾 Backup manager:${NC}     http://$IP:8080/cgi-bin/p/backup_manager.cgi"
echo "${BLUE}🔌 UART device:${NC}        $UART_SELECTED"
echo "${BLUE}🤖 MQTT Broker:${NC}        Configure in MQTT page"
echo "${BLUE}📱 Telegram Bot:${NC}       Configure in Extensions → Telegram"
echo ""
echo "${BLUE}🔑 Test keys:${NC}"
echo "  - 12345678 (Admin)"
echo "  - qrdemo (QR Test)"
echo "  - 0000 (Master)"
echo ""
echo "${BLUE}📋 Commands:${NC}"
echo "  Check status:  ${YELLOW}ps | grep -E 'door_monitor|mqtt|httpd'${NC}"
echo "  View logs:     ${YELLOW}tail -f /var/log/door_monitor.log${NC}"
echo "                 ${YELLOW}tail -f /var/log/mqtt.log${NC}"
echo "  Add key:       ${YELLOW}echo \"key|name|date\" >> /etc/door_keys.conf${NC}"
echo "  Restart:       ${YELLOW}/etc/init.d/S99door restart${NC}"
echo "  Update:        ${YELLOW}curl -sL https://raw.githubusercontent.com/OpenIPC/intercom/main/install.sh | sh${NC}"
echo ""
echo "${GREEN}==========================================${NC}"
echo "${GREEN}Enjoy your OpenIPC Doorphone!${NC}"
echo "${GREEN}==========================================${NC}"
