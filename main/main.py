# ----------------------------------------------------------------
# This program uses Classes and Methods since it utilizes multiprocessing to process multiple commands simultaneously. Without categorizing each process into classes and their respective methods, the code would be much more messier to run and understand.
# Furthermore, classes and methods allows for better organization of code. Since we have several instances where we have to use similar data structures but different data. So we deemed it more approriate to create Classes for those instances. There were also instances where methods were needed for two sets of data with the same data structure so Classes were used for those as well

# Note: The code will have to be run on a Command Line or Terminal on a Raspberry Pi, not IDLE since it does not support the multiprocessing functions.

from sensor_library import *     
import time,random              
from write_temp import Temp_To_Txt as Parser    

# Creating a class that maintains a list of temperatures, rolling averages, and the ID of the sensor used
class ListTemp:
    
    def __init__(self,sensorid) -> None:
        self.templist = []           # Initialize an empty list to store temperatures
        self.rollinglist = []        # Initialize an empty list to store rolling averages
        self.id = sensorid           # Store the ID of the sensor, if ID = 0, Standard Temperature, ID = 1, Injured Temp
        if sensorid == 1:            # If the sensor ID is 1 (injured sensor), create a new Temperature_Sensor object
            self.sensor = Temperature_Sensor()

    # Method to get the temperature from the appropriate source based on the sensor ID
    def getSensorTemp(self) -> float:
        if self.id == 0:            # If the sensor ID is 0 (standard sensor), return a random value between 29.0 and 30.0. Normally this would be from another sensor, but due to the limitations only allowing one sensor for us, a random number generator was used for the standard temperature.
            return float(random.randint(290,300))/10.0
        elif self.id == 1:          # If the sensor ID is 1 (injured sensor), get the average temperature from the Temperature_Sensor object
            return self.sensor.avg_temp()
        else:
            print("Please input a valid Sensor ID")   # If an invalid sensor ID is provided, print an error message

    # Method to add a temperature value to the templist
    def addTemp(self) -> None:
        self.templist.append(self.getSensorTemp())

    # Method to calculate rolling averages and store them in the rollinglist
    def getRollingTemp(self,rolling_interval,total_time):
        for x in range(0,total_time):                   # Loop through total_time number of times
            self.addTemp()                              # Add a temperature value to the templist
            try:
                if len(self.templist) == rolling_interval:   # If the templist contains the specified number of temperature values
                    avg = 0
                    for x in range(0,len(self.templist)):    # Calculate the average temperature value
                        avg += self.templist[x]
                    avg = avg/len(self.templist)
                    self.rollinglist.append(avg)            # Add the average temperature to the rollinglist
                    self.print_styled(avg)                  # Print the templist and rolling average in a stylized format
                    self.templist.pop(0)                     # Remove the oldest temperature value from the templist to maintain the rolling interval
            except ZeroDivisionError:
                print("Please input a list of temperatures.")    # If an empty list is provided, print an error message and return None
                return None
            time.sleep(1)

    # Method to print the templist and rolling average in a stylized format
    def print_styled(self,avg):
        str_id = ""
        if self.id == 0:            # If the sensor ID is 0 (standard sensor), set str_id to "Standard Temperatures"
            str_id = "Standard Temperatures"
        else:
            str_id = "Injured Temperatures "    # If the sensor ID is 1 (injured sensor), set str_id to "Injured Temperatures"
        print("------",str_id,"-----")
        print("[",end=" ")
        for x in self.templist:
            print(round(x,2),end=" ")
        print("]")
        print("Rolling Avg:",round(avg,2))
        print("----------------------------------")


from gpiozero import Servo
from gpiozero import Button as gpioButton
import gpiozero
import sys
from gpiozero.pins.pigpio import PiGPIOFactory

# Creating a class for the actuator
class Actuator:

    def __init__(self, gpioid):
        # Setting up the pin factory
        gpiozero.Device.pin_factory = PiGPIOFactory('127.0.0.1')
        self.id = gpioid
        self.servo = Servo(gpioid)
    
    def min(self):
        # Moving the actuator to minimum position
        self.servo.min()
        time.sleep(1)
    
    def max(self):
        # Moving the actuator to maximum position
        self.servo.max()
        time.sleep(1)

# Creating a class for the Button
class Button:

    def __init__(self, gpioid):
        # Setting up the pin factory
        gpiozero.Device.pin_factory = PiGPIOFactory('127.0.0.1')
        self.id = gpioid
        self.button = gpioButton(gpioid)
    
    def check_press(self):
        # Checking if the button is pressed or not
        if self.button.is_pressed:
            return True
        else:
            return False

from gpiozero import LED

from multiprocessing import Process as proc
from multiprocessing import Value as val

# Creating 2 instances of a class
standardList = ListTemp(0)
injuredList = ListTemp(1)

def standardListInit(rolling, total, rolling_avg):
    # Initializing rolling temperature list for the standard temperature 
    standardList.getRollingTemp(rolling,total)
    standard_avg = 0
    
    # Calculating the rolling average of the standard temperature
    for x in standardList.rollinglist:
        standard_avg += x
    
    rolling_avg.value = standard_avg/len(standardList.rollinglist)


def injuredListInit(rolling,total,rolling_avg):
    # Initializing rolling temperature list for the injured temperature
    injuredList.getRollingTemp(rolling,total)
    injured_avg = 0

    # Calculating the rolling average of the injured temperature
    for x in injuredList.rollinglist:
        injured_avg += x
    
    rolling_avg.value = injured_avg/len(injuredList.rollinglist)

def cont_check_button(gpioid,button_state):
    # Creating an instance of the button class
    button = Button(gpioid)
    while True:
        # Checking if the button is pressed or not
        if button.check_press():
            button_state.value = not button_state.value
            time.sleep(2)
            print("Button pressed")

def cont_check_button_hold(gpioid,time_hold,button_state):
    # Creating an instance of the button class
    button = Button(gpioid)
    while True:
        for x in range(0,time_hold+1):
            # Checking if the button is pressed for the given time period or not
            if button.check_press():
                if x == time_hold:
                    button_state.value = True
                    break
            else:
                break
            time.sleep(1)

def main():
    try:
        ACTUATOR_ID = 17
        BUTTON_ID = 19
        LED_ID = 5
        servo = Actuator(ACTUATOR_ID)                     # Creates a new Actuator object with pin number 17
        button_status = val('b',False)           # Creates a new shared boolean variable with an initial value of False
        button_status = val('b',False)
        led = LED(LED_ID)
        
        # Creates a new process that checks the state of a button and updates the shared variable
        button_job = proc(
                    target = cont_check_button,
                args=(BUTTON_ID,button_status)
            )
        button_job.start()
        
        # An 'infinite' loop is started
        while True:

            # Starts a nested loop that runs as long as the button is pressed
            while button_status.value:
                
                # Creates two new shared variables with initial values of 0.0 to store average temperature values
                svalue = val('d',0.0)
                ivalue = val('d',0.0)

                start = time.perf_counter()      # Records the start time

                jobs = []
                
                ROLLING_INTERVAL = 2
                TOTAL_TIME_INTERVAL = 10

                # Creates a new process that initializes a list of standard temperature values
                process1 = proc(
                        target=standardListInit,
                    args=(ROLLING_INTERVAL,TOTAL_TIME_INTERVAL,svalue)
                )
                jobs.append(process1)

                # Creates a new process that initializes a list of injured temperature values
                process2 = proc(
                        target=injuredListInit,
                    args=(ROLLING_INTERVAL,TOTAL_TIME_INTERVAL,ivalue)
                )
                jobs.append(process2)
                
                # Starts each process in the list
                for j in jobs:
                    j.start()
            
                # Waits for each process in the list to finish before continuing

                led.blink()

                for j in jobs:
                    j.join()

                led.off()
            
                # Terminates each process in the list
                for j in jobs:
                    j.terminate()

                stop = time.perf_counter()         # Records the end time

                print("Total Time Elapsed: ", stop-start)

                print("Standard Avg Temp:", svalue.value)
                print("Injured Avg Temp:", ivalue.value)

                # Creates a new Parser object
                parser = Parser()

                sval = round(svalue.value,2)
                ival = round(ivalue.value,2)
                
                # Writes the temperature values to a file using the Parser object
                parser.write_two_to_file(sval,ival)

                # Activates the servo motor if the standard average temperature is lower than the injured average temperature
                if svalue.value < ivalue.value:
                    print("Servo activated")
                    servo.max()
                    print("sleep")
                    led.on()
                    time.sleep(5)
                    led.off()
                    print("unsleep")
                else:
                    print("Go next")
                    servo.min()

            # If the button is not pressed, print a message and wait for 3 seconds before checking the button state again
            while not button_status.value:
                print("Button off")
                led.off()
                time.sleep(3)

    # If an exception is caught, exits the program
    except:
        sys.exit()

if __name__ == "__main__":
    try:
        button_status_hold = val('b',False)   # Creates a boolean value for button status

        BUTTON_ID = 19
        TIME_HOLD = 3
        
        # Creates a process to check the button status
        button_job2 = proc(
                    target = cont_check_button_hold,
                args=(BUTTON_ID,TIME_HOLD,button_status_hold)
            )
        
        button_job2.start()                   # Starts the button checking process

        # Creates the main process
        main_job = proc(
                target = main
        )

        main_job.start()                      # Starts the main process

        # Loops until button is held down
        while True:
            
            # Checks if the button is held down
            if button_status_hold.value:
                # Terminates both processes
                button_job2.terminate()
                main_job.terminate()
                
                print("Forced Exit")
                sys.exit()

    # If an exception is encountered, exits script
    except:
        sys.exit()