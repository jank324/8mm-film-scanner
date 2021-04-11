import RPi.GPIO as GPIO

PIN_A, PIN_B = 23, 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_A, GPIO.IN)
GPIO.setup(PIN_B, GPIO.IN)

counter = 0

def encoder():
    global counter
    if GPIO.input(PIN_B) == GPIO.HIGH:
        counter += 1
    else:
        counter -= 1
    print("INTERUPT")

GPIO.add_event_detect(PIN_A, GPIO.FALLING, callback=encoder)

while(counter < 1200):
    a = 0

GPIO.cleanup()