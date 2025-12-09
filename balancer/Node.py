from typing import Tuple, List, Optional

SHIP_ROWS = 8
SHIP_COLS = 12

PARK_ROW = 8 
PARK_COL = 0

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
    crane_pos: Tuple[int, int]
    used_slots: List[Slot]
    f_cost: int
    g_cost: int
    h_cost: int

    def __init__(self,current_ship, crane_pos=(PARK_ROW, PARK_COL), g_cost=0, parent=None, prev_state=None):
        self.state = current_ship
        self.crane_pos = crane_pos
        self.used_slots = self.get_used_slots()
        self.g_cost = g_cost
        self.h_cost = self.calculate_h_cost()
        self.f_cost = self.g_cost + self.h_cost
        self.parent = parent
        self.prev_state = prev_state
    
    def get_used_slots(self):
        used_slots: List[Slot] = []
        for r in range(SHIP_ROWS):
            for c in range(SHIP_COLS):
                slot = self.state[r][c]
                if slot and slot.description not in ("NAN", "UNUSED"):
                    used_slots.append(slot)
        return used_slots

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
        # for r in range(SHIP_ROWS):
        #     for c in range(SHIP_COLS):
        #         slot = self.state[r][c]
        #         print(f"[{slot.row + 1}, {slot.col + 1}] {slot.weight} {slot.description}") #Does not prepend '0's onto 1-digit coordinates
        #         print()
        for slot in self.used_slots:
            print(f"[{slot.row + 1}, {slot.col + 1}] {slot.weight} {slot.description}")
            print()

    def calculate_h_cost(self):
        #lower h is better
        
        portside_weight = 0
        starboard_weight = 0
        portside_containers = []
        starboard_containers = []
        h = 0

        #weigh each side, separate
        for slot in self.used_slots:
            if slot.col < 6:
                portside_weight += slot.weight
                portside_containers.append(slot)
            else:
                starboard_weight += slot.weight
                starboard_containers.append(slot)
        
        deficit =  abs(portside_weight - starboard_weight)
        
        #no difference in weight is good
        if deficit == 0: 
            return 0

        if (portside_weight > starboard_weight):
            heavy = portside_containers
            col_range = range(6, 12) #opposite side range
        else:
            heavy = starboard_containers
            col_range = range(0, 6) #opposite side range
        
        heavy_sorted = sorted(heavy, key=lambda container: container.weight, reverse=True)
        leftover_deficit = deficit

        for container in heavy_sorted:
            if leftover_deficit <= 0:
                break
            
            h += min(abs(container.col - c) for c in col_range)
            leftover_deficit -= container.weight
            
        return h

        #return 0 #currently Uniform Cost Search

    def adjusted_manhattan_distance(self, r1, c1, r2, c2):
        #function must not ghost through containers
        #lift distance + horizontal distance + drop distance
        
        #helper calculation: find tallest intermediate row (exclusive)
        tallest_intermediate_row = -1

        start_c = min(c1,c2)
        end_c = max(c1,c2)

        for c in range(start_c+1, end_c):
            for r in range(SHIP_ROWS):
                slot = self.state[r][c]
                if slot.description != "UNUSED":
                    tallest_intermediate_row = max(tallest_intermediate_row,r)

        #lift

        if r1 >= tallest_intermediate_row + 1:
            lift_distance = 0
            curr_row = r1
        else:
            lift_distance = tallest_intermediate_row + 1 - r1
            curr_row = tallest_intermediate_row + 1

        #horizontal
        horizontal_distance = abs(c2 - c1) #min value = 0 (no move)

        #drop
        drop_distance =  curr_row - r2

        return lift_distance + horizontal_distance + drop_distance

    def get_successors(self):
        successors: List[Node] = [] #successors is a list of nodes

        #what containers can move? containers that exist and have nothing above them (topmost) per column
        candidate_containers: List[Slot] = []

        #where can valid containers move? UNUSED slots, not NAN slots. Only in the lowest unused row per column
        candidate_slots: List[Tuple[int,int]] = [] #just list the row and col, don't need other slot info

        #iterate through each column, searching for candidate containers or slots from node state
        for c in range(SHIP_COLS):
            #check rows
            topmost_container = None
            lowest_candidate = None

            for r in range(SHIP_ROWS):
                slot = self.state[r][c]
                
                if slot.description not in ("UNUSED", "NAN"):
                    topmost_container = slot  #will continously update as rows increase
                elif slot.description == "UNUSED" and lowest_candidate is None: #first open row found
                    lowest_candidate = r

            if topmost_container: 
                candidate_containers.append(topmost_container)
            if lowest_candidate is not None:
                candidate_slots.append((lowest_candidate, c))
            
        #generate successor nodes with candidate_containers and candidate_slots
        for container in candidate_containers:
            for targetR, targetC in candidate_slots:
                if targetC == container.col:
                    continue

                curr_crane_r, curr_crane_c = self.crane_pos
                crane_travel_dist = abs(curr_crane_r - container.row) + abs(curr_crane_c - container.col)
                
                move_dist = self.adjusted_manhattan_distance(container.row, container.col, targetR, targetC)
                
                step_cost = crane_travel_dist + move_dist
                cumulative_cost = self.g_cost + step_cost

                new_state = [list(row) for row in self.state]
                
                new_container = Slot(targetR, targetC, container.weight, container.description)
                new_empty = Slot(container.row, container.col, 0, "UNUSED")
                
                new_state[targetR][targetC] = new_container
                new_state[container.row][container.col] = new_empty
                
                new_state_tuple = tuple(tuple(row) for row in new_state)

                new_node = Node(
                    new_state_tuple,
                    crane_pos=(targetR, targetC), 
                    g_cost=cumulative_cost,
                    parent=self,
                    prev_state=((container.row, container.col), (targetR, targetC))
                )

                successors.append(new_node)
        
        return successors
