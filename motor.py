import time
import sys
import RPi.GPIO as GPIO
from ultrasonic import distance
#设置GPIO模式为BCM编码模式
GPIO.setmode(GPIO.BCM)
#定义 GPIO 引脚
GPIO_IN1 = 14
GPIO_IN2 = 15
GPIO_IN3 = 18
GPIO_IN4 = 23
ENA = 7
ENB = 8
run_flag = 1 #当前运动状态标志
pre_run_flag =0 #上一次运动状态标志

GPIO.setwarnings(False)
#设置 GPIO 的工作方式 (IN / OUT)
GPIO.setup(GPIO_IN1, GPIO.OUT)
GPIO.setup(GPIO_IN2, GPIO.OUT)
GPIO.setup(GPIO_IN3, GPIO.OUT)
GPIO.setup(GPIO_IN4, GPIO.OUT)
GPIO.setup(ENA,GPIO.OUT)
GPIO.setup(ENB,GPIO.OUT)

#PWM频率设置，单位Hz
p1 = GPIO.PWM(ENA, 10) 
p2 = GPIO.PWM(ENB, 10) 
#设置p1和p2的占空比为41%和45%，并发送PWM波
p1.start(41)
p2.start(45)
def forward():
    GPIO.output(GPIO_IN1,False)
    GPIO.output(GPIO_IN2,True)
    GPIO.output(GPIO_IN3,True)
    GPIO.output(GPIO_IN4,False)
def backward():
    GPIO.output(GPIO_IN1,True)
    GPIO.output(GPIO_IN2,False)
    GPIO.output(GPIO_IN3,False)
    GPIO.output(GPIO_IN4,True)

def turnLeft():
    GPIO.output(GPIO_IN1,True)
    GPIO.output(GPIO_IN2,False)
    GPIO.output(GPIO_IN3,True)
    GPIO.output(GPIO_IN4,False)

def turnRight():
    GPIO.output(GPIO_IN1,False)
    GPIO.output(GPIO_IN2,True)
    GPIO.output(GPIO_IN3,False)
    GPIO.output(GPIO_IN4,True)

def pause():
    GPIO.output(GPIO_IN1,True)
    GPIO.output(GPIO_IN2,True)
    GPIO.output(GPIO_IN3,True)
    GPIO.output(GPIO_IN4,True)

def forward_avoid_obstacle():
    '''前进并避障函数
    遇到障碍物时先后退再左转'''
    dist = distance()
    print("Measured Distance = {:.2f} cm".format(dist))
    if(dist < 25 ):
        backward()
        #延时0.2s
        time.sleep(0.2)
        #改变占空比百分值
        p1.ChangeDutyCycle(41)#50
        p2.ChangeDutyCycle(48)#57
        turnLeft()
        time.sleep(0.2)
        return
    else:
        p1.ChangeDutyCycle(31)#41
        p2.ChangeDutyCycle(35)#48
        forward()
    time.sleep(0.08)


def motion_ctrol(child_pipe):
    '''方向控制函数
    如果改变转动方向，则转动一定角度后又继续直走并且避障
    '''
    global run_flag
    global pre_run_flag 
    pause()
    print("motion ctrol started")
    try:
        while 1:
            #try:
                # print(share_state.value)
                #if child_conn.poll():
                #temp = child_que.get_nowait()
                #run_flag = temp 
                #   print(child_conn.recv())
                   #print(run_flag)
            #except:
                #pass
                
            #返回是否有可供读取的数据
            if child_pipe.poll():
                run_flag = child_pipe.recv()
            #if share_state.value != -1:
            #    run_flag = share_state.value
            #    print("signal accepted")
            #    share_state.value = -1
            #如果之前暂停现在仍然暂停就跳过本次循环
            if pre_run_flag == 0 and pre_run_flag == run_flag:
               continue 
            if run_flag == 0:
                pause()
                print("pause")
            elif run_flag == 1:
                forward_avoid_obstacle()
                print('move forward')
            elif run_flag == 2:
                turnLeft()
                time.sleep(1)
                print("turn left")
                pause()
                time.sleep(1)
                run_flag = 1
            elif run_flag == 3:
                turnRight()
                time.sleep(1)
                print("turn right")
                pause()
                time.sleep(1)
                run_flag = 1
            pre_run_flag = run_flag
    # exit by pressing CTRL + C
    except KeyboardInterrupt:
        p1.stop()#使能端PWM波停止，电机停止
        p2.stop()
        print("Measurement stopped by User")
        GPIO.cleanup()#清空GPIO数据
        sys.exit(0)
