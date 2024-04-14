# Elevator System Requirement
## 1.System goal
In this project, our goal was to develop a software to manage the operation of two elevators in a three-floor building and to improve the efficiency of this process. We not only designed button panels and UIs for each floor and each elevator so that the user can know what is going on in the elevator, but also designed the elevator control system so that the scheduling of the two elevators can be done more efficiently, thus providing a better experience for the user.

## 2.Basic requirements setting
- There are three floors, denoted as `floor_num = 3`
- There are two elevators, denoted as `elevator_num = 2`
- Setting limits on elevators:
  - Max speed is $1m/s$, denoted as `max_speed = 1`
  - Time to open and close the door is $4s$, denoted as `time_open_close = 4`
  - Weight limit is $800kg$, denoted as `weight_limit = 800`

## 3. Basic use case
### 3.1 Use case diagram
<div align=center><img src=./Use_case_diagram.png></div>
<center style="font-size:14px;color:#C0C0C0;text-decoration:underline">Elevator system normal use case diagram</center>  
This is a preliminary overview of the normal use case diagram for the elevator system. Specific details and requirements are discussed in the following sections.

### 3.2 Sequence diagram
<div align=center><img src=./basic_sequence.png></div>
<center style="font-size:14px;color:#C0C0C0;text-decoration:underline">Elevator system basic sequence diagram</center> 
This is a preliminary overview of the basic sequence diagram for the elevator system while using. Specific details and requirements are discussed in the following sections.

## Normal requirements
1. Requirement1: Elevator_UI  
- R1.1: The passengers should be able to know elevator's position and moving direction.
- R1.2: The passengers should be able to control the elevator's door, including open and close while the elevator is stopping.
- R1.3: The passengers should be able to select the certain floor they want to go.
- R1.4: The passengers should be able to call security guard while emergency occurs.
- R1.5: The elevator system should be able to get the information when passengers press the buttons.

2. Requirement2: Floor_UI
- R2.1: The passengers should be able to know two elevators' position and moving direction.
- R2.2: The passengers should be able to select and press the direction button they want to go.
- R2.3: The passengers should be able to know which floor they are on.
- R2.4: The elevator system should be able to know how buttons are pressed on each floor.

3. Requirement3: Elevator_system
- 
4. Requirement4: Sensor
-
## Special cases in discussion
- Elevator alarm when overloaded.
- The elevator on the first floor only goes up.
- The third floor elevator only goes down. 
- Open the door and close it at the same time. It won't close.
- Press any key to see if there is an elevator bug.
- When the elevator goes up, the first floor is pressed and when it reaches the third floor/ the second floor(Depends on the top floor being pressed), the 1st floor button is canceled.
- No one presses the button on the third floor. At this point, the second floor goes up, but people press the button to go to the first floor, and the elevator closes, then opens, then closes again and goes down to the first floor.
- Press repeatedly to cancel.
- One on the 1st floor, one on the 3rd floor initially.
- People need to press the button in advance or they can't get to the target floor.