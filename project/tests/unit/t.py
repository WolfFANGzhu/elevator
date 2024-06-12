

    
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

