from typing import Tuple, List

SHIP_ROWS = 8
SHIP_COLS = 12

class Slot:
    # SLOT CLASS
    # -------------
    # Represents one individual slot of the 8x12 grid. Row and Col are 0 indexed.
    # Functionality:
    #   Small class, likely some setter/getter functions, print functions for testing
    #   Keeps track of individual slot weight, desc/status, etc

    row: int
    col: int
    weight: int
    description: str

    def __init__(self,row,col,weight,description):
        self.row=row
        self.col=col
        self.weight=weight
        self.description=description

class Node:
    # NODE CLASS
    # -------------
    # Represents state of the entire ship at one moment in time through Tuple[Tuple[Slot]]
    # Functionality:
    #   Initialize with input of Tuple[Tuple[Slot]]
    #   Have a print function for testing purposes/possibly outbound manifets purposes
    #   Have operators for A*
    #   Keep track of costs such as balance ratio, heurtistic manhattan distance, etc
    #   Have transformation/next state function (?)

    state: Tuple[Tuple[Slot]] #immutable
    used_slots: List[Slot] = [] #mutable, slot coordinates may change 

    def __init__(self,current_ship):
        self.state = current_ship
        self.used_slots = self.get_used_slots()
    
    def get_used_slots(self):
        for r in range(SHIP_ROWS):
            for c in range(SHIP_COLS):
                slot = self.state[r][c]
                if slot.description != "NAN" and slot.description != "UNUSED":
                    self.used_slots.append(slot)
        return self.used_slots

    def is_balanced(self):
        portside_weight = 0
        starboard_weight = 0
        
        for slot in self.used_slots:
            if slot.col < 6:
                portside_weight += slot.weight
            else:
                starboard_weight += slot.weight

        total_weight = portside_weight + starboard_weight
        num_used_slots = len(self.used_slots)

        #special case 1/2: Empty or 1-Container Ship
        if num_used_slots == 0 or num_used_slots == 1:
            return True

        #special case 3: 2-Container Ship, Containers on opposite sides
        if num_used_slots == 2:
            if (self.used_slots[0].col < 6 and self.used_slots[1].col >= 6) or (self.used_slots[0].col >= 6 and self.used_slots[1].col < 6):
                return True

        #default case 1: minimal (TO DO)

        #default case 2: 10% variance
        return abs(portside_weight - starboard_weight) < (total_weight * 0.10)
    
    def test_func_print(self):
        for r in range(SHIP_ROWS):
            for c in range(SHIP_COLS):
                slot = self.state[r][c]
                print(f"[{slot.row + 1}, {slot.col + 1}] {slot.weight} {slot.description}") #Does not prepend '0's onto 1-digit coordinates
                print()

