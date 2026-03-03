#!/bin/sh
echo "Content-type: text/html; charset=utf-8"
echo ""

# HTML страница
cat << 'EOFH'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Управление домофоном</title>
    <link rel="stylesheet" href="/a/bootstrap.min.css">
    <style>
        body { background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .status-panel { display: flex; gap: 20px; flex-wrap: wrap; background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .status-item { display: flex; align-items: center; gap: 10px; }
        .status-led { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
        .green { background: #4caf50; }
        .red { background: #f44336; }
        .yellow { background: #ffc107; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #1976d2; color: white; }
        .btn-success { background: #4caf50; color: white; }
        .btn-danger { background: #f44336; color: white; }
        .table { width: 100%; border-collapse: collapse; }
        .table th { background: #f0f0f0; padding: 10px; text-align: left; }
        .table td { padding: 10px; border-bottom: 1px solid #e0e0e0; }
        .history-log { background: #1e1e1e; color: #4af899; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 400px; overflow-y: auto; white-space: pre-wrap; }
        .door-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
        .door-open { background: #ffebee; color: #c62828; }
        .door-closed { background: #e8f5e8; color: #2e7d32; }
        .toast { position: fixed; top: 20px; right: 20px; background: #333; color: white; padding: 12px 24px; border-radius: 4px; z-index: 1000; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔑 Управление домофоном</h1>
        
        <div class="status-panel">
            <div class="status-item">
                <span class="status-led" id="espLed"></span>
                <span id="espStatus">ESP: Проверка...</span>
            </div>
            <div class="status-item">
                <span class="status-led" id="doorLed"></span>
                <span id="doorStatus">Дверь: Проверка...</span>
            </div>
            <div class="status-item">
                <span id="keysCount">Ключей: 0</span>
            </div>
            <div>
                <button class="btn btn-primary" onclick="openDoor()">🚪 Открыть дверь</button>
            </div>
        </div>

        <div class="card">
            <h3>🔑 Ключи доступа</h3>
            <table class="table">
                <thead>
                    <tr><th>Ключ</th><th>Владелец</th><th>Дата</th><th>Действия</th></tr>
                </thead>
                <tbody id="keysList">
                    <tr><td colspan="4" class="text-center">Загрузка...</td></tr>
                </tbody>
            </table>
            
            <div class="mt-3">
                <h4>Добавить ключ</h4>
                <div class="row g-2">
                    <div class="col-md-4">
                        <input type="text" id="newKey" class="form-control" placeholder="Номер ключа">
                    </div>
                    <div class="col-md-4">
                        <input type="text" id="newOwner" class="form-control" placeholder="Владелец">
                    </div>
                    <div class="col-md-2">
                        <button class="btn btn-success w-100" onclick="addKey()">Добавить</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>📋 Последние события (последние 50)</h3>
            <div id="historyLog" class="history-log">Загрузка...</div>
            <div class="mt-2 text-muted small">
                * Хранятся последние 1000 событий (примерно 2-3 дня)
            </div>
        </div>
    </div>

    <script>
        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }

        function loadStatus() {
            fetch('/cgi-bin/p/door_api.cgi?action=get_status')
                .then(r => r.json())
                .then(data => {
                    const espLed = document.getElementById('espLed');
                    const espStatus = document.getElementById('espStatus');
                    const doorLed = document.getElementById('doorLed');
                    const doorStatus = document.getElementById('doorStatus');
                    
                    // Статус ESP
                    if (data.esp === 'connected') {
                        espLed.className = 'status-led green';
                        espStatus.textContent = 'ESP: Подключено';
                    } else {
                        espLed.className = 'status-led red';
                        espStatus.textContent = 'ESP: Отключено';
                    }
                    
                    // Статус двери
                    if (data.door === 'open') {
                        doorLed.className = 'status-led red';
                        doorStatus.innerHTML = '<span class="door-badge door-open">🔓 Дверь ОТКРЫТА</span>';
                    } else if (data.door === 'closed') {
                        doorLed.className = 'status-led green';
                        doorStatus.innerHTML = '<span class="door-badge door-closed">🔒 Дверь ЗАКРЫТА</span>';
                    } else {
                        doorLed.className = 'status-led yellow';
                        doorStatus.textContent = 'Дверь: Неизвестно';
                    }
                    
                    document.getElementById('keysCount').textContent = 'Ключей: ' + data.keys;
                });
        }

        function loadKeys() {
            fetch('/cgi-bin/p/door_api.cgi?action=list_keys')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.getElementById('keysList');
                    if (!data.keys || data.keys.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="4" class="text-center">Нет ключей</td></tr>';
                        return;
                    }
                    tbody.innerHTML = '';
                    data.keys.forEach(item => {
                        tbody.innerHTML += '<tr>' +
                            '<td><code>' + item.key + '</code></td>' +
                            '<td>' + (item.owner || 'Unknown') + '</td>' +
                            '<td>' + (item.date || '') + '</td>' +
                            '<td><button class="btn btn-danger btn-sm" onclick="deleteKey(\'' + item.key + '\')">Удалить</button></td>' +
                            '</tr>';
                    });
                });
        }

        function loadHistory() {
            fetch('/cgi-bin/p/door_api.cgi?action=get_history&lines=50')
                .then(r => r.json())
                .then(data => {
                    const log = document.getElementById('historyLog');
                    if (!data.events || data.events.length === 0) {
                        log.textContent = 'Нет событий';
                        return;
                    }
                    log.innerHTML = data.events.map(e => e.msg).join('\n');
                });
        }

        function addKey() {
            const key = document.getElementById('newKey').value.trim();
            const owner = document.getElementById('newOwner').value.trim() || 'Unknown';
            if (!key) {
                showToast('Введите номер ключа');
                return;
            }
            fetch('/cgi-bin/p/door_api.cgi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'action=add_key&key=' + encodeURIComponent(key) + '&owner=' + encodeURIComponent(owner)
            })
            .then(r => r.json())
            .then(data => {
                showToast(data.message);
                if (data.status === 'success') {
                    document.getElementById('newKey').value = '';
                    document.getElementById('newOwner').value = '';
                    loadKeys();
                    loadHistory();
                }
            });
        }

        function deleteKey(key) {
            if (!confirm('Удалить ключ ' + key + '?')) return;
            fetch('/cgi-bin/p/door_api.cgi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'action=remove_key&key=' + encodeURIComponent(key)
            })
            .then(r => r.json())
            .then(data => {
                showToast(data.message);
                if (data.status === 'success') {
                    loadKeys();
                    loadHistory();
                }
            });
        }

        function openDoor() {
            fetch('/cgi-bin/p/door_api.cgi?action=open_door', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    showToast(data.message);
                    loadHistory();
                });
        }

        // Загружаем данные и обновляем каждые 5 секунд
        document.addEventListener('DOMContentLoaded', function() {
            loadStatus();
            loadKeys();
            loadHistory();
            setInterval(() => {
                loadStatus();
                loadHistory();
            }, 5000);
        });
    </script>
</body>
</html>
EOFH

