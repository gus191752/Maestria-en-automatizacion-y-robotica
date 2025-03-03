/* Programa de cruce por cero SIN LIBRERIA hecho en clase 1/3/2025 */
volatile int i=0;               // variable contador
volatile boolean cruce_cero=0;  // variable cruce cero
#define triac 3                 // salida del moc 3021
#define AD A0                   // entrada analofica
int dim=0;                      // on= 0 , 83=off
int POT=0;                      // variable para A/D
int filteredPOT=0;              // valor filtrado para potenciometro

void setup() 
{
  //serial.begin(9600);
pinMode(triac, OUTPUT);          // configura como salida
pinMode(AD, INPUT);              // configura como entrada
pinMode(2,INPUT);
attachInterrupt(digitalPinToInterrupt(2),deteccion_cruce_cero, RISING);  // detecta la interrupcion por cambio de estado flanco de subida INT0 es el mismo pin PD2
noInterrupts();         // deshabilita las interrupciones mientras se configura
TCCR1A= 0;              // limpia los registros
TCCR1B= 0;              // limpia los registros
TCNT1=  0;              // Inicializa el contador del timer1 a cero
OCR1A= 0x50;            // Valor de comparacion es 80 y en hexadecimal es 0x50
TCCR1B=0b0001001;       // modo CTC (clear timer on compare match) WGM12=1 CS10=1 -> pre-escaler 1 -> 16Mhz/1  T= 63 nanoseg x 80 = 5 useg CADA INTERRUPCION
TCCR1A=0b0000000;       // para que el modo ctc funcione todo el bit debe ser cero
TIMSK1=0b0000010;       // OCIE1A=1   // habilita las interrupciones
interrupts();           // habilita las interrupciones mientras se configura
}

ISR(TIMER1_COMPA_vect)   // funcion del microcontrolador, ver el datasheet
{
  Dimer();
}

void deteccion_cruce_cero()    // si existe cruce por cero entoces ejecuto el codigo
{                              // resenteando el valo de i y apago el triac
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
dim = map(filteredPOT,0,1023,0,83);        // mapea el valor a un rango de 0 a 83
dim= constrain(dim,0,83);                  // asegura que dim este dentro del rango
}

