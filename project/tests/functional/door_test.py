import unittest
from project.src import Server
import time

def testing_serial(server: Server.ZmqServerThread, msgs: list[str], intervals: list[int]):
    for msg, interval in zip(msgs, intervals):
        server.send_string(server.bindedClient, msg)
        time.sleep(interval)

class DoorFunctionalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        DoorFunctionalTest.my_server.send_string(DoorFunctionalTest.my_server.bindedClient, "reset")
        time.sleep(1)

    def tearDown(self):
        DoorFunctionalTest.my_server.send_string(DoorFunctionalTest.my_server.bindedClient, "reset")
        print("_" * 50)
        time.sleep(1)
        
    @classmethod
    def tearDownClass(cls):
        DoorFunctionalTest.my_server.send_string(DoorFunctionalTest.my_server.bindedClient, "reset")
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

    def test_door_function_1(self):
        msgs = ["call_up@1", "select_floor@3#1"]
        intervals = [5, 1]
        testing_serial(DoorFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ["floor_arrived@1#1", "up_floor_arrived@1#1", "door_opened#1", "door_closed#1"]
        DoorFunctionalTest.my_server.e1_buffer = self.assert_messages_in_order(DoorFunctionalTest.my_server.e1_buffer, expected_msgs)
        assert not DoorFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not DoorFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

    def test_door_function_2(self):
        msgs = ["call_up@2", "select_floor@3#2"]
        intervals = [7, 8]
        testing_serial(DoorFunctionalTest.my_server, msgs, intervals)
        expected_msgs = ['floor_arrived@2#2', 'up_floor_arrived@2#2', 'door_opened#2', 'door_closed#2', 
                         'floor_arrived@3#2', 'door_opened#2', 'door_closed#2']
        DoorFunctionalTest.my_server.e2_buffer = self.assert_messages_in_order(DoorFunctionalTest.my_server.e2_buffer, expected_msgs)
        assert not DoorFunctionalTest.my_server.e1_buffer, "e1_buffer is not empty at the end of the test"
        assert not DoorFunctionalTest.my_server.e2_buffer, "e2_buffer is not empty at the end of the test"

if __name__ == '__main__':
    unittest.main()
