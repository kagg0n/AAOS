#Auto Avoiding Obstacles System (AAOS beta version)

#******LIBRARIES******
from time import sleep
from machine import PWM,I2C
import VL53L0X
from machine import Pin,UART

#******VARIABLES******
rangingPosition = 0
rangingPosition_reverse = 5

distanceArray = []
actuationDistance = 200 # растояние при котором сработает поворот в сторону ( единица измерения ?)

drivingMode = 0 # режим езды: 0 - резкий поворот направо; 1-плавный поворот направо; 2-езда по центру; 3-плавный поворот налево; 4-резкий поворот налево

pwm = PWM(Pin(6)) # управляющий пин сервопривода
pwm.freq(50)
#******INIT******
i2c = I2C(1,scl=Pin(3), sda=Pin(2), freq=1000000) #пины лазерного дальномера
tof = VL53L0X.VL53L0X(i2c)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)

#uart = UART(0,9600,rx=Pin(17),tx=Pin(16)) # пины bluetooth модуля

#******MAIN CODE******
def distanceRanging():
    #Tech.info:1000-6000 диапазон,необходимый для лидара;50 пунктов-1 градус вращения
    # делаем 5 измерений и записываем их в список
    for rotation_angle in range(1000,6000,1000):
        pwm.duty_u16(rotation_angle)
        
        tof.start()
        tof.read()
        global rangingPosition
        distanceArray.insert(rangingPosition,(tof.read() ) )
        
        rangingPosition = rangingPosition + 1
        
        tof.stop()
        
    theBestRoad()
    #print(distanceArray)
    distanceArray.clear()
    
    for rotation_angle in range(6000,1000,-1000):
        pwm.duty_u16(rotation_angle)
        
        tof.start()
        tof.read()
        global rangingPosition_reverse
        rangingPosition_reverse = rangingPosition_reverse - 1
        

        distanceArray.insert(rangingPosition_reverse,(tof.read() ) )
        
        tof.stop()
        
    theBestRoad()
    
    distanceArray.clear()
    
    rangingPosition = 0
    rangingPosition_reverse = 5
    
def theBestRoad():
    # изначально выбираем лучшую сторону движения
    # Пометка: 0 и 1 элементы - правая сторона, 2 элемент - центр(приоритет), 3 и 4 элемент - левая сторона
    global distanceArray
    global actuationDistance
    if (distanceArray[0] + distanceArray[1]) - (distanceArray[3] + distanceArray[4]) >= actuationDistance:
        if (distanceArray[0] - distanceArray[1]) >= 20: # нужно откалибровать значение
            global drivingMode
            drivingMode = 0
        else:
            global drivingMode
            drivingMode = 1
            
            
    elif (distanceArray[3] + distanceArray[4]) - (distanceArray[0] + distanceArray[1]) >= actuationDistance:
        if (distanceArray[4] - distanceArray[3]) >= 20: # калибровка значения
            global drivingMode
            drivingMode = 4
        else:
            global drivingMode
            drivingMode = 3
            
            
    else:
        global drivingmode
        drivingMode = 2
            
while True:
    distanceRanging()
    print(drivingMode)