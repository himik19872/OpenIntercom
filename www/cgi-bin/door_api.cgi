#!/bin/sh
echo "Content-type: application/json; charset=utf-8"
echo ""

# Функция для URL декодирования
urldecode() {
    echo -e "$(echo "$1" | sed 's/+/ /g;s/%/\\x/g')"
}

# Функция для экранирования JSON
json_escape() {
    echo "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

# Функция для логирования с ограничением по времени
log_event() {
    event="$1"
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp - $event" >> /var/log/door_monitor.log
    
    # Оставляем только последние 1000 строк (примерно 2-3 дня при 5-10 событиях в день)
    tail -n 1000 /var/log/door_monitor.log > /tmp/door_monitor.tmp
    mv /tmp/door_monitor.tmp /var/log/door_monitor.log
}

# Функция для получения последних событий с лимитом
get_recent_events() {
    limit=${1:-50}
    if [ -f /var/log/door_monitor.log ]; then
        tail -n $limit /var/log/door_monitor.log
    fi
}

# Функция для получения статуса двери
get_door_status() {
    if [ -f /tmp/door_status.tmp ]; then
        cat /tmp/door_status.tmp
    else
        echo "unknown"
    fi
}

# Сохраняем статус двери при каждом изменении
update_door_status() {
    status="$1"
    echo "$status" > /tmp/door_status.tmp
}

# Получаем action из QUERY_STRING
action=$(echo "$QUERY_STRING" | sed -n 's/.*action=\([^&]*\).*/\1/p')

# Читаем POST данные если есть
if [ "$REQUEST_METHOD" = "POST" ]; then
    read POST_STRING
    key=$(echo "$POST_STRING" | sed -n 's/.*key=\([^&]*\).*/\1/p')
    owner=$(echo "$POST_STRING" | sed -n 's/.*owner=\([^&]*\).*/\1/p')
    duration=$(echo "$POST_STRING" | sed -n 's/.*duration=\([^&]*\).*/\1/p')
    settings=$(echo "$POST_STRING" | sed -n 's/.*settings=\([^&]*\).*/\1/p')
    
    if [ -n "$key" ]; then
        key=$(urldecode "$key")
    fi
    if [ -n "$owner" ]; then
        owner=$(urldecode "$owner")
    fi
    if [ -n "$settings" ]; then
        settings=$(urldecode "$settings")
    fi
fi

case "$action" in
    "list_keys")
        echo -n '{"keys": ['
        if [ -f /etc/door_keys.conf ]; then
            first=true
            cat /etc/door_keys.conf | while IFS='|' read k o d; do
                if [ -n "$k" ]; then
                    if [ "$first" = true ]; then
                        first=false
                    else
                        echo -n ','
                    fi
                    k=$(json_escape "$k")
                    o=$(json_escape "$o")
                    d=$(json_escape "$d")
                    echo -n "{\"key\":\"$k\",\"owner\":\"$o\",\"date\":\"$d\"}"
                fi
            done
        fi
        echo ']}'
        ;;
        
    "add_key")
        if [ -n "$key" ]; then
            if [ -z "$owner" ]; then
                owner="Unknown"
            fi
            if grep -q "^$key|" /etc/door_keys.conf 2>/dev/null; then
                echo '{"status": "error", "message": "Ключ уже существует"}'
            else
                echo "$key|$owner|$(date '+%Y-%m-%d')" >> /etc/door_keys.conf
                log_event "KEY_ADDED - Ключ $key добавлен для $owner"
                echo '{"status": "success", "message": "Ключ добавлен"}'
            fi
        else
            echo '{"status": "error", "message": "Не указан ключ"}'
        fi
        ;;
        
    "remove_key")
        if [ -n "$key" ] && [ -f /etc/door_keys.conf ]; then
            grep -v "^$key|" /etc/door_keys.conf > /tmp/keys.tmp
            mv /tmp/keys.tmp /etc/door_keys.conf
            log_event "KEY_REMOVED - Ключ $key удален"
            echo '{"status": "success", "message": "Ключ удален"}'
        else
            echo '{"status": "error", "message": "Ключ не найден"}'
        fi
        ;;
        
    "update_key_owner")
        if [ -n "$key" ] && [ -n "$owner" ] && [ -f /etc/door_keys.conf ]; then
            > /tmp/keys.tmp
            while IFS='|' read k o d; do
                if [ "$k" = "$key" ]; then
                    echo "$key|$owner|$d" >> /tmp/keys.tmp
                else
                    echo "$k|$o|$d" >> /tmp/keys.tmp
                fi
            done < /etc/door_keys.conf
            mv /tmp/keys.tmp /etc/door_keys.conf
            log_event "OWNER_UPDATED - Владелец ключа $key изменен на $owner"
            echo '{"status": "success", "message": "Владелец обновлен"}'
        else
            echo '{"status": "error", "message": "Ошибка обновления"}'
        fi
        ;;
        
    "open_door")
        if [ -c /dev/ttyS0 ]; then
            if [ -n "$duration" ]; then
                echo "OPEN:$duration" > /dev/ttyS0
                log_event "MANUAL_OPEN - Дверь открыта вручную на ${duration}мс"
                echo "{\"status\": \"success\", \"message\": \"Дверь открыта на ${duration}мс\"}"
            else
                echo "OPEN" > /dev/ttyS0
                log_event "MANUAL_OPEN - Дверь открыта вручную"
                echo '{"status": "success", "message": "Дверь открыта"}'
            fi
        else
            echo '{"status": "error", "message": "ESP не подключен"}'
        fi
        ;;
        
    "get_last_key")
        last_key="none"
        if [ -f /tmp/last_key.txt ]; then
            last_key=$(cat /tmp/last_key.txt 2>/dev/null | head -1)
            if [ -z "$last_key" ]; then
                last_key="none"
            fi
        fi
        echo "{\"key\": \"$last_key\"}"
        ;;
        
    "get_history")
        lines=$(echo "$QUERY_STRING" | sed -n 's/.*lines=\([0-9]*\).*/\1/p')
        if [ -z "$lines" ] || [ "$lines" -gt 100 ]; then
            lines=50  # По умолчанию показываем 50 последних событий
        fi
        
        echo -n '{"events": ['
        if [ -f /var/log/door_monitor.log ]; then
            first=true
            get_recent_events $lines | while read line; do
                if [ -n "$line" ]; then
                    if [ "$first" = true ]; then
                        first=false
                    else
                        echo -n ','
                    fi
                    
                    line=$(json_escape "$line")
                    
                    # Определяем тип события для иконки
                    if echo "$line" | grep -q "ALLOWED\|Доступ разрешен"; then
                        icon="✅"
                        event_type="ACCESS_GRANTED"
                    elif echo "$line" | grep -q "DENIED\|Доступ запрещен"; then
                        icon="❌"
                        event_type="ACCESS_DENIED"
                    elif echo "$line" | grep -q "MANUAL_OPEN\|открыта вручную"; then
                        icon="🚪"
                        event_type="MANUAL_OPEN"
                    elif echo "$line" | grep -q "KEY_ADDED\|Ключ добавлен"; then
                        icon="➕"
                        event_type="KEY_ADDED"
                    elif echo "$line" | grep -q "KEY_REMOVED\|Ключ удален"; then
                        icon="🗑️"
                        event_type="KEY_REMOVED"
                    elif echo "$line" | grep -q "DOOR_OPEN\|Дверь открыта"; then
                        icon="🔓"
                        event_type="DOOR_OPEN"
                        # Обновляем статус двери
                        update_door_status "open"
                    elif echo "$line" | grep -q "DOOR_CLOSED\|Дверь закрыта"; then
                        icon="🔒"
                        event_type="DOOR_CLOSED"
                        update_door_status "closed"
                    else
                        icon="📌"
                        event_type="INFO"
                    fi
                    
                    echo -n "{\"msg\":\"$line\",\"icon\":\"$icon\",\"type\":\"$event_type\"}"
                fi
            done
        fi
        echo ']}'
        ;;
        
    "get_status")
        esp_status="disconnected"
        if [ -c /dev/ttyS0 ]; then
            echo "STATUS" > /dev/ttyS0 2>/dev/null
            read -t 1 response < /dev/ttyS0 2>/dev/null
            if [ -n "$response" ]; then
                esp_status="connected"
            else
                esp_status="no_response"
            fi
        fi
        
        if [ -f /etc/door_keys.conf ]; then
            keys_count=$(cat /etc/door_keys.conf 2>/dev/null | wc -l)
        else
            keys_count=0
        fi
        
        # Получаем статус двери
        door_status=$(get_door_status)
        
        echo "{\"esp\": \"$esp_status\", \"keys\": $keys_count, \"door\": \"$door_status\"}"
        ;;
        
    "update_door_status")
        status="$1"
        if [ -n "$status" ]; then
            update_door_status "$status"
            echo "{\"status\": \"success\"}"
        else
            echo "{\"status\": \"error\", \"message\": \"No status provided\"}"
        fi
        ;;
        
    *)
        echo '{"status": "error", "message": "Неизвестное действие"}'
        ;;
esac
