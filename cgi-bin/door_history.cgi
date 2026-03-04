#!/bin/sh
echo "Content-type: text/html"
echo ""

cat << 'EOFH'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Полная история - Домофон</title>
    <link rel="stylesheet" href="/a/bootstrap.min.css">
    <style>
        body { background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .filter-panel { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .table { width: 100%; border-collapse: collapse; }
        .table th { background: #f0f0f0; padding: 10px; text-align: left; }
        .table td { padding: 10px; border-bottom: 1px solid #e0e0e0; }
        .success { color: #4caf50; }
        .danger { color: #f44336; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #1976d2; color: white; }
        .btn-success { background: #4caf50; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .nav-bar { margin-bottom: 20px; }
        .nav-bar a { margin-right: 10px; }
        .time-badge { color: #666; font-size: 12px; }
        .event-count { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-bar">
            <a href="/cgi-bin/status.cgi" class="btn btn-primary btn-sm">🏠 Главная</a>
            <a href="/cgi-bin/p/door_keys.cgi" class="btn btn-primary btn-sm">🔑 Управление ключами</a>
        </div>

        <h1>📋 Полная история событий</h1>

        <div class="filter-panel">
            <div class="row">
                <div class="col-md-3">
                    <input type="text" id="filterKey" class="form-control" placeholder="Фильтр по ключу">
                </div>
                <div class="col-md-3">
                    <select id="filterEvent" class="form-control">
                        <option value="">Все события</option>
                        <option value="ACCESS_GRANTED">✅ Успешные проходы</option>
                        <option value="ACCESS_DENIED">❌ Отказы</option>
                        <option value="MANUAL_OPEN">🚪 Ручное открытие</option>
                        <option value="INFO">📌 Информация</option>
                    </select>
                </div>
                <div class="col-md-2">
                    <input type="date" id="filterDate" class="form-control">
                </div>
                <div class="col-md-2">
                    <button class="btn btn-primary w-100" onclick="applyFilter()">Применить</button>
                </div>
                <div class="col-md-2">
                    <button class="btn btn-success w-100" onclick="exportCSV()">📥 Экспорт</button>
                </div>
            </div>
        </div>

        <div class="card">
            <table class="table">
                <thead>
                    <tr>
                        <th>Время</th>
                        <th>Событие</th>
                        <th>Детали</th>
                    </tr>
                </thead>
                <tbody id="historyList">
                    <tr><td colspan="3" class="text-center">Загрузка...</td></tr>
                </tbody>
            </table>
            <div class="mt-3 d-flex justify-content-between align-items-center">
                <button class="btn btn-secondary" onclick="loadMore()">Загрузить еще</button>
                <span class="event-count" id="eventCount"></span>
            </div>
        </div>
    </div>

    <script>
        let allEvents = [];
        let displayedEvents = 50;

        function loadFullHistory() {
            fetch('/cgi-bin/p/door_api.cgi?action=get_history&lines=1000')
                .then(response => response.json())
                .then(data => {
                    allEvents = data.events || [];
                    displayEvents();
                })
                .catch(error => {
                    console.error('Error loading history:', error);
                    document.getElementById('historyList').innerHTML = 
                        '<tr><td colspan="3" class="text-center text-danger">Ошибка загрузки истории</td></tr>';
                });
        }

        function displayEvents() {
            const filterKey = document.getElementById('filterKey').value.toLowerCase();
            const filterEvent = document.getElementById('filterEvent').value;
            const filterDate = document.getElementById('filterDate').value;

            let filteredEvents = allEvents.filter(event => {
                const msg = event.msg || '';
                if (filterKey && !msg.toLowerCase().includes(filterKey)) return false;
                if (filterEvent && event.event !== filterEvent) return false;
                if (filterDate && !msg.startsWith(filterDate)) return false;
                return true;
            });

            const tbody = document.getElementById('historyList');
            let html = '';

            if (filteredEvents.length === 0) {
                html = '<tr><td colspan="3" class="text-center">Нет событий</td></tr>';
            } else {
                const eventsToShow = filteredEvents.slice(0, displayedEvents);
                
                eventsToShow.forEach(event => {
                    let className = '';
                    if (event.event === 'ACCESS_GRANTED') className = 'success';
                    else if (event.event === 'ACCESS_DENIED') className = 'danger';
                    
                    // Извлекаем время из сообщения (первые 19 символов)
                    const timeStr = event.msg ? event.msg.substring(0, 19) : '';
                    
                    html += '<tr>' +
                        '<td class="time-badge">' + timeStr + '</td>' +
                        '<td class="' + className + '">' + (event.icon || '📌') + ' ' + event.event.replace(/_/g, ' ') + '</td>' +
                        '<td>' + (event.msg || '') + '</td>' +
                        '</tr>';
                });
            }

            tbody.innerHTML = html;
            document.getElementById('eventCount').textContent = 
                'Показано ' + Math.min(displayedEvents, filteredEvents.length) + ' из ' + filteredEvents.length;
        }

        function applyFilter() {
            displayedEvents = 50;
            displayEvents();
        }

        function loadMore() {
            displayedEvents += 50;
            displayEvents();
        }

        function exportCSV() {
            let csv = 'Время,Событие,Детали\n';
            allEvents.forEach(event => {
                const timeStr = event.msg ? event.msg.substring(0, 19) : '';
                const eventType = event.event.replace(/_/g, ' ');
                csv += '"' + timeStr + '","' + eventType + '","' + (event.msg || '') + '"\n';
            });

            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'door_history.csv';
            link.click();
        }

        // Автоматическое обновление при изменении фильтров
        document.getElementById('filterKey').addEventListener('input', applyFilter);
        document.getElementById('filterEvent').addEventListener('change', applyFilter);
        document.getElementById('filterDate').addEventListener('change', applyFilter);

        // Загружаем историю
        loadFullHistory();

        // Обновляем каждые 10 секунд
        setInterval(loadFullHistory, 10000);
    </script>
</body>
</html>
EOFH

