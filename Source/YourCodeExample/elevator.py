from elevatorState import State
from direction import Direction
import NetClient
# Elevator
class Elevator:

    def __init__(self,elevatorId:int,zmqThread:NetClient.ZmqClientThread,upTask,downTask) -> None:
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
    
            
# Utility Functions for controller
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
    