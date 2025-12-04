from typing import Tuple, List, Optional

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
    used_slots: List[Slot]
    f_cost: int
    g_cost: int
    h_cost: int

    def __init__(self,current_ship, g_cost=0, parent=None, prev_state=None):
        self.state = current_ship
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
                if slot and slot.description not in ("NAN, UNUSED"):
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
        #balance ratio of current node? 
        return 0 #currently Uniform Cost Search, figure out what heuristic to implement. include h=0 vs h(n) in report

    def adjusted_manhattan_distance(self, r1, c1, r2, c2):
        #function must not ghost through containers
        #lift distance + horizontal distance + drop distance
        
        #helper calculation: find tallest intermediate row (exclusive)
        tallest_intermediate_row = -1
        for c in range(c1+1, c2):
            for r in range(SHIP_ROWS):
                slot = self.state[r][c]
                if slot.description != "UNUSED":
                    tallest_intermediate_row = r

        tallest_intermediate_row = max(tallest_intermediate_row, r2)  

        #lift
        if tallest_intermediate_row == -1:
            lift_distance = 0
            curr_row = r1
        else:
            lift_distance = tallest_intermediate_row + 1 - r1
            curr_row = r1 + lift_distance

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
            if lowest_candidate:
                candidate_slots.append((lowest_candidate, c))
            
        #generate successor nodes with candidate_containers and candidate_slots
        for container in candidate_containers:
            for targetR, targetC in candidate_slots:
                if targetC == container.col: #case: available slot is directly above container, invalid movement
                    continue
                
                movement_cost = self.adjusted_manhattan_distance(container.row, container.col, targetR, targetC)
                cumulative_cost = self.g_cost + movement_cost

                new_state = [list(row) for row in self.state] #make list so we can change self.state (mutable)

                new_container = Slot(
                    row = targetR,
                    col = targetC,
                    weight = container.weight,
                    description = container.description
                )

                new_empty = Slot(
                    row = container.row,
                    col = container.col,
                    weight = 0, #is this different from 00000? find out later
                    description = "UNUSED"
                )

                new_state[targetR][targetC] = new_container
                new_state[container.row][container.col] = new_empty

                new_state = tuple(tuple(row) for row in new_state) #convert to tuple for Node generation, immutable

                new_node = Node(
                    new_state,
                    cumulative_cost,
                    parent=self,
                    prev_state=((container.row, container.col),(targetR, targetC)) #sends two tuples of coordinates showing where container moved to
                )

                successors.append(new_node)
        return successors


