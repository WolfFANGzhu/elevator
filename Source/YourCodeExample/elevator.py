from elevatorState import State
import NetClient
# Elevator
class Elevator:

    def __init__(self,elevatorId:int,zmqThread:NetClient.ZmqClientThread) -> None:
        self.elevatorId = elevatorId
        self.zmqThread = zmqThread
        # Move related variables
        self.__speedLimit: int = 0.1
        self.currentPos: float = 1.0 # Initially stop at floor 1
        self.currentFloor: int = 1
        self.__currentSpeed = 99
        self.currentDirection: int = 0 # 0 means stop, 1 means up, -1 means down
        self.targetFloor: list[int] = []
        # Weight related variables
        self.__currentWeight: int = 0
        self.weightLimit: int = 800
        self.maxPeopleNum: int = 10
        # Door related variables
        self.__doorOpenTime: float = 3.2
        self.__doorCloseTime: float = 3.2
        self.__elevatorWaitTime: int = 10
        self.__doorSpeed: float = 0.1
        self.__doorInterval: float = 0.0
        self.__doorOpenFlag: bool = False
        self.__doorCloseFlag: bool = False
        # State
        self.currentState: State = State.stopped_door_closed
        return

    def reset(self) -> None:
        self.__speedLimit: int = 0.1
        self.currentPos: float = 1.0 # Initially stop at floor 1
        self.currentFloor: int = 1
        self.__currentSpeed = 0.1
        self.currentDirection: int = 0 # 0 means stop, 1 means up, -1 means down
        self.targetFloor: list[int] = []
        # Weight related variables
        self.__currentWeight: int = 0
        self.weightLimit: int = 800
        self.maxPeopleNum: int = 10
        # Door related variables
        self.__doorOpenTime: float = 3.2
        self.__doorCloseTime: float = 3.2
        self.__elevatorWaitTime: int = 10
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
            self.currentFloor = arrivedFloor
            self.currentPos = float(arrivedFloor)
            self.currentState = State.stopped_opening_door
            self.floorArrivedMessage(self.currentState,self.currentFloor,self.elevatorId)
            if len(self.targetFloor) == 0:
                self.currentDirection = 0
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
        # Ignore Close Flag
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
            
        return
    
# Sending Msg
    def floorArrivedMessage(self,state: State, floor: int, eid: int) -> None:
        directions = ["up", "down", ""]
        floors = ["-1", "1", "2", "3"]
        elevators = ["#1", "#2"]

        direction_str = directions[state.direction]
        floor_str = floors[floor]
        elevator_str = elevators[eid - 1]  # Adjusting elevator index to start from 1

        message = f"{direction_str}_floor_{floor_str}_arrived{elevator_str}"
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
        return True   
    def checkOpenDoor(self) -> None:
        if self.__doorOpenFlag:
            self.__doorOpenFlag = False
            self.currentState = State.stopped_opening_door
        return

# Utility Functions for controller
    def addTargetFloor(self, floor: int) -> None:
        self.targetFloor.append(floor)
        self.targetFloor.sort(reverse=(self.currentDirection == 1))
        return
    def setOpenDoorFlag(self) -> None:
        self.__doorOpenFlag = True
        return
    def setCloseDoorFlag(self) -> None:
        self.__doorCloseFlag = True
        return
    
    def update(self) -> None:
        if self.currentState == State.up or self.currentState == State.down:
            self.move()
            pass
        elif self.currentState == State.stopped_opening_door:
            self.openingDoor()
            pass
        elif self.currentState == State.stopped_door_opened:
            self.waitForClosingDoor()
            pass
        elif self.currentState == State.stopped_closing_door:
            self.closingDoor()
            pass
        elif self.currentState == State.stopped_door_closed:
            # Find if Controller give new command to this elevator
            hasTarget = self.checkTargetFloor()
            if not hasTarget:
                self.checkOpenDoor()
            pass
        return
    