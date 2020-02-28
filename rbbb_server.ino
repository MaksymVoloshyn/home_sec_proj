#include <EtherCard.h>
#include "DHT.h"
#define DHTPIN 6
#define PIN_TRIG 5
#define PIN_ECHO 4

DHT dht(DHTPIN, DHT11); //Инициация датчика
// ethernet interface mac address, must be unique on the LAN
static byte mymac[] = { 0x74,0x69,0x69,0x2D,0x30,0x31 };
static byte myip[] = { 192,168,10,202 };

byte Ethernet::buffer[500];
BufferFiller bfill;

static word homePage() {
  long duration, cm, cm_old;
  long t = millis() / 1000;
  word h = t / 3600;
  byte m = (t / 60) % 60;
  byte s = t % 60;
  
  // Сначала генерируем короткий импульс длительностью 2-5 микросекунд.
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(5);
  digitalWrite(PIN_TRIG, HIGH);
  // Выставив высокий уровень сигнала, ждем около 10 микросекунд. В этот момент датчик будет посылать сигналы с частотой 40 КГц.
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  //  Время задержки акустического сигнала на эхолокаторе.
  duration = pulseIn(PIN_ECHO, HIGH);
  // Теперь осталось преобразовать время в расстояние
  cm = (duration / 2) / 29.1;
  Serial.print("Расстояние до объекта: ");
  Serial.print(cm);
  Serial.println(" см.");

  long temp = dht.readTemperature(); //Измеряем температуру
  long hum = dht.readHumidity(); //Измеряем влажность
  if (isnan(hum) || isnan(temp)) {  // Проверка. Если не удается считать показания, выводится «Ошибка считывания», и программа завершает работу
    Serial.println("Ошибка считывания");
    return;
  }
  Serial.print("Влажность: ");
  Serial.print(hum);
  Serial.print(" %\t");
  Serial.print("Температура: ");
  Serial.print(temp);
  Serial.println(" *C "); //Вывод показателей на экран
  
  bfill = ether.tcpOffset();
  bfill.emit_p(PSTR(
    "HTTP/1.0 200 OK\r\n"
    "Content-Type: text/html\r\n"
    "Pragma: no-cache\r\n"
    "\r\n"
    "<meta http-equiv='refresh' content='5'/>"
    "<title>Home monitor</title>"
    "<h1>Arduino worked: <a class=tw>$D$D:$D$D:$D$D</a></h1>"
    "<h1>Distance to object = <a class=dis>$D</a>cm</h1>"
    "<h1>Temp = <a class=temp>$D$D</a> *C</h1>"
    "<h1>Hum = <a class=hum>$D$D</a> %</h1>"
    ), h/10, h%10, m/10, m%10, s/10, s%10, cm, temp, hum);
  return bfill.position();
}

void setup () {
  Serial.begin(9600);

  dht.begin(); // запуск dht датчика
  
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  
  Serial.println(F("\n[RBBB Server]"));
  // Change 'SS' to your Slave Select pin, if you arn't using the default pin
  if (ether.begin(sizeof Ethernet::buffer, mymac, SS) == 0)
    Serial.println(F("Failed to access Ethernet controller"));
  ether.staticSetup(myip);
  
}

void loop () {
  word len = ether.packetReceive();
  word pos = ether.packetLoop(len);

  if (pos)  // check if valid tcp data is received
    ether.httpServerReply(homePage()); // send web page data
}
