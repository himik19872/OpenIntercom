#!/bin/sh
echo "Content-type: application/json"
echo ""

DEBUG_LOG="/tmp/sip_api_debug.log"
echo "$(date): ===== START =====" >> $DEBUG_LOG

# Читаем POST данные напрямую из stdin
if [ "$REQUEST_METHOD" = "POST" ]; then
    # Читаем весь stdin
    POST_DATA=$(cat)
    echo "$(date): POST_DATA = '$POST_DATA'" >> $DEBUG_LOG
    
    # Ищем settings= в строке
    if echo "$POST_DATA" | grep -q "settings="; then
        # Извлекаем значение settings
        settings_part=$(echo "$POST_DATA" | sed -n 's/.*settings=\([^&]*\).*/\1/p')
        echo "$(date): settings_part = '$settings_part'" >> $DEBUG_LOG
        
        if [ -n "$settings_part" ]; then
            # Декодируем URL
            settings=$(echo -e "$(echo "$settings_part" | sed 's/+/ /g;s/%/\\x/g')")
            echo "$(date): decoded settings = '$settings'" >> $DEBUG_LOG
            
            # Парсим JSON
            user=$(echo "$settings" | sed -n 's/.*"user":"\([^"]*\)".*/\1/p')
            server=$(echo "$settings" | sed -n 's/.*"server":"\([^"]*\)".*/\1/p')
            pass=$(echo "$settings" | sed -n 's/.*"pass":"\([^"]*\)".*/\1/p')
            transport=$(echo "$settings" | sed -n 's/.*"transport":"\([^"]*\)".*/\1/p')
            
            echo "$(date): Parsed - user=$user, server=$server, transport=$transport" >> $DEBUG_LOG
            
            # Проверяем autoAnswer
            if echo "$settings" | grep -q '"autoAnswer":true'; then
                ACCOUNT="<sip:$user@$server;transport=$transport>;auth_pass=$pass;answermode=auto;regint=60"
                echo "$(date): autoAnswer=true" >> $DEBUG_LOG
            else
                ACCOUNT="<sip:$user@$server;transport=$transport>;auth_pass=$pass;regint=60"
                echo "$(date): autoAnswer=false" >> $DEBUG_LOG
            fi
            
            # Сохраняем аккаунт
            {
                echo "# SIP account for doorphone"
                echo "$ACCOUNT"
            } > /etc/baresip/accounts
            
            # Перезапускаем SIP
            killall baresip 2>/dev/null
            sleep 1
            baresip -f /etc/baresip -d > /dev/null 2>&1 &
            
            echo "{\"status\": \"success\", \"message\": \"Настройки сохранены для $user\"}"
        else
            echo "$(date): ERROR - settings_part is empty" >> $DEBUG_LOG
            echo "{\"status\": \"error\", \"message\": \"settings_part empty\"}"
        fi
    else
        echo "$(date): ERROR - settings= not found in '$POST_DATA'" >> $DEBUG_LOG
        echo "{\"status\": \"error\", \"message\": \"settings not found\", \"post\": \"$POST_DATA\"}"
    fi
else
    echo "$(date): ERROR - not POST, method=$REQUEST_METHOD" >> $DEBUG_LOG
    echo '{"status": "error", "message": "POST required"}'
fi

echo "$(date): ===== END =====" >> $DEBUG_LOG

    "save_call_number")
        number=$(echo "$QUERY_STRING" | sed -n 's/.*number=\([^&]*\).*/\1/p')
        if [ -n "$number" ]; then
            number=$(urldecode "$number")
            echo "$number" > /etc/baresip/call_number
            log_event "Call number updated to $number"
            echo "{\"status\": \"success\", \"message\": \"Номер вызова сохранен: $number\"}"
        else
            echo "{\"status\": \"error\", \"message\": \"Не указан номер\"}"
        fi
        ;;
        
    "make_call")
        number=$(echo "$QUERY_STRING" | sed -n 's/.*number=\([^&]*\).*/\1/p')
        if [ -z "$number" ]; then
            # Если номер не указан, берем из файла
            if [ -f /etc/baresip/call_number ]; then
                number=$(cat /etc/baresip/call_number)
            else
                number="100"
            fi
        fi
        
        if [ -n "$number" ]; then
            echo "/dial $number" | nc 127.0.0.1 3000
            log_event "Manual call to $number"
            echo "{\"status\": \"success\", \"message\": \"Звонок на $number\"}"
        else
            echo "{\"status\": \"error\", \"message\": \"Не указан номер\"}"
        fi
        ;;
