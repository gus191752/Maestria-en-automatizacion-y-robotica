/* Programa de cruce por cero hecho en clase 1/3/2025 */

#include <TimerOne.h>           // libreria especializada en interrpciones del timer1
volatile int i=0;               // variable contador
volatile boolean cruce_cero=0;  // variable cruce cero
#define triac 3                 // salida del moc 3021
#define led 13
#define AD A0                   // entrada analogica
int dim=0;                      // on= 0 , 83=off
int T_int = 100;                 // tiempo para interrupciones en useg es 100, se coloca 10 para poder simularlo
//int T_int = 100;              // en una placa real utilizar este valor
int POT=0;                      // variable para A/D
int MOT=0;
int temperatura=0;              // temperatura con DH22
String dato;
int pos;
String label;
String valor;
int filteredPOT=0;              // valor filtrado para potenciometro

void setup() {
Serial.begin(9600);
pinMode(triac, OUTPUT);                           // configura como salida
pinMode(led, OUTPUT);  
pinMode(AD, INPUT);                               // configura como entrada
attachInterrupt(0,deteccion_cruce_cero, RISING);  // detecta la interrupcion por cambio de estado flanco de subida INT0 es el mismo pin PD2
Timer1.initialize(T_int);                         // inicia la libreria con el tiempo
Timer1.attachInterrupt(Dimer, T_int);             // en cada interrupcion ejecuta el codigo del dimer cada 100 useg

}

void deteccion_cruce_cero()    // si existe cruce por cero entoces ejecuto el codigo
{                              // resenteando el valor de i y apago el triac
cruce_cero=true;               // actica la bandera
i=0;
digitalWrite(triac,LOW);
digitalWrite(led,LOW);
}

void Dimer()
{
  if (cruce_cero==true)  // si la bandera esta activa
  {
    if (i>=dim)                 // si i es menor que el valor setpoint  mantiene el triac apagado y aumenta el contador i
    {                           // si i supera al set point dim activa el triac hasta el final del bucle y desactiva la bandera
      digitalWrite(triac,HIGH);
      digitalWrite(led,HIGH);
      i=0;
      cruce_cero=false;
    }
    else
    {
      i++;
    }
  }
}

void actuador()
{
dato.trim();
dato.toLowerCase();
pos= dato.indexOf(':');
label= dato.substring(0,pos);
valor= dato.substring(pos+1);
if (label.equals("mot"))
  {
    if (MOT != valor.toInt())
    {
      MOT=10*valor.toInt();
      //mot.write(POT);
    }
  }
}

void loop() 
{
  if (Serial.available())
  {
    dato=Serial.readString();
  }
actuador();
POT= analogRead(AD);
dim = map(MOT,0,1023,83,0);  // mapea el valor a un rango de 0 a 83      
Serial.println("pot:"+String(int(POT)));
}

