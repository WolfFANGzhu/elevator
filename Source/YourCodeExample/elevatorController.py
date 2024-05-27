from elevator import Elevator
from elevatorState import State
from direction import Direction
import NetClient
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox,QWidget
# Elevator Controller
# This class is responsible for 
# 1. Parsing the command from the server
# 2. Assigning the inner button panel(open, close, select floor) to the elevator, without considering constraints
# 3. Assigning the outer button panel(call up, call down) to the elevator, considering which task to assign to which elevator
class ElevatorController(QWidget):

    
    def __init__(self,zmqThread:NetClient.ZmqClientThread) -> None:
        # Initialize two elevators
        self.elevators: list[Elevator] = []
        # Button Panel Outside the Elevator
        self.upTask = [0,0] # 0 means up@1, 1 means up@2
        self.downTask = [0,0] # 0 means down@2, 1 means down@3
        self.msgQueue:list[str] = []
        self.elevators.append(Elevator(1,zmqThread,self.upTask,self.downTask))
        self.elevators.append(Elevator(2,zmqThread,self.upTask,self.downTask))
    def parseInput(self, command: str) -> None:
        # Parse the command from server
        """
        open_door
        close_door
        call_up: ["-1", "1", "2"], //For example, call_up@1 means a user on the first floor presses the button to call the elevator to go upwards.
        call_down: ["3", "2", "1"], //For instance, call_down@3 signifies a user on the third floor pressing the button to call the elevator to go downwards.
        select_floor: ["-1#1", "-1#2", "1#1", "1#2", "2#1", "2#2", "3#1", "3#2"], //For example, select_floor@2#1 means a user in elevator #1 selects to go to the second floor.
        reset: When your elevator system receives a reset signal, it should reset the elevator's state machine to its initial state.
        """
        # Parse the command from server
        command_parts = command.split('@')
        action = command_parts[0]
        if action == "open_door":
            pass
        elif action == "close_door":
            pass
        elif action == "call_up":
            # Basic logic is find an elevator is available and assign the task
            # Difficulty is that we dont know the potential direction the elevator is moving towards?
            floor = int(command_parts[1])
            # Intialize an empty var
            eid = -1
            # Very basic operation: find the nearest idle elevator to respond to request
            eid = self.getNearestStopElevator(floor)

            if eid != -1:
                self.elevators[eid].targetFloor.append(floor)
                return

            # 都没有，等待出现这个情况，加入等待队列，每一个update查询一遍
            self.msgQueue.append(command)
            pass
        elif action == "call_down":
            floor = int(command_parts[1])
            eid = -1
            # 先找空闲电梯离自己最近的一层的
            eid = self.getNearestStopElevator(floor)
            if(eid != -1):
                # Assign task
                self.elevators[eid].addTargetFloor(floor)
                return
            # # 都没有，等待出现这个情况，加入等待队列，每一个update查询一遍
            self.msgQueue.append(command)
            pass
        elif action == "select_floor":
            floor,eid = command_parts[1].split('#')
            eid = int(eid)-1
            floor = int(floor)
            print("user select in elevator#",eid+1, " floor",floor)
            elevator:Elevator = self.elevators[eid]
            # calculate direction by this command
            if(elevator.currentPos < floor):
                direction = Direction.up # up
            elif(elevator.currentPos > floor): # down
                direction = Direction.down
            else:
                direction = Direction.wait # same
            # 这个电梯方向相同或方向状态不存在，插入target priority queue
            if elevator.currentDirection == direction or elevator.currentDirection == Direction.wait:
                elevator.addTargetFloor(floor) # 如果电梯向上，从小到大[2,3],反之[2,1]

            
            # 暂时不考虑用户选的方向相反这种情况
            pass
        elif action == "reset":
            self.reset()
            pass
    def reset(self) -> None:
        for elevator in self.elevators:
            elevator.reset()
    def getNearestStopElevator(self, floor: int) -> int:
        # find the nearest elevator accrording to the floor that is requesting
        # return index of the elevator; return -1 if no elevator is available
        dist = [99,99]
        min_index = -1
        if(self.elevators[0].currentState == State.stopped_door_closed and len(self.elevators[0].targetFloor)==0):
            dist[0] = abs(self.elevators[0].getCurrentFloor() - floor)
        if(self.elevators[1].currentState == State.stopped_door_closed and len(self.elevators[0].targetFloor)==0):
            dist[1] = abs(self.elevators[1].getCurrentFloor() - floor)
        if(dist[0] == 99 and dist[1] == 99):
            return -1
        min_index = dist.index(min(dist))
        return min_index
    def getUpElevator(self, floor: int) -> int:
        # 找到相同方向的电梯便于2层向上搭便车
        if self.elevators[0].currentState == State.up and self.elevators[0].currentPos < floor:
            return 0
        elif self.elevators[1].currentState == State.up and self.elevators[1].currentPos < floor:
            return 1
        else:
            return -1
    def getDownElevator(self, floor: int) -> int:
        # 找到相同方向的电梯便于2层向下搭便车
        if self.elevators[0].currentState == State.down and self.elevators[0].currentPos > floor:
            return 0
        elif self.elevators[1].currentState == State.down and self.elevators[1].currentPos > floor:
            return 1
        else:
            return -1
    def update(self,msg:str) -> None:
        if len(self.msgQueue) > 0:
            self.parseInput(self.msgQueue.pop(0))
        if msg != "":
            self.parseInput(msg)
        for elevator in self.elevators:
            elevator.update()
        return
    
    ### UI part contains three panel
    def setupUi(self, layout):
        self.verticalLayout = QtWidgets.QVBoxLayout(layout)

        self.Up = QtWidgets.QPushButton("Up")
        self.Up.setObjectName("Up")
        self.verticalLayout.addWidget(self.Up)

        self.Down = QtWidgets.QPushButton("Down")
        self.Down.setObjectName("Down")
        self.verticalLayout.addWidget(self.Down)

        lcd_layout = QtWidgets.QHBoxLayout()
        self.verticalLayout.addLayout(lcd_layout)

        self.E1 = QtWidgets.QLCDNumber()
        self.E1.setDigitCount(1)
        self.E1.setObjectName("E1")
        lcd_layout.addWidget(self.E1)

        self.E2 = QtWidgets.QLCDNumber()
        self.E2.setDigitCount(1)
        self.E2.setObjectName("E2")
        lcd_layout.addWidget(self.E2)

        _translate = QtCore.QCoreApplication.translate
        layout.setWindowTitle(_translate("Form", "Form"))
        self.Up.setText(_translate("Form", "Up"))
        self.Down.setText(_translate("Form", "Down"))