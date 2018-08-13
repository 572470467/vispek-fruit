import RPi.GPIO as GPIO
import time
from bottle import route, run, template
#from drivers import *
#from subprocess import call
import subprocess

mto = [27, 18, 25, 19]
mtr = [17, 23, 24,26]
ss = [12, 16, 20, 21]


class HX711:
    def __init__(self, psck, pdt):
        GPIO.setup(psck, GPIO.OUT, initial = 0)
        GPIO.setup(pdt, GPIO.IN)
        self.psck = psck
        self.pdt = pdt
        
    def read(self):
        d = 0
        while GPIO.input(self.pdt)==1:
            pass
        for i in range(24):
            GPIO.output(self.psck, 1)
            GPIO.output(self.psck, 0)
            d = (d << 1) | GPIO.input(self.pdt)
            #GPIO.output(psck, 0)
        GPIO.output(self.psck, 1)
        GPIO.output(self.psck, 0)
        return d

def read_ss():
    for pin in ss:
        print(GPIO.input(pin))

def reset_motor(mid):
    for pinid in mid:
        GPIO.setup(mtr[pinid], GPIO.OUT, initial=0)
    st = time.time()
    nzero = 0
    while (nzero < len(mid) and time.time() - st < 1):
        nzero = 0
        for pinid in mid:
            if (GPIO.input(ss[pinid])==0):
                nzero = nzero + 1
                GPIO.setup(mtr[pinid], GPIO.IN)
                GPIO.setup(mtr[pinid], GPIO.IN)
        time.sleep(0.0001)

def operate_motor(mid, t=0.2):
    for pinid in mid:
        GPIO.setup(mto[pinid], GPIO.OUT, initial=0)
    time.sleep(t)
    for pinid in mid:
        GPIO.setup(mto[pinid], GPIO.IN)
    time.sleep(0.1)
    
def fall():
    start_time = time.time()
    
    proc = subprocess.Popen('ssh pi@192.168.0.115 /home/pi/nsdrv-kompline/NSSPIService', shell=True)
    
    operate_motor([2], 0.5)
    time.sleep(0.1)
    reset_motor([2])

    operate_motor([1], 0.4)
    time.sleep(0.1)
    reset_motor([1])

    operate_motor([0], 0.37)
    time.sleep(0.1)
    reset_motor([0])
    
    print(time.time()-start_time)

def rotate_by_time(pin_motor, t):
    GPIO.setup(pin_motor, GPIO.OUT, initial=0)
    time.sleep(t)
    GPIO.setup(pin_motor, GPIO.IN)
    
if __name__=='__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(mto, GPIO.IN)
    GPIO.setup(mtr, GPIO.IN)
    GPIO.setup(ss, GPIO.IN)

    ws0 = HX711(3, 2)
    ws1 = HX711(9, 10)

    # rotate_by_time(17, 0.35)
    # rotate_by_time(27, 0.35)
    @route('/hello')
    def index():
        fall()
        return 'weight: %d %d\n'%(ws0.read(), ws1.read())

    
    @route('/repeat/<nrep>')
    def repeatfall(nrep):
        s = ''
        for i in range(int(nrep)):
            fall()
            s = s + 'weight: %d %d\n'%(ws0.read(), ws1.read())
        return s
    
    run(host='0.0.0.0', port=8080)

