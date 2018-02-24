
from time import sleep                  #preambolo
from subprocess import call             #importazione delle librerie
import signal, sys, pygame, MPR121      
import RPi.GPIO as GPIO                 #chiamo RPi.gpio solo GPIO per comodità


print "Setting UP!"              #printa a schermo setting up

try:
  sensor = MPR121.begin()       #fa partire la funzione MPR121 e la chiamiamo sensor
except Exception as e:          #se non c'è un errore
  print e
  sys.exit(1)                   #esci dal programma.  (in caso di bugs)

num_electrodes = 12             #mettiamo in una variabile il numero degli elettrodi per comodità

# sensibilità al tocco - abbassando questo valore diventa più come un sensore di prossimità (di default è 40)
touch_threshold = 6

# questa è la sensibilità al rilascio - DEVE sempre essere PIU PICCOLO della sensibilità al tocco (default è 20)
release_threshold = 3

print "Setting thresholds!"              #printa questa stringa
sensor.set_touch_threshold(touch_threshold)           #vengono attribuiti i valori di sensibilità da noi decisi
sensor.set_release_threshold(release_threshold)

#questo è un blocco che ci permette di uscire dal programma (ctrl + C) e spegne i LED (i led verrano spiegati giusto qua sotto)
def signal_handler(signal, frame):
  light_rgb(0, 0, 0)
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#settaggio dei LED sui gpio del raspi (non cambiare questi valori, sono di default), sono i valori BCM
red_led_pin = 6
green_led_pin = 5
blue_led_pin = 26


print "Setting GPIO!"
def light_rgb(r, g, b):
  # Stiamo invertendo i valori poiché sul picap
  # LOW = on
  # HIGH = off
  GPIO.output(red_led_pin, not r)            #quindi si accenderà il LED seguito da "not"
  GPIO.output(green_led_pin, not g)
  GPIO.output(blue_led_pin, not b)

GPIO.setmode(GPIO.BCM)                    #ancora settaggio per i LED in BCM
GPIO.setwarnings(False)

GPIO.setup(red_led_pin, GPIO.OUT)        #dice ai GPIO del raspi che i gpio dei LED devono essere di OUTPUT
GPIO.setup(green_led_pin, GPIO.OUT)
GPIO.setup(blue_led_pin, GPIO.OUT)

print "Inizialize pygame Libary!"         #initializza la libreria pygame.mixer che si occupa della gestione dei file audio
pygame.mixer.pre_init(frequency = 44100, channels = 64, buffer = 1024)
pygame.mixer.init()


print "Charging sound objects!"                    #carica i file audio, formato ".ogg"
sound0 = pygame.mixer.Sound("/home/pi/Desktop/panchina/test.ogg")     #test è il primo suono che sentiamo che ci indica che tutto è andato a buon fine
sound1 = pygame.mixer.Sound("/home/pi/Desktop/panchina/c.ogg")
sound2 = pygame.mixer.Sound("/home/pi/Desktop/panchina/b.ogg")
sound3 = pygame.mixer.Sound("/home/pi/Desktop/panchina/v.ogg")
sound0.play(loops = 0)               # 0 è il numero di volte che deve essere ripetuto il suono, questo è il suono di accensione quindi basta riprodurlo una volta
sound1.play(loops = -1)              # -1 indica che il suono deve essere ripetuto infinite volte
sound2.play(loops = -1)
sound3.play(loops = -1)
sound0.set_volume(1.0)               # si mette al massimo il volume dell'audio test
sound1.set_volume(0.0)               # e al minimo tutti gli altri (poiché dovranno essere suonati solo quando si avvicina un conduttore)
sound2.set_volume(0.0)
sound3.set_volume(0.0)

print "c.ogg playing silentily"              #Printa a schermo che i suoni sono riprodotti a volume minimo
print "b.ogg playing silentily"
print "v.ogg playing silentily"
print "Lift OFF, Major Tom!"
print "CTRL + c to touchdown!"
while True:
  if sensor.touch_status_changed():
    sensor.update_touch_data()
    is_any_touch_registered = False

    for i in range(num_electrodes):
      if sensor.get_touch_data(i):
    #chiede alla funzione se è stata toccata un piastra per giostrare i LED
        is_any_touch_registered = True

    #dice di accendere il LED rosso se è stata toccata una piastra
    if is_any_touch_registered:
      light_rgb(1, 0, 0)
    else:
      light_rgb(0, 1, 0)                #accende il verde se non è stata attivata la piastra
    if sensor.is_new_touch(10):         #se il sensore 10 è stato attivato
      print "10 Go!"
      sound1.set_volume(1.0)            #setta il volume al massimo
    elif sensor.is_new_release(10):     #e se il sensore 10 è stato rilasciato
      sound1.set_volume(0.0)            #setta il volume al minimo
    if sensor.is_new_touch(11):
      print "11 Go!"
      sound3.set_volume(1.0)
    elif sensor.is_new_release(11):
      sound3.set_volume(0.0)
    if sensor.is_new_touch(9):
      print "12 Go!"
      sound2.set_volume(1.0)
    elif sensor.is_new_release(9):
      sound2.set_volume(0.0)
  # sleep a bit
  sleep(0.01)
