/* Programa de cruce por cero hecho en clase 1/3/2025 */

#include <TimerOne.h>           // libreria especializada en interrpciones del timer1
volatile int i=0;               // variable contador
volatile boolean cruce_cero=0;  // variable cruce cero
#define triac 3                 // salida del moc 3021
#define AD A0                   // entrada analogica
int dim=0;                      // on= 0 , 83=off
int T_int = 10;                 // tiempo para interrupciones en useg es 100, se coloca 10 para poder simularlo
//int T_int = 100;              // en una placa real utilizar este valor
int POT=0;                      // variable para A/D
int filteredPOT=0;              // valor filtrado para potenciometro

void setup() {
  //serial.begin(9600);
pinMode(triac, OUTPUT);                           // configura como salida
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
}

void Dimer()
{
  if (cruce_cero==true)  // si la bandera esta activa
  {
    if (i>=dim)                 // si i es menor que el valor setpoint  mantiene el triac apagado y aumenta el contador i
    {                           // si i supera al set point dim activa el triac hasta el final del bucle y desactiva la bandera
      digitalWrite(triac,HIGH);
      i=0;
      cruce_cero=false;
    }
    else
    {
      i++;
    }
  }
}

void loop() 
{
POT= analogRead(AD);
filteredPOT= (0.9*filteredPOT + 0.1*POT);      // filtro de suavizado
dim = map(filteredPOT,0,1023,0,83);            // mapea el valor a un rango de 0 a 83
dim= constrain(dim,0,83);                      // asegura que dim este dentro del rango
}

