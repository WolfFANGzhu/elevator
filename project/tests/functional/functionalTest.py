import sys
import unittest
from project.src import Server
import time


def testing_serial(server: Server.ZmqServerThread, msgs: list[str], intervals: list[int]):
    for msg, interval in zip(msgs, intervals):
        server.send_string(server.bindedClient, msg)
        time.sleep(interval)

class FunctionalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the test environment and set class-level variables"""
        cls.my_server = Server.ZmqServerThread()
        while True:
            if len(cls.my_server.clients_addr) == 0:
                continue
            elif len(cls.my_server.clients_addr) >= 2:
                print('more than 1 client address stored. server will exit')
                sys.exit()
            else:
                addr = list(cls.my_server.clients_addr)[0]
                msg = input(f"Initiate evaluation for {addr}?: (y/n)\n")
                if msg == 'y':
                    cls.my_server.bindedClient = addr
                    break
        print("[Test] Test Environment Initialized")

    def setUp(self):
        FunctionalTest.my_server.send_string(FunctionalTest.my_server.bindedClient, "reset")  # Reset the client
        time.sleep(1)

    def tearDown(self):
        """Cleanup after each test case"""
        FunctionalTest.my_server.send_string(FunctionalTest.my_server.bindedClient, "reset")  # Reset the client
        print("_"*50)
        time.sleep(1)
        
    @classmethod
    def tearDownClass(cls):
        """Cleanup work after all test cases are executed"""
        FunctionalTest.my_server.send_string(FunctionalTest.my_server.bindedClient, "reset")
        time.sleep(1)
        print("[Test] Test Environment Cleaned")

    def assert_messages_in_order(self, buffer, expected_msgs):
        buffer_copy = buffer[:]
        for msg in expected_msgs:
            if msg in buffer_copy:
                buffer_copy.remove(msg)
            else:
                self.fail(f"Message '{msg}' not found in buffer")
        return buffer_copy

    def test_freeride(self):
        # Passenger A calls the elevator at 1st floor, select 3rd floor
        # After 1 seconds, passenger B calls the elevator at 2nd floor, want to go up
        # The same elevator should go to 2nd floor and pick him up.
        msgs = ["call_up@1", "select_floor@3#1"]
        intervals = [5, 1]
        testing_serial(FunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@1#1", "up_floor_arrived@1#1", "door_opened#1","door_closed#1"]
        FunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(FunctionalTest.my_server.e1_buffer, expected_msgs)
        msgs =["call_up@2"]
        intervals = [14]
        testing_serial(FunctionalTest.my_server, msgs, intervals)
        expected_msgs = ['floor_arrived@2#1', 'up_floor_arrived@2#1', 'door_opened#1', 
                         'door_closed#1', 'floor_arrived@3#1', 'door_opened#1','door_closed#1']
        FunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(FunctionalTest.my_server.e1_buffer, expected_msgs)
        assert not FunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not FunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_freeride2(self):
        # Passenger A calls the elevator at 1st floor, select 3rd floor
        # After 1.5 seconds, passenger B calls the elevator at 2nd floor, want to go up
        # The elevator 2 should go to 2nd floor and pick him up.
        msgs = ["call_up@1", "select_floor@3#1"]
        intervals = [5, 1.5]
        testing_serial(FunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@1#1", "up_floor_arrived@1#1", "door_opened#1","door_closed#1"]
        FunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(FunctionalTest.my_server.e1_buffer, expected_msgs)
        msgs =["call_up@2", "select_floor@3#2"]
        intervals = [7, 8]
        testing_serial(FunctionalTest.my_server, msgs, intervals)
        expected_msgs = ['floor_arrived@3#1', 'door_opened#1','door_closed#1']
        FunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(FunctionalTest.my_server.e1_buffer, expected_msgs)
        expected_msgs = ['floor_arrived@2#2', 'up_floor_arrived@2#2', 'door_opened#2', 
                         'door_closed#2', 'floor_arrived@3#2', 'door_opened#2','door_closed#2']
        FunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(FunctionalTest.my_server.e2_buffer, expected_msgs)
        assert not FunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not FunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    
    '''
     def test_parallel_moving(self):
        # Passenger A calls the elevator at 1st floor, select 3rd floor
        # After that, passenger B calls the elevator at 2nd floor, want to go down
        # The other elevator should go to 2nd floor
        msgs = ["call_up@1", "call_down@2", "select_floor@3#1", "select_floor@1#2"]
        intervals = [1, 1, 2, 2]
        testing_serial(FunctionalTest.my_server, msgs, intervals)
        time.sleep(20)
        print(FunctionalTest.my_server.e1_buffer)
        print(FunctionalTest.my_server.e2_buffer)
        expected_e1_msgs = ["up_floor_arrived@1#1", "floor_arrived@3#1"]
        expected_e2_msgs = ["floor_arrived@2#2", "down_floor_arrived@2#2"]
        FunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(FunctionalTest.my_server.e1_buffer, expected_e1_msgs)
        FunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(FunctionalTest.my_server.e2_buffer, expected_e2_msgs)

    def test_two_elevators_at_same_floor(self):
        msgs = ["call_up@2", "call_down@2", "call_up@2", "call_down@2"]
        intervals = [0.1, 0.1, 6, 0.1]
        testing_serial(FunctionalTest.my_server, msgs, intervals)
        time.sleep(20)
        print(FunctionalTest.my_server.e1_buffer)
        print(FunctionalTest.my_server.e2_buffer)
        expected_msgs = ["floor_arrived@2#1", "floor_arrived@2#2", "up_floor_arrived@2#1", "down_floor_arrived@2#2"]
        FunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(FunctionalTest.my_server.e1_buffer, expected_msgs)
        FunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(FunctionalTest.my_server.e2_buffer, expected_msgs)
    
    '''
   

if __name__ == '__main__':
    unittest.main()
