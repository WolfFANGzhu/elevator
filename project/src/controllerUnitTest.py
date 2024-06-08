import sys
import unittest
from unittest.mock import Mock, patch
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QWidget
from elevatorController import ElevatorController
from elevator import Elevator
from elevatorState import State
from direction import Direction 
import NetClient

class ElevatorControllerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test environment and set class-level variables"""
        cls.app = QApplication(sys.argv)
        pass
    def setUp(self):
        self.zmqThread = Mock(spec=NetClient.ZmqClientThread)
        self.elevator1 = Elevator(1,self.zmqThread)
        self.elevator2 = Elevator(2,self.zmqThread)
        self.controller = ElevatorController(self.zmqThread, self.elevator1, self.elevator2)
        # window 1~3 are the windows for the outside panel 
        self.window1 = QWidget()
        self.window2 = QWidget()
        self.window3 = QWidget()  
        self.simulation_window = QWidget() 
        self.controller = ElevatorController(self.zmqThread,self.elevator1,self.elevator2)
        self.controller.create_window(self.window1,"f1", up=True, down=False)
        self.controller.create_window(self.window2,"f2", up=True, down=True)
        self.controller.create_window(self.window3,"f3", up=False, down=True)
        self.controller.create_simulation_window(self.simulation_window)
        self.controller.create_button_dict()
        self.controller.connect()
        self.window1.show()
        self.window2.show()
        self.window3.show()
        self.simulation_window.show()
        self.elevator1.show()
        self.elevator2.show()
    def tearDown(self):
        """Cleanup after each test case"""
        self.elevator1.close()
        self.elevator2.close()
        self.window1.close()
        self.window2.close()
        self.window3.close()
        self.simulation_window.close()
    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        # Ensure the event loop runs long enough to display the window
        QTest.qWait(1000)  # Delay 1 second to ensure the window is displayed
        cls.app.quit()
        pass
    def test_parseInput_open_door_1(self):
        self.controller.parseInput("open_door#1")
        self.assertTrue(self.elevator1.doorOpenFlag)

    def test_parseInput_open_door_2(self):
        self.controller.parseInput("open_door#2")
        self.assertTrue(self.elevator2.doorOpenFlag)

    def test_parseInput_close_door_1(self):
        self.controller.parseInput("close_door#1")
        self.assertTrue(self.elevator1.doorCloseFlag)

    def test_parseInput_close_door_2(self):
        self.controller.parseInput("close_door#2")
        self.assertTrue(self.elevator2.doorCloseFlag)

    def test_parseInput_call_up_1(self):
        self.controller.parseInput("call_up@1")
        self.assertEqual(self.controller.button_dict["1_up"]["state"],"pressed")
    def test_parseInput_call_up_2(self):
        self.controller.parseInput("call_up@2")
        self.assertEqual(self.controller.button_dict["2_up"]["state"],"pressed")
    def test_parseInput_call_down_2(self):
        self.controller.parseInput("call_down@2")
        self.assertEqual(self.controller.button_dict["2_down"]["state"],"pressed")
    def test_parseInput_call_up_2(self):
        self.controller.parseInput("call_down@3")
        self.assertEqual(self.controller.button_dict["3_down"]["state"],"pressed")
    def test_parseInput_select_floor_e1_1(self):
        self.controller.parseInput("select_floor@1#1")
        self.assertEqual(self.elevator1.f1_activeFlag,True)
    def test_parseInput_select_floor_e1_2(self):
        self.controller.parseInput("select_floor@2#1")
        self.assertEqual(self.elevator1.f2_activeFlag,True)
    def test_parseInput_select_floor_e1_3(self):
        self.controller.parseInput("select_floor@3#1")
        self.assertEqual(self.elevator1.f3_activeFlag,True)
    def test_parseInput_select_floor_e2_1(self):
        self.controller.parseInput("select_floor@1#2")
        self.assertEqual(self.elevator2.f1_activeFlag,True)
    def test_parseInput_select_floor_e2_2(self):
        self.controller.parseInput("select_floor@2#2")
        self.assertEqual(self.elevator2.f2_activeFlag,True)
    def test_parseInput_select_floor_e2_3(self):
        self.controller.parseInput("select_floor@3#2")
        self.assertEqual(self.elevator2.f3_activeFlag,True)
    def test_parseInput_reset(self):
        # Init some state
        self.elevator1.currentPos = 3.0
        self.elevator1.addTargetFloor(1)
        self.controller.button_dict["1_up"]["state"] = "pressed"
        self.controller.parseInput("reset")
        self.assertEqual(self.elevator1.currentPos,1.0)
        self.assertEqual(self.controller.button_dict["1_up"]["state"],"not pressed")
        self.assertEqual(self.elevator1.targetFloor,[])
    def test_reset(self):
        # Init some state
        self.elevator1.currentPos = 3.0
        self.elevator1.addTargetFloor(1)
        self.controller.button_dict["1_up"]["state"] = "pressed"
        self.controller.reset()
        self.assertEqual(self.elevator1.currentPos,1.0)
        self.assertEqual(self.controller.button_dict["1_up"]["state"],"not pressed")
        self.assertEqual(self.elevator1.targetFloor,[])


    def test_getNearestStopElevator_e1_m_e2_s(self):
        # First elevator is moving, second is stopped with no targets
        self.elevator1.currentState = State.up
        self.elevator1.targetFloor = [3]
        self.elevator1.currentPos = 2.1
        self.elevator2.currentState = State.stopped_door_closed
        self.elevator2.targetFloor = []
        self.elevator2.currentPos = 1.0
        eid = self.controller.getNearestStopElevator(2)
        self.assertEqual(eid, 0)

    def test_getNearestStopElevator_e1_s_e2_m(self):
        # First elevator is stopped with no targets, second is not stopped door closed
        self.elevator1.currentState = State.stopped_door_closed
        self.elevator1.targetFloor = []
        self.elevator1.currentPos = 3.0
        self.elevator2.currentState = State.stopped_closing_door
        self.elevator2.targetFloor = []
        self.elevator2.currentPos = 1.0
        eid = self.controller.getNearestStopElevator(1)
        self.assertEqual(eid, 1)

    def test_getNearestStopElevator_e1_m_e2_m(self):
        # Both elevators are moving
        self.elevator1.currentState = State.up
        self.elevator1.targetFloor = [3]
        self.elevator1.currentPos = 1.0
        self.elevator2.currentState = State.down
        self.elevator2.targetFloor = [1]
        self.elevator2.currentPos = 3.0
        eid = self.controller.getNearestStopElevator(2)
        self.assertEqual(eid, -1)

    def test_getNearestStopElevator_e1_s_e2_s(self):
        # Both elevators are at equal distance and stopped with no targets
        # Both elevators are moving
        self.elevator1.currentState = State.stopped_door_closed
        self.elevator1.targetFloor = []
        self.elevator1.currentPos = 1.0
        self.elevator2.currentState = State.stopped_door_closed
        self.elevator2.targetFloor = []
        self.elevator2.currentPos = 1.0
        eid = self.controller.getNearestStopElevator(1)
        self.assertEqual(eid, 0)
    

    def test_update_msgNotEmpty(self):
        # Test when msg is not empty
        pass

    def test_update_NotPressedWithEid(self):
        # Test when button state is 'not pressed'
        pass
    def test_update_NotPressedWithoutEid(self):
        # Test when button state is 'not pressed'
        pass

    def test_update_PressedWithEid(self):
        # Test when button state is 'pressed' and elevator_id is not -1
        pass

    def test_update_PressedWithOutEid(self):
        # Test when button state is 'pressed' and elevator_id is -1
        pass

    def test_update_WaitingArrive(self):
        # Test when button state is 'waiting'
        pass
if __name__ == '__main__':
    unittest.main()