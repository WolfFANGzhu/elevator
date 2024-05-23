import os
import NetClient
import time
from enum import IntEnum
from elevator import Elevator
from elevatorState import State
from elevatorController import ElevatorController

##Example Code For Elevator Project
#Feel free to rewrite this file!


############ Elevator state ############
#Feel free to design the states of your elevator system.
class ElevatorState(IntEnum):
    up = 0
    down = 1
    stopped_door_closed = 2
    stopped_door_opened = 3
    stopped_opening_door = 4

# This function determines whether a new message has been received
def is_received_new_message(oldTimeStamp:int, oldServerMessage:str, Msgunprocessed:bool = False)->bool:
    if(Msgunprocessed):
        return True
    else:
        if(oldTimeStamp == zmqThread.messageTimeStamp and 
           oldServerMessage == zmqThread.receivedMessage):
            return False
        else:
            return True

if __name__=='__main__':

    ############ Connect the Server ############
    identity = "Team15" #write your team name here.
    zmqThread = NetClient.ZmqClientThread(identity=identity)


    ############ Initialize Elevator System ############
    timeStamp = -1 #Used when receiving new message
    serverMessage = "" #Used when receiving new message
    messageUnprocessed = False #Used when receiving new message 
    elevatorController:ElevatorController = ElevatorController(zmqThread)
    temp_msg = ""
    

    while(True):
        
        ############ Your timed automata design ############
        

        if(is_received_new_message(timeStamp,serverMessage,messageUnprocessed)):
            timeStamp = zmqThread.messageTimeStamp
            serverMessage = zmqThread.receivedMessage
            temp_msg = serverMessage
        else:
            temp_msg = ""
        elevatorController.update(temp_msg)
        time.sleep(0.01)

            

    '''
    For Other kinds of available serverMessage, see readMe.txt
    '''
    