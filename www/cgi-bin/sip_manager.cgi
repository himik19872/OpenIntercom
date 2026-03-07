#!/bin/sh
echo "Content-type: text/html; charset=utf-8"
echo ""

# Функция для парсинга текущего аккаунта
parse_account() {
    if [ -f /etc/baresip/accounts ]; then
        ACCOUNT_LINE=$(grep -v "^#" /etc/baresip/accounts | head -1)
        
        SIP_USER=$(echo "$ACCOUNT_LINE" | sed -n 's/.*<sip:\([^@]*\)@.*/\1/p')
        SIP_SERVER=$(echo "$ACCOUNT_LINE" | sed -n 's/.*@\([^;>]*\).*/\1/p')
        SIP_PASS=$(echo "$ACCOUNT_LINE" | sed -n 's/.*auth_pass=\([^;]*\).*/\1/p')
        SIP_TRANSPORT=$(echo "$ACCOUNT_LINE" | sed -n 's/.*transport=\([^;>]*\).*/\1/p')
        
        [ -z "$SIP_TRANSPORT" ] && SIP_TRANSPORT="udp"
        
        if echo "$ACCOUNT_LINE" | grep -q "answermode=auto"; then
            AUTO_ANSWER="checked"
        else
            AUTO_ANSWER=""
        fi
    else
        SIP_USER="101"
        SIP_SERVER="192.168.1.107"
        SIP_PASS="123456"
        SIP_TRANSPORT="udp"
        AUTO_ANSWER=""
    fi
}

# Читаем номер для вызова (по умолчанию 100)
if [ -f /etc/baresip/call_number ]; then
    CALL_NUMBER=$(cat /etc/baresip/call_number)
else
    CALL_NUMBER="100"
fi

# Получаем настройки
parse_account

# Проверяем статус
if pgrep -f "baresip" > /dev/null; then
    SIP_STATUS="running"
    SIP_STATUS_TEXT="Запущен"
    SIP_STATUS_CLASS="green"
    
    # Проверяем регистрацию
    if logread | grep -q "200 OK"; then
        REG_STATUS="registered"
        REG_STATUS_TEXT="Зарегистрирован"
        REG_STATUS_CLASS="green"
    else
        REG_STATUS="waiting"
        REG_STATUS_TEXT="Ожидание регистрации"
        REG_STATUS_CLASS="yellow"
    fi
else
    SIP_STATUS="stopped"
    SIP_STATUS_TEXT="Остановлен"
    SIP_STATUS_CLASS="red"
    REG_STATUS="stopped"
    REG_STATUS_TEXT="SIP не запущен"
    REG_STATUS_CLASS="gray"
fi

# Получаем последние логи
SIP_LOGS=$(logread | grep -i "sip\|baresip\|call" | tail -10 | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')

# HTML страница
cat << EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIP - Домофон</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #f8f9fa;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 32px; color: #1a1a1a; margin: 0; }
        .nav a { color: #1976d2; text-decoration: none; margin-left: 20px; }
        
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 25px;
        }
        .status-card {
            background: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid #e0e0e0;
        }
        .status-label {
            font-size: 14px;
            text-transform: uppercase;
            color: #666;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        .status-value {
            font-size: 28px;
            font-weight: 600;
        }
        .green { color: #2e7d32; }
        .red { color: #c62828; }
        .yellow { color: #ed6c02; }
        .gray { color: #666; }
        
        .btn-group {
            display: flex;
            gap: 12px;
            margin: 25px 0;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-primary { background: #1976d2; color: white; }
        .btn-success { background: #2e7d32; color: white; }
        .btn-warning { background: #ed6c02; color: white; }
        .btn-info { background: #17a2b8; color: white; }
        .btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        
        .form-card {
            background: white;
            padding: 25px;
            border-radius: 16px;
            margin-bottom: 25px;
            border: 1px solid #e0e0e0;
        }
        .form-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #1976d2;
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .form-group { margin-bottom: 15px; }
        .form-group label {
            display: block;
            font-weight: 500;
            margin-bottom: 5px;
            color: #555;
        }
        .form-control {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 15px;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 15px 0;
        }
        .checkbox-group input {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        
        .info-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
        }
        .info-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #1976d2;
        }
        .log {
            background: #1e1e1e;
            color: #4af899;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 13px;
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .dtmf-info {
            background: #e8f5e8;
            border-left: 4px solid #2e7d32;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .dtmf-code {
            font-size: 24px;
            font-weight: bold;
            color: #2e7d32;
            background: #f1f3f4;
            padding: 5px 15px;
            border-radius: 30px;
            display: inline-block;
            margin: 10px 0;
        }
        
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #333;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            z-index: 1000;
            animation: slideIn 0.3s;
        }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .footer {
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📞 SIP</h1>
            <div class="nav">
                <a href="/cgi-bin/status.cgi">🏠 Главная</a>
                <a href="/cgi-bin/p/door_keys.cgi">🔑 Ключи</a>
            </div>
        </div>

        <div class="status-grid">
            <div class="status-card">
                <div class="status-label">SIP клиент</div>
                <div class="status-value $SIP_STATUS_CLASS">$SIP_STATUS_TEXT</div>
            </div>
            <div class="status-card">
                <div class="status-label">Регистрация</div>
                <div class="status-value $REG_STATUS_CLASS">$REG_STATUS_TEXT</div>
            </div>
        </div>

        <div class="btn-group">
            <button class="btn btn-primary" onclick="location.reload()">🔄 Обновить</button>
            <button class="btn btn-success" onclick="restartSIP()">🔄 Перезапустить SIP</button>
            <button class="btn btn-warning" onclick="testCall()">📞 Тестовый звонок</button>
        </div>

        <div class="form-card">
            <div class="form-title">✏️ Настройки SIP аккаунта</div>
            <form id="sipForm" onsubmit="return false;">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Имя пользователя:</label>
                        <input type="text" id="sipUser" class="form-control" value="$SIP_USER">
                    </div>
                    <div class="form-group">
                        <label>SIP Сервер:</label>
                        <input type="text" id="sipServer" class="form-control" value="$SIP_SERVER">
                    </div>
                    <div class="form-group">
                        <label>Пароль:</label>
                        <input type="password" id="sipPass" class="form-control" value="$SIP_PASS">
                    </div>
                    <div class="form-group">
                        <label>Транспорт:</label>
                        <select id="sipTransport" class="form-control">
                            <option value="udp" $( [ "$SIP_TRANSPORT" = "udp" ] && echo "selected")>UDP</option>
                            <option value="tcp" $( [ "$SIP_TRANSPORT" = "tcp" ] && echo "selected")>TCP</option>
                        </select>
                    </div>
                </div>
                
                <div class="checkbox-group">
                    <input type="checkbox" id="autoAnswer" $AUTO_ANSWER>
                    <label for="autoAnswer">Автоматически отвечать на звонки</label>
                </div>
                
                <div class="form-group" style="margin-top: 20px;">
                    <label>📞 Номер для вызова (кнопка на домофоне):</label>
                    <input type="text" id="callNumber" class="form-control" value="$CALL_NUMBER" placeholder="100">
                    <small class="text-muted">Номер, на который будет звонить кнопка вызова</small>
                </div>
                
                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button type="button" class="btn btn-success" onclick="saveSettings()" style="flex: 1;">💾 Сохранить настройки аккаунта</button>
                    <button type="button" class="btn btn-info" onclick="saveCallNumber()" style="flex: 1;">📞 Сохранить номер вызова</button>
                </div>
            </form>
        </div>

        <div class="info-card">
            <div class="info-title">📋 Системные события</div>
            <pre class="log">$SIP_LOGS</pre>
        </div>

        <div class="dtmf-info">
            <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 16px; font-weight: 600;">DTMF код для открытия двери:</span>
                    <span class="dtmf-code">9</span>
                </div>
                <div style="color: #2e7d32;">
                    ⚡ Во время звонка нажмите 9 для открытия двери
                </div>
            </div>
        </div>
        
        <div class="footer">
            OpenIPC • SIP Manager • Домофон
        </div>
    </div>

    <script>
        function showToast(message, isError = false) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            toast.style.background = isError ? '#c62828' : '#2e7d32';
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }

        function saveSettings() {
            const settings = {
                user: document.getElementById('sipUser').value.trim(),
                server: document.getElementById('sipServer').value.trim(),
                pass: document.getElementById('sipPass').value.trim(),
                transport: document.getElementById('sipTransport').value,
                autoAnswer: document.getElementById('autoAnswer').checked
            };

            fetch('/cgi-bin/p/sip_api.cgi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'action=save_sip_settings&settings=' + encodeURIComponent(JSON.stringify(settings))
            })
            .then(response => response.json())
            .then(data => {
                showToast(data.message, data.status !== 'success');
                if (data.status === 'success') {
                    setTimeout(() => location.reload(), 2000);
                }
            })
            .catch(error => showToast('Ошибка: ' + error, true));
        }

        function saveCallNumber() {
            const callNumber = document.getElementById('callNumber').value.trim();
            
            if (!callNumber) {
                showToast('Введите номер', true);
                return;
            }

            fetch('/cgi-bin/p/sip_api.cgi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'action=save_call_number&number=' + encodeURIComponent(callNumber)
            })
            .then(response => response.json())
            .then(data => {
                showToast(data.message, data.status !== 'success');
                if (data.status === 'success') {
                    setTimeout(() => location.reload(), 2000);
                }
            })
            .catch(error => showToast('Ошибка: ' + error, true));
        }

        function restartSIP() {
            if (confirm('Перезапустить SIP клиент?')) {
                fetch('/cgi-bin/p/sip_api.cgi?action=restart_sip', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        showToast(data.message);
                        setTimeout(() => location.reload(), 2000);
                    })
                    .catch(error => showToast('Ошибка: ' + error, true));
            }
        }

        function testCall() {
            const number = document.getElementById('callNumber').value.trim() || '100';
            fetch('/cgi-bin/p/sip_api.cgi?action=make_call&number=' + encodeURIComponent(number))
                .then(response => response.json())
                .then(data => showToast(data.message))
                .catch(error => showToast('Ошибка: ' + error, true));
        }

        // Автообновление каждые 10 секунд
        setTimeout(() => location.reload(), 10000);
    </script>
</body>
</html>
