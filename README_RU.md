# SIP Домофон на OpenIPC

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenIPC](https://img.shields.io/badge/OpenIPC-Совместимо-brightgreen)](https://openipc.org)

Превратите любую совместимую IP-камеру с прошивкой OpenIPC в **полнофункциональный SIP-домофон** с поддержкой RFID/QR-ключей, веб-управлением, удаленным открытием двери и системой резервного копирования.

## 📋 Содержание
- [Возможности](#возможности)
- [Требования к оборудованию](#требования-к-оборудованию)
- [Требования к ПО](#требования-к-по)
- [Быстрый старт](#быстрый-старт)
- [Шаг 1: Прошивка OpenIPC с VoIP](#шаг-1-прошивка-openipc-с-voip)
- [Шаг 2: Начальная настройка камеры](#шаг-2-начальная-настройка-камеры)
- [Шаг 3: Контроллер ESP32/ESP8266](#шаг-3-контроллер-esp32esp8266)
- [Шаг 4: Установка веб-интерфейса](#шаг-4-установка-веб-интерфейса)
- [Шаг 5: Настройка SIP](#шаг-5-настройка-sip)
- [Шаг 6: Расширенные возможности](#шаг-6-расширенные-возможности)
  - [6.1 QR-коды](#61-qr-коды)
  - [6.2 Временные ключи](#62-временные-ключи)
  - [6.3 Звуковые эффекты](#63-звуковые-эффекты)
  - [6.4 Система бэкапов](#64-система-бэкапов)
- [Шаг 7: Тестирование](#шаг-7-тестирование)
- [Решение проблем](#решение-проблем)
- [Структура файлов](#структура-файлов)
- [Обновления и история изменений](#обновления-и-история-изменений)
- [Лицензия](#лицензия)

## ✨ Возможности

| Функция | Описание | Статус |
|---------|----------|--------|
| **SIP-звонки** | Вызов на SIP-сервер при нажатии кнопки | ✅ Стабильно |
| **RFID-ключи** | Поддержка считывателей Wiegand 26/34 | ✅ Стабильно |
| **QR-коды** | Генерация и сканирование QR-ключей | ✅ НОВОЕ |
| **Временные ключи** | Коды доступа с ограниченным сроком | ✅ НОВОЕ |
| **Звуковые эффекты** | Воспроизведение звуков при событиях | ✅ НОВОЕ |
| **Система бэкапов** | Полное резервное копирование конфигурации | ✅ НОВОЕ |
| **Веб-интерфейс** | Полное управление через браузер | ✅ Стабильно |
| **Датчик двери** | Геркон для контроля состояния двери | ✅ Стабильно |
| **Кнопка выхода** | Внутренняя кнопка открытия двери | ✅ Стабильно |
| **История событий** | Лог всех событий домофона | ✅ Стабильно |

## Требования к оборудованию

| Компонент | Рекомендация | Примечание |
|-----------|--------------|------------|
| **IP-камера** | Uniview C1L-2WN-G с SSC335DE | "Народная камера за $5" |
| **Микроконтроллер** | ESP32 (LilyGo T-Call) или ESP8266 | Для управления дверью |
| **RFID-считыватель** | Wiegand 26/34 (3.3V или 5V) | Любой стандартный |
| **Реле** | 1-канальное 5V | Для управления замком |
| **Геркон** | НЗ магнитный контакт | Датчик положения двери |
| **Кнопки** | 2x тактовые | Выход и звонок |
| **Блок питания** | 12V для замка, 5V для ESP | Внешнее питание |
| **Динамик** | 8Ω 0.5W | Для звуковых эффектов |

## Требования к ПО
- Прошивка OpenIPC с поддержкой VoIP
- Arduino IDE для ESP32/ESP8266
- Веб-браузер (Chrome, Firefox, Яндекс.Браузер)
- SSH-клиент (PuTTY, Terminal)

---

## Быстрый старт

```bash
# 1. Подключитесь по SSH
ssh root@192.168.1.4  # пароль: 123456

# 2. Скачайте и установите веб-интерфейс
wget -O /tmp/intercom.tar.gz https://github.com/OpenIPC/intercom/archive/main.tar.gz
tar -xzf /tmp/intercom.tar.gz -C /tmp
cp -r /tmp/intercom-main/cgi-bin/* /var/www/cgi-bin/
chmod +x /var/www/cgi-bin/p/*.cgi

# 3. Запустите HTTP-сервер для бэкапов
httpd -p 8080 -h /var/www &
echo 'httpd -p 8080 -h /var/www &' >> /etc/rc.local

# 4. Откройте веб-интерфейс
# Основной UI: http://192.168.1.4
# Менеджер бэкапов: http://192.168.1.4:8080/cgi-bin/p/backup_manager.cgi
Шаг 1: Прошивка OpenIPC с VoIP
1.1 Скачайте прошивку
bash
# Базовая прошивка
wget https://github.com/OpenIPC/firmware/releases/download/image/openipc-ssc335de-nor-ultimate.bin

# VoIP-обновление для Uniview C1L
wget https://github.com/OpenIPC/builder/releases/download/latest/ssc335de_ultimate_uniview-c1l-2wn-g-voip-nor.tgz
1.2 Прошивка программатором
Используйте SPI-программатор (CH341A и т.п.) для прошивки openipc-ssc335de-nor-ultimate.bin в NOR-флеш камеры.

1.3 Первый запуск и подключение к сети
Подключите камеру по Ethernet (требуется DHCP). Найдите её IP-адрес в списке DHCP-клиентов роутера.

1.4 Обновление до VoIP-прошивки
bash
# Подключитесь по SSH
ssh root@192.168.1.x  # пароль по умолчанию: 123456

# Обновите прошивку (НЕ используйте веб-интерфейс!)
sysupgrade -k -r -f -n -z --url=https://github.com/OpenIPC/builder/releases/download/latest/ssc335de_ultimate_uniview-c1l-2wn-g-voip-nor.tgz

# Перезагрузите камеру
reboot
1.5 Настройка WiFi (при необходимости)
bash
fw_setenv wlanssid "Имя_вашей_WiFi_сети"
fw_setenv wlanpass "Пароль_WiFi"
reboot
Шаг 2: Начальная настройка камеры
2.1 Подключение по SSH
bash
ssh root@192.168.1.4  # Используйте IP вашей камеры
2.2 Настройка UART для связи с ESP
bash
# Установите права на UART
chmod 666 /dev/ttyS0
chmod 666 /dev/ttyAMA0 2>/dev/null

# Добавьте в автозапуск
echo 'chmod 666 /dev/ttyS0' >> /etc/rc.local
echo 'chmod 666 /dev/ttyAMA0' >> /etc/rc.local 2>/dev/null
2.3 Проверка UART-портов
bash
ls -la /dev/tty*
# Должны отобразиться ttyS0, ttyS1, ttyS2 (или ttyAMA0)
2.4 Установка необходимых пакетов
bash
# Обновление и установка (если нужно)
opkg update
opkg install coreutils-stat coreutils-stty 2>/dev/null
Шаг 3: Контроллер ESP32/ESP8266
3.1 Схема подключения
text
ESP32 (LilyGo T-Call)    Подключаемые устройства
─────────────────────────────────────────────────
GPIO4  ────────────────► RFID Reader DATA0
GPIO5  ────────────────► RFID Reader DATA1
3.3V/5V ───────────────► RFID Reader VCC
GND    ────────────────► RFID Reader GND

GPIO32 ────────────────► Кнопка выхода (второй контакт на GND)
GPIO33 ────────────────► Кнопка звонка (второй контакт на GND)

GPIO14 ────────────────► Реле IN
5V    ────────────────► Реле VCC
GND   ────────────────► Реле GND

GPIO12 ────────────────► Геркон (второй контакт на GND)

GPIO13 (RX2) ──────────► TX камеры (GPIO13)
GPIO15 (TX2) ──────────► RX камеры (GPIO15)
GND   ─────────────────► GND камеры

GPIO25 ────────────────► Динамик + (через конденсатор 100µF)
GND   ────────────────► Динамик -

Внешний 12V ───────────► Замок (через контакты реле)
3.2 Прошивка ESP32
<details> <summary>📁 Нажмите для полного кода ESP32</summary>
cpp
/*
 * OpenIPC SIP Doorphone - ESP32 Controller
 * Supports: RFID (Wiegand), Buttons, Relay, Reed Switch, Speaker
 */

#include <Arduino.h>

// Pin Definitions
#define PIN_RFID_D0    4
#define PIN_RFID_D1    5
#define PIN_BUTTON_EXIT 32
#define PIN_BUTTON_CALL 33
#define PIN_RELAY      14
#define PIN_REED_SWITCH 12
#define PIN_SPEAKER     25

// UART for camera communication
#define CAMERA_BAUD    115200

// RFID Wiegand variables
volatile unsigned long rfidCardNum = 0;
volatile int rfidBitCount = 0;
volatile unsigned long rfidLastBitTime = 0;
bool rfidReading = false;

// Button states
bool lastExitState = HIGH;
bool lastCallState = HIGH;
bool doorState = false;
bool lastDoorState = false;

// Timing
unsigned long lastStatusTime = 0;
const unsigned long STATUS_INTERVAL = 5000; // Send status every 5 seconds

//==============================================================================
// RFID Wiegand Interrupt Handlers
//==============================================================================
void IRAM_ATTR rfidD0Interrupt() {
  rfidLastBitTime = millis();
  rfidCardNum = (rfidCardNum << 1) | 0;
  rfidBitCount++;
  rfidReading = true;
}

void IRAM_ATTR rfidD1Interrupt() {
  rfidLastBitTime = millis();
  rfidCardNum = (rfidCardNum << 1) | 1;
  rfidBitCount++;
  rfidReading = true;
}

//==============================================================================
// Send command to camera
//==============================================================================
void sendToCamera(const char* cmd) {
  Serial2.println(cmd);
  Serial2.flush();
  Serial.print("[CAM] ");
  Serial.println(cmd);
}

//==============================================================================
// Play tone on speaker
//==============================================================================
void playTone(int frequency, int duration) {
  ledcWriteTone(0, frequency);
  delay(duration);
  ledcWriteTone(0, 0);
}

//==============================================================================
// Play sound effects
//==============================================================================
void playSound(const char* sound) {
  if (strcmp(sound, "door_open") == 0) {
    // Success sound
    playTone(1000, 100);
    delay(50);
    playTone(1500, 200);
  } else if (strcmp(sound, "door_close") == 0) {
    // Door closed sound
    playTone(500, 100);
  } else if (strcmp(sound, "key_denied") == 0) {
    // Denied sound
    playTone(300, 300);
  } else if (strcmp(sound, "button_beep") == 0) {
    // Button press sound
    playTone(800, 50);
  }
}

//==============================================================================
// Process RFID card
//==============================================================================
void processRFID() {
  if (rfidBitCount > 0 && rfidBitCount <= 64) {
    unsigned long now = millis();
    if (now - rfidLastBitTime > 50) { // 50ms no new bits = card read complete
      
      char cardStr[20];
      sprintf(cardStr, "KEY:%lu", rfidCardNum);
      sendToCamera(cardStr);
      
      // Reset for next card
      rfidCardNum = 0;
      rfidBitCount = 0;
      rfidReading = false;
    }
  }
}

//==============================================================================
// Setup
//==============================================================================
void setup() {
  Serial.begin(115200);
  Serial.println("\n==================================");
  Serial.println("OpenIPC SIP Doorphone - ESP32");
  Serial.println("==================================");
  
  // Configure pins
  pinMode(PIN_RFID_D0, INPUT_PULLUP);
  pinMode(PIN_RFID_D1, INPUT_PULLUP);
  pinMode(PIN_BUTTON_EXIT, INPUT_PULLUP);
  pinMode(PIN_BUTTON_CALL, INPUT_PULLUP);
  pinMode(PIN_RELAY, OUTPUT);
  pinMode(PIN_REED_SWITCH, INPUT_PULLUP);
  pinMode(PIN_SPEAKER, OUTPUT);
  
  digitalWrite(PIN_RELAY, LOW);
  
  // Configure speaker PWM
  ledcSetup(0, 1000, 8);
  ledcAttachPin(PIN_SPEAKER, 0);
  
  // Attach RFID interrupts
  attachInterrupt(digitalPinToInterrupt(PIN_RFID_D0), rfidD0Interrupt, FALLING);
  attachInterrupt(digitalPinToInterrupt(PIN_RFID_D1), rfidD1Interrupt, FALLING);
  
  // Initialize camera UART
  Serial2.begin(CAMERA_BAUD, SERIAL_8N1, 13, 15);
  Serial.println("Camera UART initialized");
  
  // Test beep
  playSound("door_open");
  
  Serial.println("ESP32 ready!");
  sendToCamera("ESP32_READY");
  
  lastStatusTime = millis();
}

//==============================================================================
// Main loop
//==============================================================================
void loop() {
  unsigned long now = millis();
  
  //--------------------------------------------------------------------------
  // Process RFID
  //--------------------------------------------------------------------------
  if (rfidReading) {
    processRFID();
  }
  
  //--------------------------------------------------------------------------
  // Read buttons
  //--------------------------------------------------------------------------
  bool exitState = digitalRead(PIN_BUTTON_EXIT);
  if (exitState == LOW && lastExitState == HIGH) {
    Serial.println("Exit button pressed");
    playSound("button_beep");
    sendToCamera("BUTTON:EXIT");
    digitalWrite(PIN_RELAY, HIGH);
    delay(500);
    digitalWrite(PIN_RELAY, LOW);
  }
  lastExitState = exitState;
  
  bool callState = digitalRead(PIN_BUTTON_CALL);
  if (callState == LOW && lastCallState == HIGH) {
    Serial.println("Call button pressed");
    playSound("button_beep");
    sendToCamera("CALL:");
  }
  lastCallState = callState;
  
  //--------------------------------------------------------------------------
  // Read door sensor
  //--------------------------------------------------------------------------
  doorState = (digitalRead(PIN_REED_SWITCH) == LOW);
  if (doorState != lastDoorState) {
    if (doorState) {
      Serial.println("Door closed");
      playSound("door_close");
      sendToCamera("DOOR:CLOSED");
    } else {
      Serial.println("Door opened");
      playSound("door_open");
      sendToCamera("DOOR:OPEN");
    }
    lastDoorState = doorState;
  }
  
  //--------------------------------------------------------------------------
  // Read commands from camera
  //--------------------------------------------------------------------------
  while (Serial2.available()) {
    String cmd = Serial2.readStringUntil('\n');
    cmd.trim();
    
    if (cmd.length() > 0) {
      Serial.print("[CAM] Received: ");
      Serial.println(cmd);
      
      if (cmd == "OPEN") {
        digitalWrite(PIN_RELAY, HIGH);
        delay(500);
        digitalWrite(PIN_RELAY, LOW);
        playSound("door_open");
      }
      else if (cmd == "KEY_ACCEPTED") {
        playSound("door_open");
      }
      else if (cmd == "KEY_DENIED") {
        playSound("key_denied");
      }
      else if (cmd == "OPENIPC_READY") {
        playSound("door_open");
      }
      else if (cmd.startsWith("PLAY:")) {
        String sound = cmd.substring(5);
        if (sound == "ring") playTone(800, 500);
        else if (sound == "beep") playTone(1000, 100);
      }
    }
  }
  
  //--------------------------------------------------------------------------
  // Send periodic status
  //--------------------------------------------------------------------------
  if (now - lastStatusTime > STATUS_INTERVAL) {
    char status[50];
    snprintf(status, sizeof(status), "STATUS:%s,%s",
             doorState ? "CLOSED" : "OPEN",
             rfidReading ? "READING" : "IDLE");
    sendToCamera(status);
    lastStatusTime = now;
  }
  
  delay(10);
}
</details>
3.3 Установка в Arduino IDE
Установите поддержку ESP32 в Arduino IDE

Выберите плату: "LilyGo T-Call" или "ESP32 Dev Module"

Скопируйте код прошивки выше

Настройте пины под вашу плату

Загрузите прошивку в ESP32

3.4 Проверка соединения
bash
# На камере проверьте логи
tail -f /var/log/door_monitor.log
# Должны увидеть: ESP reported ready
Шаг 4: Установка веб-интерфейса
4.1 Создание структуры папок
bash
mkdir -p /var/www/cgi-bin/p
mkdir -p /var/www/a
4.2 Скачивание веб-файлов
bash
# Скачайте с GitHub
wget -O /tmp/intercom.tar.gz https://github.com/OpenIPC/intercom/archive/main.tar.gz
tar -xzf /tmp/intercom.tar.gz -C /tmp

# Скопируйте все файлы
cp -r /tmp/intercom-main/cgi-bin/* /var/www/cgi-bin/

# Установите права
chmod +x /var/www/cgi-bin/p/*.cgi
chmod +x /var/www/cgi-bin/backup.cgi 2>/dev/null
4.3 Установка Bootstrap (если отсутствует)
bash
# Создайте папку для ресурсов
mkdir -p /var/www/a

# Скачайте Bootstrap
wget -O /var/www/a/bootstrap.min.css https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
wget -O /var/www/a/bootstrap.bundle.min.js https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js
4.4 Добавление пунктов меню
Отредактируйте /var/www/cgi-bin/p/header.cgi и добавьте эти строки в выпадающее меню Extensions:

html
<!-- ПУНКТЫ МЕНЮ ДОМОФОНА -->
<li><a class="dropdown-item" href="/cgi-bin/p/door_keys.cgi">🔑 Door Phone</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/sip_manager.cgi">📞 SIP</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/qr_generator.cgi">🎯 QR Keys</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/temp_keys.cgi">⏱️ Temp Keys</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/sounds.cgi">🔊 Sounds</a></li>
<li><a class="dropdown-item" href="/cgi-bin/p/door_history.cgi">📋 History</a></li>
<li><a class="dropdown-item" href="/cgi-bin/backup.cgi">💾 Backups</a></li>
4.5 Установка скрипта монитора двери
bash
# Скачайте скрипт монитора
wget -O /usr/bin/door_monitor.sh https://raw.githubusercontent.com/OpenIPC/intercom/main/scripts/door_monitor.sh
chmod +x /usr/bin/door_monitor.sh

# Добавьте в автозапуск
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
/etc/init.d/S99door start
Шаг 5: Настройка SIP
5.1 Настройка SIP-аккаунта
Откройте http://192.168.1.4/cgi-bin/p/sip_manager.cgi и введите:

Поле	Пример	Описание
Имя пользователя	101	Номер вашего SIP-абонента
Сервер	192.168.1.107	IP-адрес или домен SIP-сервера
Пароль	ваш_пароль	Пароль SIP-аккаунта
Транспорт	UDP	Обычно UDP (попробуйте TCP при проблемах)
5.2 Номер кнопки звонка
В этом же интерфейсе укажите номер для кнопки звонка (по умолчанию: 100).

5.3 Ручная проверка SIP
bash
# Тестовый вызов
echo "/dial 100" | nc 127.0.0.1 3000

# Завершить вызов
echo "/hangup" | nc 127.0.0.1 3000
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
/etc/init.d/S97baresip start
Шаг 6: Расширенные возможности
6.1 QR-коды
Генерируйте QR-коды, которые можно сканировать основным сенсором камеры или внешним считывателем.

Возможности:

Генерация печатных QR-кодов

Сканирование через камеру (требуется детекция движения)

Привязка к пользователям с датой истечения

Массовая генерация для гостей

Как использовать:

Откройте http://192.168.1.4/cgi-bin/p/qr_generator.cgi

Введите номер ключа и имя владельца

Нажмите "Generate QR" для создания QR-кода

Распечатайте или сохраните QR-изображение

Нажмите "Save Key" для добавления в базу

Формат QR-кода:

text
QR:12345678|Имя пользователя|2026-12-31
6.2 Временные ключи
Создавайте ключи с ограниченным сроком действия для гостей, обслуживающего персонала или курьеров.

Возможности:

Установка времени истечения (часы/дни)

Автоматическое удаление по истечении срока

Email/SMS уведомление (опционально)

Отслеживание использования

Как использовать:

Откройте http://192.168.1.4/cgi-bin/p/temp_keys.cgi

Введите номер ключа и имя владельца

Установите срок действия (часы)

Нажмите "Create Temporary Key"

Ключ автоматически удалится по истечении срока

Скрипт проверки срока действия (запускается каждый час через cron):

bash
cat > /usr/bin/check_temp_keys.sh << 'EOF'
#!/bin/sh
KEYS_FILE="/etc/door_keys.conf"
TEMP_FILE="/tmp/keys.tmp"
NOW=$(date +%s)

while IFS='|' read key owner expiry; do
    if [ -n "$expiry" ] && [ "$expiry" -lt "$NOW" ] 2>/dev/null; then
        echo "Removing expired key: $key ($owner)"
        grep -v "^$key|" "$KEYS_FILE" > "$TEMP_FILE"
        mv "$TEMP_FILE" "$KEYS_FILE"
    fi
done < "$KEYS_FILE"
EOF

chmod +x /usr/bin/check_temp_keys.sh
echo "0 * * * * /usr/bin/check_temp_keys.sh" >> /etc/crontabs/root
6.3 Звуковые эффекты
Воспроизводите звуки через подключенный динамик при событиях домофона.

Доступные звуки:

Файл	Событие	Описание
ring.pcm	Звонок в дверь	Рингтон при нажатии кнопки звонка
door_open.pcm	Дверь открыта	Звук успеха при открытии двери
door_close.pcm	Дверь закрыта	Уведомление о закрытии двери
denied.pcm	Доступ запрещен	Звук ошибки при неверном ключе
beep.pcm	Нажатие кнопки	Короткий звук обратной связи
Требования к формату звука:

PCM формат (сырое аудио)

8 кГц, 16 бит, моно

Без заголовков, только сырые данные

Конвертация MP3 в PCM:

bash


# Конвертируйте MP3 в PCM
sox input.mp3 -r 8000 -c 1 -b 16 output.pcm
Загрузка звуков:

bash
# Скопируйте PCM файлы на камеру
scp *.pcm root@192.168.1.4:/usr/share/sounds/doorphone/

# Проверьте звук
echo "/play ring.pcm" | nc 127.0.0.1 3000
6.4 Система бэкапов
Полная система резервного копирования и восстановления всех конфигураций.

Возможности:

✅ Создание бэкапов с выбором компонентов

✅ Загрузка бэкапов через drag & drop

✅ Скачивание бэкапов с правильными именами

✅ Восстановление с проверкой целостности

✅ Удаление старых (хранятся последние 10)

Компоненты для бэкапа:

Компонент	Путь	Описание
CGI скрипты	/var/www/cgi-bin/p/*.cgi	Все файлы веб-интерфейса
SIP конфиг	/etc/baresip/	Аккаунты и настройки SIP
База ключей	/etc/door_keys.conf	Все RFID и QR ключи
Скрипты монитора	/usr/bin/door_monitor.sh	Главный скрипт домофона
Init скрипты	/etc/init.d/S99door	Конфигурация автозапуска
Majestic конфиг	/etc/majestic.yaml	Настройки камеры
UART настройки	/etc/rc.local	Конфигурация портов
Места хранения:

Место	Путь	Доступность
Внутренняя память	/root/backups/	Всегда доступно
SD-карта	/mnt/mmcblk0p1/backups/	Если SD-карта вставлена
USB-накопитель	/mnt/sdX/backups/	Если USB подключен
Настройка сервера для бэкапов:

bash
# Запустите HTTP-сервер на порту 8080 (требуется для загрузки)
httpd -p 8080 -h /var/www &

# Добавьте в автозапуск
sed -i '/exit 0/i httpd -p 8080 -h /var/www \&' /etc/rc.local
Доступ к менеджеру бэкапов:

Способ	URL
Прямой	http://192.168.1.4:8080/cgi-bin/p/backup_manager.cgi
Через меню	Extensions → 💾 Backups
Именование файлов бэкапов:

Созданные: doorphone_backup_ГГГГММДД_ЧЧММСС.tar.gz

Загруженные: uploaded_backup_ГГГГММДД_ЧЧММСС.tar (авто-конвертация)

Ручные команды для бэкапов:

bash
# Создать бэкап вручную
tar -czf /root/backups/manual_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  /var/www/cgi-bin/p/ \
  /etc/baresip/ \
  /etc/door_keys.conf \
  /usr/bin/door_monitor.sh \
  /etc/init.d/S99door \
  /etc/majestic.yaml \
  /etc/rc.local

# Просмотреть список бэкапов
ls -la /mnt/mmcblk0p1/backups/

# Восстановить из бэкапа
cd /tmp
tar -xzf /mnt/mmcblk0p1/backups/doorphone_backup_20260306_123456.tar.gz
cp -rf doorphone_backup_*/* /
Шаг 7: Тестирование
7.1 Проверка всех компонентов
Компонент	Команда для проверки	Ожидаемый результат
ESP32	tail -f /var/log/door_monitor.log	STATUS сообщения каждые 5с
SIP	ps aux | grep baresip	Процесс запущен
HTTP (80)	curl -I http://localhost	200 OK
HTTP (8080)	curl -I http://localhost:8080	200 OK
База ключей	cat /etc/door_keys.conf	Список ключей
Бэкапы	ls -la /mnt/mmcblk0p1/backups/	Список файлов
7.2 Функциональные тесты
Тест	Действие	Ожидаемый результат
Кнопка звонка	Нажмите физическую кнопку	Вызов на настроенный номер
Кнопка выхода	Нажмите физическую кнопку	Реле щёлкает, дверь открывается
RFID ключ	Приложите валидный ключ	Реле щёлкает, дверь открывается
RFID ключ	Приложите невалидный ключ	Звук ошибки, дверь закрыта
QR код	Отсканируйте QR камерой	Ключ добавлен, дверь открывается
Датчик двери	Откройте/закройте дверь	Статус меняется в веб-интерфейсе
Веб-логин	Откройте браузер	Все страницы загружаются
Создать бэкап	Нажмите "Create backup"	Файл появляется в списке
Загрузить бэкап	Перетащите файл	Прогресс-бар, сообщение об успехе
Скачать бэкап	Нажмите скачивание	Файл сохраняется локально
Восстановить	Нажмите восстановление	Файлы восстановлены, подтверждение
7.3 Полезные команды
bash
# Проверка всех сервисов
ps aux | grep -E "door_monitor|baresip|httpd|majestic"

# Просмотр логов
tail -f /var/log/door_monitor.log
tail -f /var/log/baresip.log
tail -f /tmp/upload_debug.log

# Ручное управление ключами
/usr/bin/door_monitor.sh add 12345678 "Иван Петров"
/usr/bin/door_monitor.sh list
/usr/bin/door_monitor.sh remove 12345678
/usr/bin/door_monitor.sh call_number 101

# Тест реле
echo "OPEN" > /dev/ttyS0

# Тест звука
echo "/play ring.pcm" | nc 127.0.0.1 3000

# Проверка дискового пространства
df -h
du -sh /mnt/mmcblk0p1/backups/
Решение проблем
Частые проблемы и их решения
Проблема	Возможная причина	Решение
Нет связи с ESP	Неправильное подключение	Проверьте TX→RX, RX→TX, общий GND
Неверная скорость	Установите 115200 на обоих устройствах
UART не настроен	chmod 666 /dev/ttyS0
SIP не регистрируется	Неверные учетные данные	Проверьте логин/пароль
Брандмауэр блокирует	Откройте UDP порт 5060
Сервер недоступен	Проверьте ping до SIP-сервера
Ошибка 500 в веб-интерфейсе	Неверные права на файлы	chmod +x /var/www/cgi-bin/p/*.cgi
Синтаксическая ошибка	sh -n /путь/к/файлу.cgi
Отсутствуют зависимости	Установите необходимые пакеты
Ложные срабатывания ключей	Нет подтягивающих резисторов	Добавьте резисторы 10кΩ на D0/D1
Электрические помехи	Экранируйте провода, добавьте конденсаторы
Несовместимый считыватель	Попробуйте другой RFID-считыватель
Загрузка бэкапа не работает	HTTP-сервер не запущен	httpd -p 8080 -h /var/www &
Порт 8080 заблокирован	Проверьте брандмауэр
Файл слишком большой	Максимум 100МБ
Ошибка Connection refused на 8080	HTTPD не запущен	Выполните команду запуска
Порт уже занят	killall httpd; httpd -p 8080 -h /var/www &
Нет в автозапуске	Добавьте в /etc/rc.local
Загруженный файл показывает 0 байт	Ошибка парсинга multipart	Проверьте /tmp/upload_debug.log
Нет места на диске	df -h для проверки
Неверный путь сохранения	Проверьте выбранное устройство
QR код не сканируется	Фокус камеры	Отрегулируйте объектив
Слишком низкое разрешение	Включите поток высокого разрешения
Неверный формат	Используйте формат QR:KEY|NAME|DATE
Временные ключи не удаляются	Cron не запущен	Запустите crond
Неверный формат срока	Используйте Unix timestamp
Права на скрипт	chmod +x /usr/bin/check_temp_keys.sh
Нет звука	Динамик не подключен	Проверьте подключение
Звуковые файлы отсутствуют	Скопируйте PCM файлы
Неверный формат	Конвертируйте в 8кГц PCM
Режим отладки
Включите подробное логирование для диагностики:

bash
# Включите отладку в door_monitor.sh
sed -i 's/DEBUG=0/DEBUG=1/' /usr/bin/door_monitor.sh
/etc/init.d/S99door restart

# Наблюдайте за всеми логами
tail -f /var/log/door_monitor.log /var/log/baresip.log /tmp/upload_debug.log
Сброс к настройкам по умолчанию
bash
# Сброс базы ключей
rm /etc/door_keys.conf
touch /etc/door_keys.conf
chmod 666 /etc/door_keys.conf

# Сброс SIP конфигурации
rm -rf /etc/baresip
mkdir -p /etc/baresip

# Сброс веб-файлов
rm -rf /var/www/cgi-bin/p/*
# Переустановите с GitHub

# Перезагрузка
reboot
Структура файлов
text
/
├── usr/
│   └── bin/
│       ├── door_monitor.sh          # Главный скрипт домофона
│       ├── dtmf_9.sh                # DTMF обработчик для открытия двери
│       ├── start_baresip.sh         # Скрипт запуска SIP
│       └── check_temp_keys.sh       # Проверка срока временных ключей
│
├── etc/
│   ├── baresip/
│   │   ├── accounts                 # Конфигурация SIP аккаунта
│   │   ├── config                   # Общая конфигурация SIP
│   │   └── call_number              # Номер для кнопки звонка
│   ├── door_keys.conf               # ⭐ БАЗА КЛЮЧЕЙ (RFID, QR, временные)
│   ├── rc.local                     # Команды автозапуска
│   ├── init.d/
│   │   ├── S97baresip               # Автозапуск SIP
│   │   └── S99door                  # Автозапуск монитора двери
│   └── crontabs/
│       └── root                     # Cron задачи (очистка временных ключей)
│
├── var/
│   └── www/
│       ├── a/                        # Ресурсы (Bootstrap, CSS, JS)
│       │   ├── bootstrap.min.css
│       │   └── bootstrap.bundle.min.js
│       └── cgi-bin/
│           ├── backup.cgi            # Редирект на порт 8080
│           └── p/
│               ├── backup_manager.cgi # Интерфейс управления бэкапами
│               ├── backup_api.cgi     # API для бэкапов
│               ├── upload_final.cgi   # Обработчик загрузки файлов
│               ├── door_api.cgi       # API управления ключами
│               ├── door_keys.cgi      # Интерфейс управления ключами
│               ├── door_history.cgi   # Интерфейс истории событий
│               ├── sip_api.cgi        # API для SIP
│               ├── sip_manager.cgi    # Интерфейс настройки SIP
│               ├── qr_api.cgi         # API для QR-кодов
│               ├── qr_generator.cgi   # Генератор QR-кодов
│               ├── sounds.cgi         # Интерфейс звуковых эффектов
│               ├── play_sound.cgi     # Проигрыватель звуков
│               ├── temp_keys.cgi      # Интерфейс временных ключей
│               └── header.cgi         # Конфигурация меню
│
└── var/
    └── log/
        ├── door_monitor.log          # Лог событий двери
        ├── baresip.log               # Лог событий SIP
        └── upload_debug.log          # Отладочный лог загрузок

/mnt/
├── mmcblk0p1/
│   └── backups/                      # Бэкапы на SD-карте
└── sdX/
    └── backups/                      # Бэкапы на USB-накопителе

/root/
└── backups/                          # Бэкапы во внутренней памяти

/usr/share/
└── sounds/
    └── doorphone/                    # Звуковые эффекты
        ├── ring.pcm
        ├── door_open.pcm
        ├── door_close.pcm
        ├── denied.pcm
        └── beep.pcm
Обновления и история изменений
Версия 2.0 (Март 2026)
🚀 Новые возможности
Функция	Описание	Добавлено в
QR-коды	Генерация и сканирование QR-кодов для доступа	v2.0
Временные ключи	Коды доступа с ограниченным сроком действия	v2.0
Звуковые эффекты	Аудио-обратная связь для событий двери	v2.0
Система бэкапов	Полное резервное копирование конфигурации	v2.0
Drag & Drop загрузка	Удобная загрузка файлов с индикатором прогресса	v2.0
HTTP-сервер на 8080	Отдельный порт для загрузки файлов	v2.0
Парсинг multipart	Автоматическое извлечение загруженных файлов	v2.0
🔧 Улучшения
Улучшена обработка ошибок во всех CGI-скриптах

Добавлен индикатор прогресса для загрузки файлов

Автоматическая очистка старых бэкапов (хранятся последние 10)

Отладочное логирование для диагностики проблем

Улучшенная настройка UART

Поддержка нескольких устройств хранения (SD, USB, внутренняя память)

🐛 Исправленные ошибки
Исправлена обработка POST-данных в CGI-скриптах

Исправлен парсинг multipart/form-data

Исправлены проблемы с правами на файлы

Исправлена конфигурация автозапуска

Исправлены CORS-проблемы с отдельным портом

Обновление с версии v1.x
Если у вас уже установлена предыдущая версия, обновитесь с помощью:

bash
# 1. Сделайте резервную копию текущей конфигурации
cp /etc/door_keys.conf /root/door_keys.conf.bak
cp -r /etc/baresip /root/baresip.bak

# 2. Скачайте новые файлы
wget -O /tmp/intercom.tar.gz https://github.com/OpenIPC/intercom/archive/main.tar.gz
tar -xzf /tmp/intercom.tar.gz -C /tmp

# 3. Обновите веб-файлы
cp -r /tmp/intercom-main/cgi-bin/* /var/www/cgi-bin/
chmod +x /var/www/cgi-bin/p/*.cgi

# 4. Добавьте новые скрипты
cp /tmp/intercom-main/scripts/check_temp_keys.sh /usr/bin/
chmod +x /usr/bin/check_temp_keys.sh

# 5. Настройте cron для временных ключей
echo "0 * * * * /usr/bin/check_temp_keys.sh" >> /etc/crontabs/root

# 6. Запустите HTTP-сервер для бэкапов
httpd -p 8080 -h /var/www &
echo 'httpd -p 8080 -h /var/www &' >> /etc/rc.local

# 7. Обновите header.cgi (добавьте пункт меню Backups)
# Отредактируйте /var/www/cgi-bin/p/header.cgi вручную

# 8. Перезапустите сервисы
/etc/init.d/S99door restart
/etc/init.d/S97baresip restart
Лицензия
Лицензия MIT - свободно используйте и модифицируйте!

Copyright (c) 2026 OpenIPC Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Авторы
OpenIPC Team - Начальная разработка и интеграция SIP

Участники сообщества - Новые функции, исправления ошибок, переводы

Хотите внести вклад? Не стесняйтесь:

Отправлять pull request'ы

Сообщать об ошибках

Предлагать новые функции

Улучшать документацию

Переводить на другие языки

⭐ Поставьте звезду этому репозиторию, если он оказался полезен!

Удачной сборки! 🚀
