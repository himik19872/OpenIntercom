# 🚀 Установка OpenIPC Домофона одной командой

Если у вас уже установлена прошивка OpenIPC с поддержкой VoIP, вы можете превратить камеру в полнофункциональный SIP-домофон всего одной командой.

## 📋 Требования

- ✅ Установлена прошивка OpenIPC с поддержкой VoIP
- ✅ Камера подключена к сети (рекомендуется DHCP)
- ✅ SSH доступ к камере (по умолчанию: root/123456)
- ✅ Интернет для скачивания файлов

## 🔧 Быстрая установка

### Способ 1: Через curl (рекомендуется)

Подключитесь по SSH к камере и выполните:

```bash
curl -sL https://raw.githubusercontent.com/OpenIPC/intercom/main/install.sh | sh
Способ 2: Через wget
bash
wget -qO- https://raw.githubusercontent.com/OpenIPC/intercom/main/install.sh | sh
Способ 3: Скачать и запустить вручную
bash
# Скачиваем установщик
wget -O /tmp/install.sh https://raw.githubusercontent.com/OpenIPC/intercom/main/install.sh

# Делаем исполняемым
chmod +x /tmp/install.sh

# Запускаем
/tmp/install.sh
📋 Что делает установщик
Установщик автоматически:

Шаг	Действие
1️⃣	Определяет доступные UART порты (ttyS0, ttyS1, ttyS2, ttyAMA0)
2️⃣	Создает необходимые директории
3️⃣	Скачивает все файлы с GitHub
4️⃣	Устанавливает CGI скрипты в /var/www/cgi-bin/p/
5️⃣	Устанавливает системные скрипты в /usr/bin/
6️⃣	Настраивает права UART в /etc/rc.local
7️⃣	Запускает backup сервер на порту 8080
8️⃣	Создает базу ключей с тестовыми ключами
9️⃣	Настраивает автозапуск монитора двери
🔟	Запускает все сервисы
🌐 После установки
После завершения установки вам будут доступны:

Интерфейс	URL	Описание
Основной веб-интерфейс	http://IP_КАМЕРЫ	Стандартный интерфейс OpenIPC
Управление ключами	http://IP_КАМЕРЫ/cgi-bin/p/door_keys.cgi	В меню Extensions
SIP настройки	http://IP_КАМЕРЫ/cgi-bin/p/sip_manager.cgi	Настройка SIP аккаунта
QR-коды	http://IP_КАМЕРЫ/cgi-bin/p/qr_generator.cgi	Генерация QR-ключей
Временные ключи	http://IP_КАМЕРЫ/cgi-bin/p/temp_keys.cgi	Ключи с ограниченным сроком
Звуки	http://IP_КАМЕРЫ/cgi-bin/p/sounds.cgi	Проверка звуковых эффектов
История	http://IP_КАМЕРЫ/cgi-bin/p/door_history.cgi	Все события двери
Бэкапы	http://IP_КАМЕРЫ:8080/cgi-bin/p/backup_manager.cgi	Резервное копирование
🔑 Тестовые ключи
Установщик добавляет тестовые ключи:

12345678 - Администратор (RFID)

qrdemo - QR тест (QR-код)

0000 - Мастер-ключ (RFID)

📋 Полезные команды
bash
# Проверка статуса сервисов
ps | grep -E 'door_monitor|httpd|baresip'

# Просмотр логов двери
tail -f /var/log/door_monitor.log

# Добавление нового ключа
echo "12345|Имя пользователя|$(date +%Y-%m-%d)" >> /etc/door_keys.conf

# Перезапуск монитора двери
/etc/init.d/S99door restart

# Обновление всех файлов (повторный запуск)
curl -sL https://raw.githubusercontent.com/OpenIPC/intercom/main/install.sh | sh
⚙️ Подключение оборудования
UART подключение
Установщик автоматически определяет ваш UART порт. Подключите ESP32/ESP8266:

Камера	ESP32
TX (GPIO13)	RX (GPIO13)
RX (GPIO15)	TX (GPIO15)
GND	GND
Схема подключения
text
ESP32 (LilyGo T-Call)    Подключаемые устройства
─────────────────────────────────────────────────
GPIO4  ────────────────► RFID считыватель DATA0
GPIO5  ────────────────► RFID считыватель DATA1
3.3V/5V ───────────────► RFID считыватель VCC
GND    ────────────────► RFID считыватель GND

GPIO32 ────────────────► Кнопка выхода (к GND)
GPIO33 ────────────────► Кнопка звонка (к GND)

GPIO14 ────────────────► Реле IN
5V    ────────────────► Реле VCC
GND   ────────────────► Реле GND

GPIO12 ────────────────► Геркон (к GND)

GPIO13 (RX2) ──────────► TX камеры (GPIO13)
GPIO15 (TX2) ──────────► RX камеры (GPIO15)
GND   ─────────────────► GND камеры

Внешний 12V ───────────► Замок (через реле)
🔧 Прошивка ESP32
Загрузите прошивку ESP32 из папки /firmware в репозитории.

🐛 Решение проблем
Проблема	Решение
Установка не удалась	Проверьте интернет, запустите заново
Ошибки 404 при установке	Нет файлов в GitHub - проверьте репозиторий
Сервисы не запускаются	Выполните /etc/init.d/S99door restart
Backup manager 404	Проверьте httpd на порту 8080: ps | grep httpd
UART не найден	Проверьте подключение: ls -la /dev/tty*
📦 Структура репозитория
text
intercom/
├── install.sh                 # Главный установщик
├── www/
│   └── cgi-bin/
│       ├── backup.cgi         # Редирект на порт 8080
│       └── p/                 # Все CGI скрипты домофона
│           ├── door_keys.cgi
│           ├── sip_manager.cgi
│           ├── qr_generator.cgi
│           └── ...
├── usr/
│   └── bin/
│       ├── door_monitor.sh    # Главный скрипт монитора
│       └── check_temp_keys.sh  # Очистка временных ключей
├── etc/
│   ├── door_keys.conf         # Шаблон базы ключей
│   └── baresip/               # SIP конфигурация
│       ├── accounts
│       └── call_number
└── sounds/                    # Звуковые эффекты (опционально)
    ├── ring.pcm
    ├── door_open.pcm
    └── ...
🎉 Успешная установка
После успешной установки вы увидите:

text
==========================================
✅ Installation complete!
==========================================

📱 Main web interface: http://192.168.1.28
💾 Backup manager:     http://192.168.1.28:8080/cgi-bin/p/backup_manager.cgi
🔌 UART device:        /dev/ttyAMA0

🔑 Test keys:
  - 12345678 (Admin)
  - qrdemo (QR Test)
  - 0000 (Master)

==========================================
Enjoy your OpenIPC Doorphone!
==========================================
