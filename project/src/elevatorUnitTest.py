import sys
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from unittest.mock import MagicMock, patch
from elevator import Elevator
from elevatorState import State
from direction import Direction
import NetClient

class TestElevator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test environment and set class-level variables"""
        cls.app = QApplication(sys.argv)
        pass
    def setUp(self):
        """Initialization of each test case"""
        self.zmqThreadMock = MagicMock(spec=NetClient.ZmqClientThread)
        self.elevator:Elevator = Elevator(elevatorId=0, zmqThread=self.zmqThreadMock)
        self.elevator.show()
    def tearDown(self):
        """Cleanup after each test case"""
        self.elevator.close()
    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        # Ensure the event loop runs long enough to display the window
        QTest.qWait(1000)  # Delay 1 second to ensure the window is displayed
        cls.app.quit()
        pass

    def test_reset(self):
        """Test the reset functionality"""
        QTest.mouseClick(self.elevator.f3, Qt.LeftButton)
        QTest.qWait(500)  # Delay 0.5 second to ensure elevator is moving
        self.elevator.reset()
        QTest.qWait(500)  # Delay 0.5 second to ensure the window is displayed
        self.assertAlmostEqual(self.elevator.currentPos, 1.0)
        self.assertEqual(self.elevator.currentState, State.stopped_door_closed)
        self.assertEqual(self.elevator.LCD.value(),1)
    
    def test_move_up(self):
        """Test the move functionality without changing status"""
        initialPos = 1.1
        # Initialize the elevator status
        self.elevator.currentState = State.up
        self.elevator.currentPos = initialPos
        self.elevator.targetFloor = [2]
        self.elevator.move()
        self.assertAlmostEqual(self.elevator.currentPos, initialPos+self.elevator.getCurrentSpeed())
        self.assertEqual(self.elevator.targetFloor, [2])
        self.assertEqual(self.elevator.currentState, State.up)

    def test_move_down(self):
        """Test the move functionality when moving down"""
        initialPos = 2.4
        self.elevator.currentState = State.down
        self.elevator.currentPos = initialPos
        self.elevator.targetFloor = [1]
        self.elevator.move()
        self.assertAlmostEqual(self.elevator.currentPos, initialPos - self.elevator.getCurrentSpeed())
        self.assertEqual(self.elevator.targetFloor, [1])
        self.assertEqual(self.elevator.currentState, State.down)

    def test_move_up_arrive_at_floor(self):
        self.elevator.currentState = State.up
        self.elevator.currentPos = 3.0 - self.elevator.getCurrentSpeed()
        self.elevator.targetFloor = [3]
        self.elevator.move()
        self.assertEqual(self.elevator.currentPos, 3.0)
        self.assertEqual(self.elevator.targetFloor, [])
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)
        self.assertEqual(self.elevator.currentDirection, Direction.wait)

    def test_openingDoor_openFlag_true_closeFlag_true(self):
        """Test opening door when openFlag is True, closeFlag is True, and not changing status"""
        self.elevator.doorOpenFlag = True
        self.elevator.doorCloseFlag = True
        self.elevator.currentState = State.stopped_opening_door
        interval = 0.0
        self.elevator.doorInterval = interval
        self.elevator.openingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,interval+self.elevator.doorSpeed)
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)

    def test_openingDoor_openFlag_false_closeFlag_false(self):
        """Test opening door when openFlag is False, closeFlag is False, and is changing status"""
        self.elevator.doorOpenFlag = False
        self.elevator.doorCloseFlag = False
        self.elevator.currentState = State.stopped_opening_door
        interval = self.elevator.doorOpenTime - self.elevator.doorSpeed
        self.elevator.doorInterval = interval
        self.elevator.openingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,0.0)
        self.assertEqual(self.elevator.currentState, State.stopped_door_opened)

    def test_closingDoor_openFlag_true_closeFlag_true(self):
        """Test closing door when openFlag is True, closeFlag is True, and changing status to opening door"""
        self.elevator.doorOpenFlag = True
        self.elevator.doorCloseFlag = True
        self.elevator.currentState = State.stopped_closing_door
        interval = 0.6
        self.elevator.doorInterval = interval
        self.elevator.closingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,self.elevator.doorOpenTime-interval)
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)
    def test_closingDoor_openFlag_true_closeFlag_true(self):
        """Test closing door when openFlag is True, closeFlag is True, and changing status to door closed"""
        self.elevator.doorOpenFlag = False
        self.elevator.doorCloseFlag = False
        self.elevator.currentState = State.stopped_closing_door
        interval = self.elevator.doorCloseTime - self.elevator.doorSpeed
        self.elevator.doorInterval = interval
        self.elevator.closingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,0.0)
        self.assertEqual(self.elevator.currentState, State.stopped_door_closed)
    def test_waitForClosingDoor_openFlag_true_closeFlag_true(self):
        """Test door opened(waiting to close) when openFlag is True, closeFlag is True, and changing status to door closed"""
        self.elevator.doorOpenFlag = True
        self.elevator.doorCloseFlag = True
        self.elevator.currentState = State.stopped_door_opened
        interval = 0.3
        self.elevator.doorInterval = interval
        self.elevator.waitForClosingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,0.0)
        self.assertEqual(self.elevator.currentState, State.stopped_closing_door)
    def test_waitForClosingDoor_openFlag_false_closeFlag_false(self):
        """Test door opened(waiting to close) when openFlag is False, closeFlag is False, and changing status to door closed"""
        self.elevator.doorOpenFlag = False
        self.elevator.doorCloseFlag = False
        self.elevator.currentState = State.stopped_door_opened
        interval = Elevator.elevatorWaitTime - self.elevator.doorSpeed
        self.elevator.doorInterval = interval
        self.elevator.waitForClosingDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertFalse(self.elevator.doorCloseFlag)
        self.assertEqual(self.elevator.doorInterval,0.0)
        self.assertEqual(self.elevator.currentState, State.stopped_closing_door)

    def test_checkTargetFloor_none(self):
        """Test the check target floor functionality: no target floor"""
        self.elevator.currentState = State.stopped_door_closed
        self.elevator.targetFloor = []
        res = self.elevator.checkTargetFloor()
        self.assertFalse(res)
    def test_checkTargetFloor_changeToUp(self): 
        """Test the check target floor functionality: target floor upwards""" 
        self.elevator.currentState = State.stopped_door_closed
        self.elevator.targetFloor = [2]
        self.elevator.currentPos = 1.0
        res = self.elevator.checkTargetFloor()
        self.assertTrue(res)
        self.assertEqual(self.elevator.currentState, State.up)
    def test_checkTargetFloor_changeToDown(self):
        """Test the check target floor functionality: target floor downwards""" 
        self.elevator.currentState = State.stopped_door_closed     
        self.elevator.targetFloor = [2]
        self.elevator.currentPos = 3.0
        res = self.elevator.checkTargetFloor()
        self.assertTrue(res)
        self.assertEqual(self.elevator.currentState, State.down)
    def test_checkTargetFloor_currentFloor(self):
        """Test the check target floor functionality: target floor current"""  
        self.elevator.currentState = State.stopped_door_closed   
        self.elevator.targetFloor = [1]
        self.elevator.currentPos = 1.0
        self.assertTrue(self.elevator.checkTargetFloor())
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)
    def test_checkOpenDoor_openFlag_true(self):
        """Test the check open door functionality"""
        self.elevator.currentState = State.stopped_door_closed
        self.elevator.doorOpenFlag = True
        self.elevator.checkOpenDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertEqual(self.elevator.currentState, State.stopped_opening_door)
    def test_checkOpenDoor_openFlag_false(self):
        """Test the check open door functionality"""
        self.elevator.currentState = State.stopped_door_closed
        self.elevator.doorOpenFlag = False
        self.elevator.checkOpenDoor()
        self.assertFalse(self.elevator.doorOpenFlag)
        self.assertEqual(self.elevator.currentState, State.stopped_door_closed)
    def test_addTargetFloor_alreadyInTheList(self):
        self.elevator.targetFloor = [2]
        self.elevator.addTargetFloor(2)
        self.assertEqual(self.elevator.targetFloor, [2])
    def test_addTargetFloor_firstTimeAdd_Up(self):
        """Test the add target floor functionality"""
        self.elevator.currentDirection = Direction.wait
        self.elevator.targetFloor = []
        self.elevator.currentPos = 1.0
        self.elevator.addTargetFloor(2)
        self.assertEqual(self.elevator.targetFloor, [2])
        self.assertEqual(self.elevator.currentDirection, Direction.up)
    def test_addTargetFloor_firstTimeAdd_Down(self):    
        """Test the add target floor functionality"""
        self.elevator.currentDirection = Direction.wait
        self.elevator.targetFloor = []
        self.elevator.currentPos = 2.0
        self.elevator.addTargetFloor(1)
        self.assertEqual(self.elevator.targetFloor, [1])
        self.assertEqual(self.elevator.currentDirection, Direction.down)
    def test_addTargetFloor_secondTimeAdd_Up(self): 
        """Test the add target floor functionality"""
        self.elevator.currentDirection = Direction.wait
        self.elevator.targetFloor = []
        self.elevator.currentPos = 1.4
        self.elevator.addTargetFloor(2)
        self.elevator.addTargetFloor(3)
        self.assertEqual(self.elevator.targetFloor, [2,3])
        self.assertEqual(self.elevator.currentDirection, Direction.up)
    def test_addTargetFloor_secondTimeAdd_Down(self): 
        """Test the add target floor functionality"""
        self.elevator.currentDirection = Direction.wait
        self.elevator.targetFloor = []
        self.elevator.currentPos = 2.4
        self.elevator.addTargetFloor(1)
        self.elevator.addTargetFloor(2)
        self.assertEqual(self.elevator.targetFloor, [2,1])
        self.assertEqual(self.elevator.currentDirection, Direction.down)
    def test_setOpenDoorFlag(self):
        """Test the set open door flag functionality"""
        self.elevator.setOpenDoorFlag()
        self.assertTrue(self.elevator.doorOpenFlag)
    def test_setCloseDoorFlag(self):
        """Test the set close door flag functionality"""
        self.elevator.setCloseDoorFlag()
        self.assertTrue(self.elevator.doorCloseFlag)

    def test_update(self):
        """Test the update functionality"""
        with patch.object(self.elevator, 'move') as mock_move:
            self.elevator.currentState = State.up
            self.elevator.update()
            mock_move.assert_called_once()
        
        with patch.object(self.elevator, 'openingDoor') as mock_openingDoor:
            self.elevator.currentState = State.stopped_opening_door
            self.elevator.update()
            mock_openingDoor.assert_called_once()
        
        with patch.object(self.elevator, 'waitForClosingDoor') as mock_waitForClosingDoor:
            self.elevator.currentState = State.stopped_door_opened
            self.elevator.update()
            mock_waitForClosingDoor.assert_called_once()
        
        with patch.object(self.elevator, 'closingDoor') as mock_closingDoor:
            self.elevator.currentState = State.stopped_closing_door
            self.elevator.update()
            mock_closingDoor.assert_called_once()
        
        with patch.object(self.elevator, 'checkTargetFloor') as mock_checkTargetFloor:
            self.elevator.currentState = State.stopped_door_closed
            self.elevator.update()
            mock_checkTargetFloor.assert_called_once()



if __name__ == "__main__":
    # app = QApplication(sys.argv)
    unittest.main()
    # app.quit()

