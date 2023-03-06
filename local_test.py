##from sensor_library import *

from main.write_temp import Temp_To_Txt as Parser

from average_test import ListTemp

import time

from multiprocessing import Process as proc

from multiprocessing import Value as val

import math

standardList = ListTemp(0)
injuredList = ListTemp(1)

def standardListInit(rolling,total,rolling_avg,led_status,button_status,servo_status):
    standardList.getRollingTemp(rolling,total,led_status,button_status,servo_status)
    ##print(standardList.rollinglist)
    ri = standardList.rollinglist

    standard_avg = 0

    for x in standardList.rollinglist:
        standard_avg += x

    
    rolling_avg.value = standard_avg/len(standardList.rollinglist)

def injuredListInit(rolling,total,rolling_avg,led_status,button_status,servo_status):
    injuredList.getRollingTemp(rolling,total,led_status,button_status,servo_status)
    injured_avg = 0

    for x in injuredList.rollinglist:
        injured_avg += x

    print(injured_avg)
    
    rolling_avg.value = injured_avg/len(injuredList.rollinglist)

def print_styled(led_status,button_status,actuator_status):
    print("----------------------------------------")
    print("I/O Devices Status")
    print("LED\t\tButton\t\tActuator")
    print(led_status + "\t" + button_status + "\t\t" + actuator_status)
    print("----------------------------------------")

if __name__ == "__main__":

    COMPRESSION_TIME = 10
    PRINT_TIME_SLEEP = 2

    svalue = val('d',0.0)
    ivalue = val('d',0.0)

    start = time.perf_counter()
    jobs = []
    process1 = proc(
            target=standardListInit,
        args=(5,20,svalue,"Off\t","Off","Not Compressing")
    )
    jobs.append(process1)
    process2 = proc(
            target=injuredListInit,
        args=(5,20,ivalue,"Off\t",0,"Not Compressing")
    )
    jobs.append(process2)

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()

    stop = time.perf_counter()

    print(stop-start)

    print(svalue.value)
    print(ivalue.value)

    parser = Parser()

    sval = round(svalue.value,2)
    ival = round(ivalue.value,2)

    parser.write_two_to_file(sval,ival)

    if svalue.value < ivalue.value or svalue.value > ivalue.value:
        print("Servo activated")
        print("Device Sleeping")
        LED_Status = "On\t"
        # Creates new task for constantly printing out the state of the I/O devices

        for x in range(0,COMPRESSION_TIME,PRINT_TIME_SLEEP):
            print_styled(LED_Status,"Off","Compressing")
            time.sleep(PRINT_TIME_SLEEP)

        LED_Status = "Off\t"
        print("Device Re-activating")
    else:
        print("Go next")