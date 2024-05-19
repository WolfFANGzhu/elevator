from elevator import Elevator
from elevatorState import State
import NetClient
class ElevatorController:

    
    def __init__(self,zmqThread:NetClient.ZmqClientThread) -> None:
        # Initialize two elevators
        self.elevators: list[Elevator] = []
        self.elevators.append(Elevator(1,zmqThread))
        self.elevators.append(Elevator(2,zmqThread))
        # Button Panel Outside the Elevator
        self.upTask = [0,0] # 0 means up@1, 1 means up@2
        self.downTask = [0,0] # 0 means down@2, 1 means down@3
        self.msgQueue:list[str] = []
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
            # Code to handle opening the door
            pass
        elif action == "close_door":
            # Code to handle closing the door
            pass
        elif action == "call_up":
            floor = int(command_parts[1])
            # Intialize an empty var
            eid = -1
            # 先判断：is there any elevator that is at the requesting floor and not going to move in the opposite direction
            for i in range(2):
                if self.elevators[i].currentFloor == floor and self.elevators[i].currentDirection != -1:
                    # if the elevator is at the requesting floor and is not going down
                    eid = i
                    self.elevators[i].setOpenDoorFlag()
                    return
    
            # 先找空闲电梯离自己最近的一层的
            eid = self.getNearestStopElevator(floor)
            if(eid != -1):
                # Assign task
                self.elevators[eid].addTargetFloor(floor)
                return
            # 有没有电梯位置小于这一层且正在上行的(搭便车向上的情况只会出现在2层，所以只限定2层的request)
            if(floor == 2):
                eid = self.getUpElevator(floor)
                if(eid != -1):
                    self.elevators[eid].addTargetFloor(floor)
                    return
                
            # 都没有，等待出现这个情况，加入等待队列，每一个update查询一遍
            self.msgQueue.append(command)
            pass
        elif action == "call_down":
            floor = int(command_parts[1])
            # Intialize an empty var
            eid = -1
            # 先判断：is there any elevator that is at the requesting floor and not going to move in the opposite direction
            for i in range(2):
                if self.elevators[i].currentFloor == floor and self.elevators[i].currentDirection != 1:
                    # if the elevator is at the requesting floor and is not going down
                    eid = i
                    self.elevators[i].setOpenDoorFlag()
                    return
            # 先找空闲电梯离自己最近的一层的
            eid = self.getNearestStopElevator(floor)
            if(eid != -1):
                # Assign task
                self.elevators[eid].addTargetFloor(floor)
                return
            # 有没有电梯位置大于这一层且正在下行的
            if(floor == 2):
                eid = self.getDownElevator(floor)
                if(eid != -1):
                    self.elevators[eid].addTargetFloor(floor)
                    return
            # 都没有，等待出现这个情况，加入等待队列，每一个update查询一遍
            self.msgQueue.append(command)
            pass
        elif action == "select_floor":
            eid, floor = command_parts[1].split('#')
            eid = int(eid-1)
            floor = int(floor)
            elevator:Elevator = self.elevators[eid]
            # 计算 direction
            if(elevator.currentPos < floor):
                direction = 1 # up
            elif(elevator.currentPos > floor): # down
                direction = -1
            else:
                direction = 0 # same
            # 这个电梯方向相同或方向状态不存在，插入target priority queue
            if elevator.currentDirection == direction or elevator.currentDirection == 0:
                elevator.addTargetFloor(floor) # 如果电梯向上，从小到大[2,3],反之[2,1]

            # 这个电梯有target楼层，方向不同，插入waiting queue，待所有target清空后，把waiting queue插入target queue
            # 暂时不考虑这种情况
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
        if(self.elevators[0].currentState == State.stopped_door_closed):
            dist[0] = abs(self.elevators[0].currentFloor - floor)
        if(self.elevators[1].currentState == State.stopped_door_closed):
            dist[1] = abs(self.elevators[1].currentFloor - floor)
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