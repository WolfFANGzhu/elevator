# Requirement
## basic requirements
- A building with 3 floors
- 2 elevators (should be coordinated)
- Interfaces – Button panels and display inside each elevator – Button panels and display on each floor
- System Events – Door open, door closed
- Elevator arrive at each floor

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