Russian
Полное руководство по сборке SIP домофона на OpenIPC
Этот проект превращает IP-камеру с прошивкой OpenIPC в полноценный SIP домофон с доступом по RFID ключам, веб-интерфейсом и дистанционным управлением дверью.

📋 Содержание
Требования к оборудованию

Требования к ПО

Шаг 1: Прошивка OpenIPC с VoIP

Шаг 2: Первоначальная настройка камеры

Шаг 3: Контроллер на ESP32/ESP8266

Шаг 4: Установка веб-интерфейса

Шаг 5: Настройка SIP

Шаг 6: Тестирование

Решение проблем

Структура файлов

Требования к оборудованию
Компонент	Рекомендация	Примечание
IP-камера	Uniview C1L-2WN-G с SSC335DE	"Народная камера за 500 руб."
Микроконтроллер	ESP32 (LilyGo T-Call) или ESP8266 (Wemos D1 mini)	Для управления дверью
Считыватель RFID	Wiegand 26/34 (3.3V или 5V)	Любой стандартный
Модуль реле	1-канальное 5V	Для управления замком
Геркон	Нормально-замкнутый	Датчик положения двери
Кнопки	2 тактовые кнопки	Выход и вызов
Блок питания	12V для замка, 5V для ESP	Внешнее питание
Требования к ПО
Прошивка OpenIPC с VoIP поддержкой (ssc335de_ultimate_uniview-c1l-2wn-g-voip-nor.tgz)

Arduino IDE для ESP32/ESP8266

Python 3 (для начальной настройки)

Веб-браузер для конфигурации

Шаг 1: Прошивка OpenIPC с VoIP
1.1 Скачать прошивку
bash
# Базовая прошивка
wget https://github.com/OpenIPC/firmware/releases/download/image/openipc-ssc335de-nor-ultimate.bin

# Обновление с VoIP
wget https://github.com/OpenIPC/builder/releases/download/latest/ssc335de_ultimate_uniview-c1l-2wn-g-voip-nor.tgz
1.2 Прошивка программатором
Используйте программатор SPI (CH341A и т.п.) для записи openipc-ssc335de-nor-ultimate.bin в NOR flash камеры.

1.3 Первый запуск и подключение к сети
Подключите камеру по Ethernet (обязательно наличие DHCP сервера). Найдите её IP адрес в списке клиентов DHCP роутера.

1.4 Обновление до VoIP прошивки
bash
# Подключитесь по SSH (пароль по умолчанию: 123456)
ssh root@192.168.1.x

# Обновите прошивку (НЕ используйте веб-интерфейс!)
sysupgrade -k -r -f -n -z --url=https://github.com/OpenIPC/builder/releases/download/latest/ssc335de_ultimate_uniview-c1l-2wn-g-voip-nor.tgz
1.5 Настройка WiFi (если нужно)
bash
fw_setenv wlanssid "ИмяВашейСети"
fw_setenv wlanpass "ВашПароль"
reboot
Шаг 2: Первоначальная настройка камеры
2.1 Подключение по SSH
bash
ssh root@192.168.1.4  # Используйте IP вашей камеры
2.2 Настройка UART
bash
# Устанавливаем права на UART
chmod 666 /dev/ttyS0
echo 'chmod 666 /dev/ttyS0' >> /etc/rc.local
2.3 Проверка UART портов
bash
ls -la /dev/tty*
# Должны быть ttyS0, ttyS1, ttyS2
Шаг 3: Контроллер на ESP32/ESP8266
3.1 Схема подключения
text
ESP32 (LilyGo T-Call)    Подключаемые устройства
---------------------    -----------------------
GPIO4  ----------------> Считыватель DATA0
GPIO5  ----------------> Считыватель DATA1
3.3V/5V ---------------> Считыватель VCC
GND    ----------------> Считыватель GND

GPIO32 ----------------> Кнопка выхода (другой контакт на GND)
GPIO33 ----------------> Кнопка вызова (другой контакт на GND)

GPIO14 ----------------> Модуль реле IN
5V    ----------------> Модуль реле VCC
GND   ----------------> Модуль реле GND

GPIO12 ----------------> Геркон (другой контакт на GND)

GPIO13 (RX2) -----------> Камера TX (GPIO13)
GPIO15 (TX2) -----------> Камера RX (GPIO15)
GND   -------------------> Камера GND

Внешний 12V ------------> Замок (через контакты реле)
3.2 Прошивка ESP32
Полный код прошивки доступен в папке /firmware.

3.3 Установка в Arduino IDE
Установите поддержку ESP32 в Arduino IDE

Выберите плату: "LilyGo T-Call" или "ESP32 Dev Module"

Скопируйте код прошивки

Установите правильные пины для вашей платы

Загрузите прошивку в ESP32

3.4 Проверка подключения
На камере проверьте логи:

bash
tail -f /var/log/door_monitor.log
Должно появиться: ESP reported ready

Шаг 4: Установка веб-интерфейса
4.1 Создание структуры папок
bash
mkdir -p /var/www/cgi-bin/p
mkdir -p /var/www/a
4.2 Установка файлов
Скопируйте все файлы из папки /www в /var/www/ на камере.

Основные файлы:

cgi-bin/p/door_api.cgi - API для управления ключами

cgi-bin/p/door_keys.cgi - интерфейс управления ключами

cgi-bin/p/door_history.cgi - история событий

cgi-bin/p/sip_api.cgi - SIP API

cgi-bin/p/sip_manager.cgi - интерфейс управления SIP

cgi-bin/p/sip_save.cgi - сохранение настроек SIP

4.3 Установка прав
bash
chmod +x /var/www/cgi-bin/p/*.cgi
4.4 Добавление в меню
Отредактируйте /var/www/cgi-bin/p/header.cgi и добавьте:

html
<li><a class="dropdown-item" href="/cgi-bin/p/door_keys.cgi">🔑 Домофон</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/sip_manager.cgi">📞 SIP</a></li>
4.5 Скриншоты веб-интерфейса
Управление ключами	Настройки SIP
https:///screenshots/1.png?raw=true	https:///screenshots/2.png?raw=true
Управление RFID ключами, история, открытие двери	Настройка SIP аккаунта и номера вызова
Статус двери	История событий
https:///screenshots/3.png?raw=true	https:///screenshots/4.png?raw=true
Статус двери в реальном времени с LED индикацией	Последние 50 событий с автообновлением
Шаг 5: Настройка SIP
5.1 Настройка SIP аккаунта
Через веб-интерфейс:

Откройте http://192.168.1.4/cgi-bin/p/sip_manager.cgi

Введите данные SIP аккаунта:

Имя пользователя (например, 101)

Сервер (например, 192.168.1.107)

Пароль

Транспорт (обычно UDP)

5.2 Установка номера для кнопки вызова
В том же интерфейсе укажите номер для кнопки вызова (по умолчанию 100).

5.3 Тестирование SIP
bash
# Тестовый звонок вручную
echo "/dial 100" | nc 127.0.0.1 3000
5.4 Настройка автозапуска
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
Шаг 6: Тестирование
6.1 Проверка всех компонентов
Компонент	Тест	Ожидаемый результат
Подключение ESP32	tail -f /var/log/door_monitor.log	STATUS каждые 5 секунд
Кнопка вызова	Нажать кнопку	Звонок на заданный номер
Кнопка выхода	Нажать кнопку	Дверь открывается
RFID ключ	Приложить ключ	Дверь открывается (если ключ в базе)
Датчик двери	Открыть/закрыть дверь	Статус меняется в веб
Веб-интерфейс	Открыть браузер	Все функции работают
6.2 Полезные команды
bash
# Проверка монитора двери
ps aux | grep door_monitor

# Проверка SIP
ps aux | grep baresip

# Просмотр логов
tail -f /var/log/door_monitor.log
tail -f /var/log/baresip.log

# Добавить ключ вручную
/usr/bin/door_monitor.sh add 12345678 "Имя пользователя"

# Список ключей
/usr/bin/door_monitor.sh list

# Установить номер вызова
/usr/bin/door_monitor.sh call_number 101
Решение проблем
Проблема	Решение
Нет связи с ESP	Проверьте подключение UART (TX->RX, RX->TX), проверьте общий GND, проверьте скорость (115200)
SIP не регистрируется	Проверьте доступность SIP сервера, проверьте правильность учетных данных, проверьте файерволл (порт 5060 UDP)
Веб-интерфейс ошибка 500	Проверьте права на файлы (chmod +x *.cgi), проверьте синтаксис: sh -n /путь/к/файлу.cgi
Ложные срабатывания ключей	Добавьте подтягивающие резисторы на линии Wiegand, измените MIN_KEY_LENGTH в door_monitor.sh
Структура файлов
text
/usr/bin/
├── door_monitor.sh          # Основной скрипт монитора
├── dtmf_9.sh                # Обработчик DTMF для открытия двери
└── start_baresip.sh         # Скрипт запуска SIP

/etc/
├── baresip/
│   ├── accounts             # SIP аккаунт
│   ├── config               # Конфигурация SIP
│   └── call_number          # Номер для кнопки вызова
├── door_keys.conf           # База разрешенных ключей
└── rc.local                 # Автозапуск

/var/www/cgi-bin/p/
├── door_api.cgi             # API управления ключами
├── door_keys.cgi            # Интерфейс управления ключами
├── door_history.cgi         # История событий
├── sip_api.cgi              # SIP API
├── sip_manager.cgi          # Интерфейс управления SIP
└── sip_save.cgi             # Сохранение настроек SIP

/var/log/
├── door_monitor.log         # События двери
└── baresip.log              # События SIP
Лицензия
MIT License - свободно используйте и модифицируйте!

Авторы
На основе проекта OpenIPC
