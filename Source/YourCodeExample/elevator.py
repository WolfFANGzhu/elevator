from elevatorState import State
from direction import Direction
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox,QWidget
import NetClient
# Elevator
class Elevator(QWidget):

    def __init__(self,elevatorId:int,zmqThread:NetClient.ZmqClientThread,upTask,downTask) -> None:
        super().__init__()
        self.elevatorId = elevatorId
        self.zmqThread = zmqThread
        # Move related variables
        self.currentPos: float = 1.0 # Initially stop at floor 1
        self.__currentSpeed = 0.1
        self.currentDirection: Direction = Direction.wait # Direction record
        self.targetFloor: list[int] = []
        self.upTask = upTask
        self.downTask = downTask
        # Weight related variables
        self.__currentWeight: int = 0
        self.weightLimit: int = 800
        self.maxPeopleNum: int = 10
        # Door related variables
        self.__doorOpenTime: float = 3.2
        self.__doorCloseTime: float = 3.2
        self.__elevatorWaitTime: float = 10.0
        self.__doorSpeed: float = 0.1
        self.__doorInterval: float = 0.0
        self.__doorOpenFlag: bool = False
        self.__doorCloseFlag: bool = False
        # State
        self.currentState: State = State.stopped_door_closed
        # Init Ui
        self.setupUi(self,elevatorId)
        return

    def reset(self) -> None:
        # Move related variables
        self.currentPos: float = 1.0 # Initially stop at floor 1
        self.__currentSpeed = 0.1
        self.currentDirection: Direction = Direction.up # Direction record
        self.targetFloor: list[int] = []
        # Weight related variables
        self.__currentWeight: int = 0
        self.weightLimit: int = 800
        self.maxPeopleNum: int = 10
        # Door related variables
        self.__doorOpenTime: float = 3.2
        self.__doorCloseTime: float = 3.2
        self.__elevatorWaitTime: int = 3.2
        self.__doorSpeed: float = 0.1
        self.__doorInterval: float = 0.0
        self.__doorOpenFlag: bool = False
        self.__doorCloseFlag: bool = False
        # State
        self.currentState: State = State.stopped_door_closed
        return
        
    def move(self) -> None:
        if self.currentState == State.up:
            self.currentPos += self.__currentSpeed
        elif self.currentState == State.down:
            self.currentPos -= self.__currentSpeed

        # Check if the elevator has reached the target floor
        if self.currentPos > self.targetFloor[0]-0.01 and self.currentPos < self.targetFloor[0]+0.01:
            # Arrive! transfer state to stopped_door_opening
            arrivedFloor = self.targetFloor.pop(0)
            self.currentPos = float(arrivedFloor)
            self.floorArrivedMessage(self.currentState,arrivedFloor,self.elevatorId)
            self.currentState = State.stopped_opening_door
            if len(self.targetFloor) == 0:
                self.currentDirection = Direction.wait
            pass
        return

    def openingDoor(self) -> None:
        # Ignore Flag
        if self.__doorOpenFlag:
            self.__doorOpenFlag = False
        if self.__doorCloseFlag:
            self.__doorCloseFlag = False
        # Keep Opening the door
        self.__doorInterval += self.__doorSpeed
        if self.__doorInterval >= self.__doorOpenTime:
            self.__doorInterval = 0.0
            self.doorOpenedMessage(self.elevatorId)
            self.currentState = State.stopped_door_opened
        return
    def closingDoor(self) -> None:
        # Ignore Repeated Close Flag
        if self.__doorCloseFlag:
            self.__doorCloseFlag = False
        # Pay attention to Open Flag
        if self.__doorOpenFlag:
            # If press open button, reopen the door immediately
            self.__doorInterval = self.__doorOpenTime - self.__doorInterval
            self.__doorOpenFlag = False
            self.currentState = State.stopped_opening_door
        # Keep Closing the door
        self.__doorInterval += self.__doorSpeed
        if self.__doorInterval >= self.__doorCloseTime:
            self.__doorInterval = 0.0
            self.doorClosedMessage(self.elevatorId)
            self.currentState = State.stopped_door_closed
        return

    def waitForClosingDoor(self) -> None:
        # Close? transfer state to closing door
        if self.__doorCloseFlag:
            self.__doorInterval = 0.0
            self.currentState = State.stopped_closing_door
            self.__doorCloseFlag = False
        # Open Flag is on, keep opened
        if self.__doorOpenFlag:
            self.__doorOpenFlag = False

        self.__doorInterval += self.__doorSpeed
        if self.__doorInterval >= self.__elevatorWaitTime:
            self.__doorInterval = 0.0
            self.currentState = State.stopped_closing_door
            
        return
    
# Sending Msg
    def floorArrivedMessage(self,state: State, floor: int, eid: int) -> None:
        print("floor arrived message",state,floor,eid)
        directions = ["up", "down", ""]
        floors = ["-1", "1", "2", "3"]
        elevators = ["#1", "#2"]

        direction_str = directions[state.value]
        floor_str = floors[floor]
        elevator_str = elevators[eid - 1]  # Adjusting elevator index to start from 1

        message = f"{direction_str}_floor_arrived@{floor_str}{elevator_str}"
        self.zmqThread.sendMsg(message)
    def doorOpenedMessage(self,eid: int) -> None:
        elevators = ["#1", "#2"]
        elevator_str = elevators[eid - 1]
        message = f"door_opened{elevator_str}"
        self.zmqThread.sendMsg(message)
    def doorClosedMessage(self,eid: int) -> None:
        elevators = ["#1", "#2"]
        elevator_str = elevators[eid - 1]
        message = f"door_closed{elevator_str}"
        self.zmqThread.sendMsg(message)
    
    def checkTargetFloor(self) -> bool:
        if len(self.targetFloor) == 0:
            return False
        # If there is a target floor, begin to move
        if self.targetFloor[0] > self.currentPos:
            self.currentState = State.up
        elif self.targetFloor[0] < self.currentPos:
            self.currentState = State.down
        elif self.targetFloor[0] == self.currentPos:
            self.targetFloor.remove(int(self.currentPos))
            self.floorArrivedMessage(State.up,self.getCurrentFloor(),self.elevatorId)
            self.currentState = State.stopped_opening_door
        return True   
    def checkOpenDoor(self) -> None:
        if self.__doorOpenFlag:
            self.__doorOpenFlag = False
            self.currentState = State.stopped_opening_door
        return
    def clearOutsideButton(self,state: State, floor: int) -> None:
        if state == State.up:
            self.upTask[floor-1] = 0
        elif state == State.down:
            self.downTask[floor-2] = 0

# Util function inside class
    def getCurrentFloor(self) -> int:
        return round(self.currentPos)
    
            
# Utility Functions for controller & button panel inside this elevator
    # Reveive outer request from controller
    def addTargetFloor(self, floor: int) -> None:
        if floor in self.targetFloor:
            return
        self.targetFloor.append(floor)
        self.targetFloor.sort(reverse=(self.currentDirection == Direction.up))
        print("current target floor: ",self.targetFloor)
        return
    def setOpenDoorFlag(self) -> None:
        self.__doorOpenFlag = True
        return
    def setCloseDoorFlag(self) -> None:
        self.__doorCloseFlag = True
        return
    
    def update(self) -> None:
        if self.currentState == State.up or self.currentState == State.down:
            print("elevator: ",self.elevatorId," is moving",self.currentState.name)
            self.move()
            pass
        elif self.currentState == State.stopped_opening_door:
            self.openingDoor()
            pass
        elif self.currentState == State.stopped_door_opened:
            self.waitForClosingDoor()
            pass
        elif self.currentState == State.stopped_closing_door:
            print("elevator: ",self.elevatorId," is closing door")
            self.closingDoor()
            pass
        elif self.currentState == State.stopped_door_closed:
            # Find if Controller give new command to this elevator
            hasTarget = self.checkTargetFloor()
            # If door is already closed， user can still exit or enter by request opening door.
            if not hasTarget:
                self.checkOpenDoor()
            pass
        return
    

    """UI Related functions"""
    def setupUi(self):
        self.setObjectName("InsideWidget")
        self.resize(222, 289)

        layout = QtWidgets.QVBoxLayout(self)

        self.Direction = QtWidgets.QGraphicsView()
        layout.addWidget(self.Direction)

        self.LCD = QtWidgets.QLCDNumber()
        self.set_lcd_value(1) # default value is 1
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.LCD.setFont(font)
        self.LCD.setSmallDecimalPoint(False)
        self.LCD.setDigitCount(1)
        self.LCD.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        layout.addWidget(self.LCD)

        self.f3 = QtWidgets.QPushButton("3")
        self.f3.clicked.connect(self.on_f3_clicked)
        self.f3_activeFlag = False
        layout.addWidget(self.f3)

        self.f2 = QtWidgets.QPushButton("2")
        self.f2.clicked.connect(self.on_f2_clicked)
        self.f2_activeFlag = False
        layout.addWidget(self.f2)

        self.f1 = QtWidgets.QPushButton("1")
        self.f1.clicked.connect(self.on_f1_clicked)
        self.f1_activeFlag = False
        layout.addWidget(self.f1)

        self.open = QtWidgets.QPushButton("<|>")
        self.open.clicked.connect(self.on_open_clicked)
        layout.addWidget(self.open)

        self.close = QtWidgets.QPushButton(">|<")
        self.close.clicked.connect(self.on_close_clicked)
        layout.addWidget(self.close)

        self.label = QtWidgets.QLabel("E#" + str(self.elevatorId))
        layout.addWidget(self.label)

        # ReTranslate UI
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("InsideWidget", "Elevator#" + str(self.elevatorId)))
        self.label.setText(_translate("InsideWidget", "E#" + str(self.elevatorId)))
    # button click event
    def on_f1_clicked(self):
        if self.f1_activeFlag:
            return
        else:
            self.f1_activeFlag = True
            self.floorbutton_clicked(self.f1,1)
    def on_f2_clicked(self):
        if self.f2_activeFlag:
            return
        else:
            self.f2_activeFlag = True
            self.floorbutton_clicked(self.f2,2)
    def on_f3_clicked(self):
        if self.f3_activeFlag:
            return
        else:
            self.f3_activeFlag = True
            self.floorbutton_clicked(self.f3,3)
    def floorbutton_clicked(self,button:QtWidgets.QPushButton,floor:int):
        if(self.currentPos < floor):
                direction = Direction.up # up
        elif(self.currentPos > floor): # down
                direction = Direction.down
        else:
            direction = Direction.wait # same
        # 这个电梯方向相同或方向状态不存在，插入target priority queue
        if self.currentDirection == direction or self.currentDirection == Direction.wait:
            button.setStyleSheet("background-color: yellow;")
            self.addTargetFloor(floor) # 如果电梯向上，从小到大[2,3],反之[2,1]
    def resetUi(self):
        self.f1_activeFlag = False
        self.f2_activeFlag = False
        self.f3_activeFlag = False
        self.f1.setStyleSheet("background-color: none;")
        self.f2.setStyleSheet("background-color: none;")
        self.f3.setStyleSheet("background-color: none;")
    def updateUi(self):
        self.set_lcd_value(self.getCurrentFloor())
        
    def on_open_clicked(self):
        # Open button may not be light up on pressed, it is only for testing
        self.open.setStyleSheet("background-color: yellow;")
        self.setOpenDoorFlag()
    def on_close_clicked(self):
        print("close button is pressed!")

    # Other util functions

    def set_lcd_value(self,value):
        self.LCD.display(value)

