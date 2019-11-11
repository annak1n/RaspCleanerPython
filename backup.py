import RPi.GPIO as GPIO
import time
import read_RPM
import threading
import setup_robo
import sys
from Gyro_new import Gyro
#from mpu6050 import mpu6050

class Control_robo:

    def __init__(self, encoder_1, encoder_2, SAMPLE_TIME, motor_1, motor_2):

        self.encoder_1 = encoder_1
        self.encoder_2 = encoder_2
        self.SAMPLE_TIME = SAMPLE_TIME
        self.motor_1 = motor_1  ##LEFT MOTOR
        self.motor_2 = motor_2  ##RIGHT MOTOR
        
        self.p = GPIO.PWM(self.motor_1.enable, 1000)
        self.p2 = GPIO.PWM(self.motor_2.enable, 1000)
        self.p.start(25)
        self.p2.start(25)
        self.duty_1_value = 15
        self.duty_2_value = 15
        self.TARGET = 80 # USE ONLY WITH PID ENCODER CONTROL
        self.TARGET_1 = 80 #USE WITH PID ENCODER + GYRO CONTROL
        self.TARGET_2 = 80 #USE WITH PID ENCODER + GYRO CONTROL
        self.TARGET_ANGLE = 0 # USE WITH PID ENCODER + GYRO CONTROL
        self.select = 'p'
        self.gyro = Gyro()
        self.gyro.calibration()


     
    def background_2(self):

        def run_2(self):
            print("Starting Thread 2")
            thread2 = threading.Thread(target = pid_angle, args =(self,))
            thread2.daemon = True
            thread2.start()

        def pid_angle(self):

            ## PID ANGLE DATA
            #KP = 0.0032
            #KD = 0.0008
            #KI = 0.00002

            #KI MELHORES VALORES ATE AGORA
            '''
            KP = 0.0032
            KD = 0.0008
            KI = 0.00002
            '''

            ##KI 0.00010

            error_prev = 0
            sum_z = 0

            ## PID RPM DATA
            KPr = 0.05
            KDr = 0.03
            KIr = 0.0005

            e1_prev = 0
            e2_prev = 0
            e1_sum = 0
            e2_sum = 0

            while True:

                print("\n")
                ##READ GYRO's DATA
                angle_data = self.gyro.reading()
                data_x = angle_data['x']
                data_y = angle_data['y']
                data_z = angle_data['z'] ##DATA POSITIVO PARA DIREITA
                #print("data: ", data_z)


                ## CALCULATE ERROR FOR ANGLE DATA
                error_z = self.TARGET_ANGLE - data_z ##ERROR NEGATIVO DOBRANDO PRA DIREITA
                diff_z = (error_z - error_prev)/0.02
                print("error: ", error_z)

                ## CALL FOCUS FUNCTION TO FIND THE WAY IF TOO LOST
                #if error_z > 55 or error_z < -55:
                 #   while True:
                  #      exit = focus(self) ## TRY IT?

                ##READ ENCODERS DATA
                RPM_1 = self.encoder_1.RPM()
                RPM_2 = self.encoder_2.RPM()

                ## CALL DIRECTION FUNCTION WITH PID TO ANGLE CONTROL
                direction(self, error_z, diff_z, sum_z)

                '''
                if error_z > 0 and self.TARGET_2 > 80:
                    self.TARGET_2 = 80 - (error_z * KP) - (diff_z * KD) #- (sum_z * KI) #DISCART SUM TO TRANSITIONS
                    print("codiçao 1")
                elif error_z > 0 and self.TARGET_2 <= 80:
                    self.TARGET_2 = self.TARGET_2 - (error_z * KP) - (diff_z * KD) - (sum_z * KI)
                    print("condicao 2")
                elif error_z < 0 and self.TARGET_2 <= 80:
                    self.TARGET_2 = 80 - (error_z * KP) - (diff_z * KD) #- (sum_z * KI) #DISCART SUM TO TRANSITIONS
                    print("condicao 3")
                elif error_z < 0 and self.TARGET_2 > 80:
                    self.TARGET_2 = self.TARGET_2 - (error_z * KP) - (diff_z * KD) - (sum_z * KI)
                    print("condicao 4")
                '''

                self.TARGET_2 = max(min(250, self.TARGET_2), 50)

                


                ## CALCULATE ERROR FOR RPM DATA
                if RPM_1 < 600:
                    RPM_1_error = self.TARGET_1 - RPM_1 ##WILL TRY TO BE ARROUND 100
                    e1_diff = (RPM_1_error - e1_prev) ## DERIVATIVE ERROR
                if RPM_2 < 600:
                    RPM_2_error = self.TARGET_2 - RPM_2 ##WILL TRY TO STABILIZE ANGLE
                    e2_diff = (RPM_2_error - e2_prev)

                ##DERIVATIVE ERROR FOR RPM
                #e1_diff = (RPM_1_error - e1_prev)
                #e2_diff = (RPM_2_error - e2_prev)

                if self.select in ('w', 's', 't', 'y', 'h','l','m'):
                    self.duty_1_value = self.duty_1_value + (RPM_1_error * KPr) + (e1_diff * KDr) + (e1_sum * KIr)
                    self.duty_2_value = self.duty_2_value + (RPM_2_error * KPr) + (e2_diff * KDr) + (e2_sum * KIr)
                if self.select == 'p':
                    self.duty_1_value = 10
                    self.duty_2_value = 10
                #elif self.select in ('d', 'h', 'l', 'm'):
                #    self.duty_1_value = self.duty_1_value + (RPM_1_error * KP) + (e1_diff * KD) + (e1_sum * KI)
                #elif self.select in ('a', 'h','l','m'):
                #    self.duty_2_value = self.duty_2_value + (RPM_2 * KP) + (e2_diff * KD) + (e2_sum * KI)
                

                self.duty_1_value = max(min(100,self.duty_1_value), 0)
                self.duty_2_value = max(min(100,self.duty_2_value),0)

                print("RPM 1: ", RPM_1)
                print("RPM 2: ", RPM_2)
                print("DUTY VALUE: ", self.duty_1_value)
                print("DUTY VALUE 2: ", self.duty_2_value)
                print("SOMA: ", round(sum_z,3))
                print("DIFF: ", round(diff_z,3))
                print("TARGET 2: ", self.TARGET_2)


                ## CHANGE DUTY CYCLE VALUES
                self.p.ChangeDutyCycle(self.duty_1_value)
                self.p2.ChangeDutyCycle(self.duty_2_value)

                #time.sleep(self.SAMPLE_TIME/10)
                if self.select != 'p':
                    error_prev = error_z
                    sum_z += error_z

                ## ENCODERS NEW ERRORS DATA
                    e1_prev = RPM_1_error
                    e2_prev = RPM_2_error

                    e1_sum += RPM_1_error
                    e2_sum += RPM_2_error

        def direction(self, error_z, diff_z, sum_z):

            ## PID ANGLE DATA
            KP = 0.0032
            KD = 0.0008
            KI = 0.00002

            if self.select == 'w':
                if error_z > 0 and self.TARGET_2 > 80:
                    self.TARGET_2 = 80 - (error_z * KP) - (diff_z * KD) #- (sum_z * KI) #DISCART SUM TO TRANSITIONS
                    print("codiçao 1")
                elif error_z > 0 and self.TARGET_2 <= 80:
                    self.TARGET_2 = self.TARGET_2 - (error_z * KP) - (diff_z * KD) - (sum_z * KI)
                    print("condicao 2")
                elif error_z < 0 and self.TARGET_2 <= 80:
                    self.TARGET_2 = 80 - (error_z * KP) - (diff_z * KD) #- (sum_z * KI) #DISCART SUM TO TRANSITIONS
                    print("condicao 3")
                elif error_z < 0 and self.TARGET_2 > 80:
                    self.TARGET_2 = self.TARGET_2 - (error_z * KP) - (diff_z * KD) - (sum_z * KI)
                    print("condicao 4")

            if self.select == 's':
                if error_z > 0 and self.TARGET_2 > 80:
                    self.TARGET_2 = 80 + (error_z * KP) + (diff_z * KD) #- (sum_z * KI) #DISCART SUM TO TRANSITIONS
                    print("codiçao 1")
                elif error_z > 0 and self.TARGET_2 <= 80:
                    self.TARGET_2 = self.TARGET_2 + (error_z * KP) + (diff_z * KD) + (sum_z * KI)
                    print("condicao 2")
                elif error_z < 0 and self.TARGET_2 <= 80:
                    self.TARGET_2 = 80 + (error_z * KP) + (diff_z * KD) #- (sum_z * KI) #DISCART SUM TO TRANSITIONS
                    print("condicao 3")
                elif error_z < 0 and self.TARGET_2 > 80:
                    self.TARGET_2 = self.TARGET_2 + (error_z * KP) + (diff_z * KD) + (sum_z * KI)
                    print("condicao 4")





        def focus(self):
            ########### STOP ALL MOTORS ##########
            self.p.ChangeDutyCycle(0)
            self.p2.ChangeDutyCycle(0)
            ## RETURN FALSE IF OK

            #### AXIS ROTATION TO FIND THE WAY ####
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.HIGH)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.HIGH)

            angle_data = self.gyro.reading()
            data_z = angle_data['z']
            #print("TO NA ANGLE DATA: ", data_z)
            RPM_1 = self.encoder_1.RPM()
            RPM_2 = self.encoder_2.RPM()

            i = 0
            while RPM_1 < 20 and RPM_2 < 20:
                
                duty_value = max(min(50,i),0)
                print("duty p1: ", duty_value)
                self.p.ChangeDutyCycle(duty_value)
                self.p2.ChangeDutyCycle(duty_value)
                RPM_1 = self.encoder_1.RPM()
                RPM_2 = self.encoder_2.RPM()
                i = i+1
                time.sleep(0.5) ## MUDAR ISSO POIS IMPEDE O GYRO READING (CRIAR THREAD PRA LER ANGULO?)

            angle_data = self.gyro.reading()
            data_z = angle_data['z']
            print("DATA Z: ", data_z)
            if data_z < 30 or data_z > -30:
                return False
            else:
                return True

        run_2(self)


    def set_speed(self, x):
        temp1 = 1
        #if x!= 'h' or x!='m' or x!='l':
        self.select = x
        if x == 'r':
            print("run")
            if (temp1 == 1):
                ##LEFT MOTOR
                GPIO.output(self.motor_1.in1, GPIO.HIGH)
                GPIO.output(self.motor_1.in2, GPIO.LOW)
                ##RIGHT MOTOR
                GPIO.output(self.motor_2.in1, GPIO.HIGH)
                GPIO.output(self.motor_2.in2, GPIO.LOW)
                print("forward")

                x = 'z'
            else:
                ##LEFT MOTOR
                GPIO.output(self.motor_1.in1, GPIO.LOW)
                GPIO.output(self.motor_1.in2, GPIO.HIGH)
                ##RIGHT MOTOR
                GPIO.output(self.motor_2.in1, GPIO.LOW)
                GPIO.output(self.motor_2.in2, GPIO.HIGH)
                print("backward")
                temp1 = 0 
                x = 'z'


        elif x == 'p':
            print("stop")
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.LOW)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.LOW)
            self.duty_1_value = 10
            self.duty_2_value = 10
            self.select = 'p'
            x='z'

        elif x == 'w':
            #print("forward")
            self.gyro.calibration()
            self.duty_1_value = self.duty_1_value 
            self.duty_2_value = self.duty_2_value 
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.HIGH)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.HIGH)
            GPIO.output(self.motor_2.in2, GPIO.LOW)

            temp1 = 1
            x = 'z'
            self.select = 'w'

        elif x == 's':
            print("backward")
            
            #self.gyro.calibration()
            self.duty_1_value = self.duty_1_value
            self.duty_2_value = self.duty_2_value 
          
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.LOW)
            GPIO.output(self.motor_1.in2, GPIO.HIGH)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.HIGH)
            temp1 = 0
            x = 's'
            self.select = 's'
            
        elif x == 'd':
            print("turn right")
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.HIGH)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.LOW)
            x='z'
            
        elif x == 'a':
            print("turn left")
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.LOW)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.HIGH)
            GPIO.output(self.motor_2.in2, GPIO.LOW)
            x='z'
        
        elif x == 'y':
            print("axis rotation right")
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.HIGH)
            GPIO.output(self.motor_1.in2, GPIO.LOW)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.LOW)
            GPIO.output(self.motor_2.in2, GPIO.HIGH)
        
        elif x == 't':
            print("axis rotation left")
            ##LEFT MOTOR
            GPIO.output(self.motor_1.in1, GPIO.LOW)
            GPIO.output(self.motor_1.in2, GPIO.HIGH)
            ##RIGHT MOTOR
            GPIO.output(self.motor_2.in1, GPIO.HIGH)
            GPIO.output(self.motor_2.in2, GPIO.LOW)
        
        elif x == 'l':
            print("low")
            #self.p.ChangeDutyCycle(25)
            #self.p2.ChangeDutyCycle(25)
            self.TARGET = 80
            x = 'z'

        elif x == 'm':
            print("medium")
            #self.p.ChangeDutyCycle(50)
            #self.p2.ChangeDutyCycle(50)
            self.TARGET = 200
            x = 'z'

        elif x == 'h':
            print("high")
            #self.p.ChangeDutyCycle(100)
            #self.p2.ChangeDutyCycle(100)
            self.TARGET = 300
            x = 'z'
        else:
            print("<<<  wrong data  >>>")