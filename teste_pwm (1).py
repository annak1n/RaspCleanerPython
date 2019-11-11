import RPi.GPIO as GPIO
from time import sleep
import read_RPM
import threading

in1 = 24
in2 = 23
in3 = 16
in4 = 26
en2 = 6
en = 25
temp1 = 1



##SETUP MODE LEFT SIDE
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
p = GPIO.PWM(en, 1000)

##SETUP RIGHT
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(en2, GPIO.OUT)
GPIO.output(in3, GPIO.LOW)
GPIO.output(in4, GPIO.LOW)
p2 = GPIO.PWM(en2, 1000)


##FUNCAO THREAD###############################################

def encoder():
    import read_RPM
    import pigpio
    
    RPM_GPIO = 4
    RPM_GPIO_2 = 17

    ##SETUP RPM MOTOR 1
    encoder_1 = pigpio.pi()
    rpm_1 = read_RPM.reader(encoder_1, RPM_GPIO)
    RPM1 = rpm_1.RPM()                              # VALOR DO RPM DO MOTOR 1
    ##SETUP RPM MOTOR 2
    encoder_2 = pigpio.pi()
    rpm_2 = read_RPM.reader(encoder_2, RPM_GPIO_2)       # VALOR DO RPM DO MOTOR 2
    RPM2 = rpm_2.RPM()
    ###PUXAR PRO WHILE A FUNC .RPM() E PRO SETUP O RESTO#
#
    while 1:
        print("RPM 1 : ", RPM1)
        print("RPM 2 : ", RPM2)
###############################################################

p.start(25)
p2.start(25)
print("\n")
print("The default speed & direction of motor is LOW & Forward.....")
print("r-run s-stop f-forward b-backward l-low m-medium h-high e-exit")
print("\n")

t = threading.Thread(target=encoder)
t.start()

while (1):

    x = input()


    if x == 'r':
        print("run")
        if (temp1 == 1):
            ##LEFT MOTOR
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.LOW)

            print("forward")
            x = 'z'
        else:
            ##LEFT MOTOR
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
            ##RIGHT MOTOR
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.HIGH)
            print("backward")
            x = 'z'


    elif x == 's':
        print("stop")
        ##LEFT MOTOR
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        ##RIGHT MOTOR
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)
        x = 'z'

    elif x == 'f':
        print("forward")
        ##LEFT MOTOR
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        ##RIGHT MOTOR
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)
        temp1 = 1
        x = 'z'

    elif x == 'b':
        print("backward")
        ##LEFT MOTOR
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
        ##RIGHT MOTOR
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)
        temp1 = 0
        x = 'z'
        
    elif x == 'd':
        print("turn right")
        ##LEFT MOTOR
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        ##RIGHT MOTOR
        GPIO.output(in3, GPIO.HIGH)
        GPIO.output(in4, GPIO.LOW)
        x='z'
        
    elif x == 't':
        print("turn left")
        ##LEFT MOTOR
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        ##RIGHT MOTOR
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)
        x='z'
    
    elif x == 'a':
        print("axis rotation")
        ##LEFT MOTOR
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
        ##RIGHT MOTOR
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.HIGH)
    
    
    elif x == 'l':
        print("low")
        p.ChangeDutyCycle(25)
        p2.ChangeDutyCycle(25)
        x = 'z'

    elif x == 'm':
        print("medium")
        p.ChangeDutyCycle(50)
        p2.ChangeDutyCycle(50)
        x = 'z'

    elif x == 'h':
        print("high")
        p.ChangeDutyCycle(100)
        p2.ChangeDutyCycle(100)
        x = 'z'


    elif x == 'e':
        t.kill()
        GPIO.cleanup()
        print("GPIO Clean up")
        break
    

    else:
        print("<<<  wrong data  >>>")
print("please enter the defined data to continue.....")


