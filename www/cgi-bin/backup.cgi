#!/bin/sh
# Получаем локальный IP камеры
CAMERA_IP=$(ip -4 addr show | grep -o '192\.168\.[0-9]*\.[0-9]*' | head -1)

# Если IP не найден, пробуем другие варианты
if [ -z "$CAMERA_IP" ]; then
    CAMERA_IP=$(ifconfig | grep -o '192\.168\.[0-9]*\.[0-9]*' | head -1)
fi

# Если всё ещё нет IP, используем localhost
if [ -z "$CAMERA_IP" ]; then
    CAMERA_IP="127.0.0.1"
fi

# Отправляем HTML с мета-редиректом (работает в любом сервере)
echo "Content-type: text/html"
echo ""
echo "<!DOCTYPE html>"
echo "<html>"
echo "<head>"
echo "<meta http-equiv=\"refresh\" content=\"0;url=http://${CAMERA_IP}:8080/cgi-bin/p/backup_manager.cgi\">"
echo "</head>"
echo "<body>"
echo "<p>Redirecting to <a href=\"http://${CAMERA_IP}:8080/cgi-bin/p/backup_manager.cgi\">Backup Manager</a>...</p>"
echo "</body>"
echo "</html>"
