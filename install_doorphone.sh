#!/bin/sh
#===============================================================================
# OpenIPC Doorphone Installer
# https://github.com/OpenIPC/intercom
#===============================================================================

set -e  # Exit on error

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

#===============================================================================
# Функции
#===============================================================================

print_header() {
    clear
    echo "${BLUE}================================================================================"
    echo "  OpenIPC Doorphone Installer v2.0"
    echo "  https://github.com/OpenIPC/intercom"
    echo "================================================================================"
    echo "${NC}"
}

print_step() {
    echo "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

print_warning() {
    echo "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo "${BLUE}[INFO]${NC} $1"
}

check_command() {
    if ! command -v $1 >/dev/null 2>&1; then
        print_error "$1 not found. Please install it first."
        exit 1
    fi
}

#===============================================================================
# Проверка и определение UART
#===============================================================================

detect_uart() {
    print_step "🔍 Detecting available UART ports..."
    
    UART_PORTS=""
    if [ -c /dev/ttyS0 ]; then
        UART_PORTS="$UART_PORTS ttyS0"
    fi
    if [ -c /dev/ttyS1 ]; then
        UART_PORTS="$UART_PORTS ttyS1"
    fi
    if [ -c /dev/ttyS2 ]; then
        UART_PORTS="$UART_PORTS ttyS2"
    fi
    if [ -c /dev/ttyAMA0 ]; then
        UART_PORTS="$UART_PORTS ttyAMA0"
    fi
    
    if [ -z "$UART_PORTS" ]; then
        print_error "No UART ports found!"
        exit 1
    fi
    
    echo "Available UART ports:"
    for port in $UART_PORTS; do
        echo "  - /dev/$port"
    done
    
    # Если только один порт, используем его
    if [ $(echo $UART_PORTS | wc -w) -eq 1 ]; then
        UART_DEV="/dev/$UART_PORTS"
        print_info "Auto-selected UART: $UART_DEV"
    else
        # Если несколько портов, спрашиваем пользователя
        while true; do
            printf "Enter UART device to use (e.g., ttyS0): "
            read UART_CHOICE
            UART_DEV="/dev/$UART_CHOICE"
            if [ -c "$UART_DEV" ]; then
                break
            else
                print_error "Device $UART_DEV not found. Try again."
            fi
        done
    fi
    
    echo "$UART_DEV"
}

#===============================================================================
# Запрос SIP настроек
#===============================================================================

ask_sip_settings() {
    print_step "📞 SIP Configuration"
    echo "Leave empty to skip SIP configuration (can be configured later via web)"
    
    printf "SIP Username (e.g., 101): "
    read SIP_USER
    
    if [ -n "$SIP_USER" ]; then
        printf "SIP Server (e.g., 192.168.1.107): "
        read SIP_SERVER
        printf "SIP Password: "
        read SIP_PASS
        printf "Call button number (default: 100): "
        read SIP_CALL_NUMBER
        [ -z "$SIP_CALL_NUMBER" ] && SIP_CALL_NUMBER="100"
    fi
}

#===============================================================================
# Основная установка
#===============================================================================

main() {
    print_header
    
    # Проверка прав
    if [ "$(id -u)" != "0" ]; then
        print_error "This script must be run as root"
        exit 1
    fi
    
    # Определение UART
    UART_DEV=$(detect_uart)
    
    # Запрос SIP настроек
    ask_sip_settings
    
    print_step "🚀 Starting installation..."
    
    #-----------------------------------------------------------------------------
    # 1. Создание необходимых директорий
    #-----------------------------------------------------------------------------
    print_step "📁 Creating directories..."
    mkdir -p /var/www/cgi-bin/p
    mkdir -p /var/www/a
    mkdir -p /usr/share/sounds/doorphone
    mkdir -p /root/backups
    mkdir -p /etc/baresip
    
    #-----------------------------------------------------------------------------
    # 2. Настройка UART
    #-----------------------------------------------------------------------------
    print_step "⚙️ Configuring UART ($UART_DEV)..."
    chmod 666 $UART_DEV
    # Удаляем старые записи если есть
    sed -i "/chmod 666 \/dev\/tty/d" /etc/rc.local
    # Добавляем новую запись перед exit 0
    sed -i "/exit 0/i chmod 666 $UART_DEV" /etc/rc.local
    
    #-----------------------------------------------------------------------------
    # 3. Загрузка файлов с GitHub
    #-----------------------------------------------------------------------------
    print_step "📥 Downloading files from GitHub..."
    
    TEMP_DIR="/tmp/intercom_$$"
    mkdir -p "$TEMP_DIR"
    
    # Скачиваем архив с GitHub
    wget -O "$TEMP_DIR/intercom.tar.gz" https://github.com/OpenIPC/intercom/archive/main.tar.gz
    
    if [ $? -ne 0 ]; then
        print_error "Failed to download from GitHub"
        exit 1
    fi
    
    # Распаковываем
    tar -xzf "$TEMP_DIR/intercom.tar.gz" -C "$TEMP_DIR"
    
    # Копируем CGI скрипты
    print_step "🔄 Installing CGI scripts..."
    cp -r "$TEMP_DIR/intercom-main/cgi-bin/"* /var/www/cgi-bin/
    chmod +x /var/www/cgi-bin/p/*.cgi
    chmod +x /var/www/cgi-bin/backup.cgi 2>/dev/null
    
    # Копируем звуковые файлы (если есть)
    if [ -d "$TEMP_DIR/intercom-main/sounds" ]; then
        print_step "🔊 Installing sound effects..."
        cp -r "$TEMP_DIR/intercom-main/sounds/"* /usr/share/sounds/doorphone/ 2>/dev/null
    fi
    
    # Копируем скрипты
    if [ -d "$TEMP_DIR/intercom-main/scripts" ]; then
        print_step "📜 Installing scripts..."
        cp "$TEMP_DIR/intercom-main/scripts/"* /usr/bin/ 2>/dev/null
        chmod +x /usr/bin/door_monitor.sh
        chmod +x /usr/bin/check_temp_keys.sh 2>/dev/null
    fi
    
    #-----------------------------------------------------------------------------
    # 4. Установка Bootstrap (если нужен)
    #-----------------------------------------------------------------------------
    print_step "🎨 Installing Bootstrap..."
    wget -q -O /var/www/a/bootstrap.min.css https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
    wget -q -O /var/www/a/bootstrap.bundle.min.js https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js
    
    #-----------------------------------------------------------------------------
    # 5. Настройка автозапуска
    #-----------------------------------------------------------------------------
    print_step "⚙️ Configuring autostart..."
    
    # Скрипт автозапуска для door_monitor
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
    
    # Скрипт автозапуска для baresip
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
    
    # HTTP сервер для бэкапов на порту 8080
    if ! grep -q "httpd -p 8080" /etc/rc.local; then
        sed -i "/exit 0/i httpd -p 8080 -h /var/www \&" /etc/rc.local
    fi
    
    # Cron для временных ключей
    if [ -f /usr/bin/check_temp_keys.sh ]; then
        echo "0 * * * * /usr/bin/check_temp_keys.sh" >> /etc/crontabs/root 2>/dev/null
    fi
    
    #-----------------------------------------------------------------------------
    # 6. Базовая конфигурация
    #-----------------------------------------------------------------------------
    print_step "🔧 Creating basic configuration..."
    
    # Создаем пустую базу ключей если её нет
    if [ ! -f /etc/door_keys.conf ]; then
        touch /etc/door_keys.conf
        chmod 666 /etc/door_keys.conf
    fi
    
    # Настройка SIP если пользователь ввел данные
    if [ -n "$SIP_USER" ] && [ -n "$SIP_SERVER" ] && [ -n "$SIP_PASS" ]; then
        print_step "📞 Configuring SIP account..."
        
        # SIP аккаунт
        cat > /etc/baresip/accounts << EOF
# SIP account configured by installer
<sip:$SIP_USER@$SIP_SERVER>;auth_pass=$SIP_PASS;regint=60
EOF
        
        # Номер для кнопки звонка
        echo "$SIP_CALL_NUMBER" > /etc/baresip/call_number
        
        print_info "SIP account configured: $SIP_USER@$SIP_SERVER"
    fi
    
    #-----------------------------------------------------------------------------
    # 7. Запуск сервисов
    #-----------------------------------------------------------------------------
    print_step "🚀 Starting services..."
    
    # Запускаем HTTP сервер для бэкапов
    killall httpd 2>/dev/null
    httpd -p 8080 -h /var/www &
    
    # Запускаем door_monitor
    /etc/init.d/S99door restart
    
    # Запускаем SIP если настроен
    if [ -f /etc/baresip/accounts ]; then
        /etc/init.d/S97baresip restart
    fi
    
    #-----------------------------------------------------------------------------
    # 8. Завершение
    #-----------------------------------------------------------------------------
    print_step "🧹 Cleaning up..."
    rm -rf "$TEMP_DIR"
    
    # Получаем IP адрес
    IP_ADDR=$(ip addr show | grep -o '192\.168\.[0-9]*\.[0-9]*' | head -1)
    [ -z "$IP_ADDR" ] && IP_ADDR="192.168.1.4"
    
    print_header
    echo "${GREEN}✅ Installation complete!${NC}"
    echo ""
    echo "${BLUE}=== Access Information ===${NC}"
    echo "📱 Main Web Interface: ${GREEN}http://$IP_ADDR${NC}"
    echo "💾 Backup Manager:     ${GREEN}http://$IP_ADDR:8080/cgi-bin/p/backup_manager.cgi${NC}"
    echo "🔑 Default login:      ${YELLOW}root / 123456${NC}"
    echo ""
    echo "${BLUE}=== UART Configuration ===${NC}"
    echo "🔌 UART Device:        ${GREEN}$UART_DEV${NC}"
    echo ""
    
    if [ -n "$SIP_USER" ]; then
        echo "${BLUE}=== SIP Configuration ===${NC}"
        echo "📞 Account:            ${GREEN}$SIP_USER@$SIP_SERVER${NC}"
        echo "🔢 Call Number:        ${GREEN}$SIP_CALL_NUMBER${NC}"
        echo ""
    fi
    
    echo "${BLUE}=== Commands ===${NC}"
    echo "View logs:             ${YELLOW}tail -f /var/log/door_monitor.log${NC}"
    echo "Add test key:          ${YELLOW}/usr/bin/door_monitor.sh add 12345678 \"Test User\"${NC}"
    echo "Restart services:      ${YELLOW}/etc/init.d/S99door restart${NC}"
    echo ""
    echo "${GREEN}Enjoy your new OpenIPC Doorphone!${NC}"
    echo "================================================================================"
}

#===============================================================================
# Запуск
#===============================================================================

main