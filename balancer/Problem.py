import sys
import heapq
from typing import Tuple, List, Dict #is this a repeated import?
from .Node import Node, Slot, SHIP_ROWS, SHIP_COLS

class Problem: 
    # PROBLEM CLASS 
    # -------------
    # Represents entire problem given filename of unedited, initial manifest.
    # Functionality:
    #   Receive manifest text input
    #   Read initial manifest, convert to Node form and store in initial_state
    #   Keep track of visited_nodes for A* (?)
    #   Have some sort of solve() function (?)
    #   Ideally recieve filename/produce filenameOUTBOUND for modularity

    initial_state: Node
    visited_nodes: List[Node] #mutable

    def __init__(self, manifest_text):
        #self.visited_nodes = # can we initialize to first state here?
        self.initial_state = self.create_initial_node(manifest_text)

    def read_initial_manifest(self, manifest_text):
        ship_state: List[List[Slot|None]] = [[None for _ in range(SHIP_COLS)] for _ in range(SHIP_ROWS)]
        slots_count = 0

        for line in manifest_text.splitlines():
            line = line.strip()
                    
            try:
                parts = line.split(',')
                row = int(parts[0].strip('[')) - 1
                col = int(parts[1].strip(']')) - 1
                weight = int(parts[2].strip().strip('{').strip('}'))
                description = parts[3].strip()
                            
                slot = Slot(
                    row=row,
                    col=col,
                    weight=weight,
                    description=description
                )

            except Exception as error:
                continue

            ship_state[slot.row][slot.col] = slot
            slots_count += 1
            
        ship_tuple = tuple(tuple(s) for s in ship_state)
        return ship_tuple
        
    def create_initial_node(self, manifest_text):
        initial_manifest = self.read_initial_manifest(manifest_text)
        return Node(initial_manifest)

    def run_a_star(self): #solve(), currently just tests if initial input is balanced
        if self.initial_state.is_balanced():
            print("Initial state is balanced.")

        open_list: List[Tuple[int,int,Node]] #store list of tuples containing {Node.f_cost, Node}
        closed_set: Set[Tuple] = set()
        
        node_idx = 0
        heapq.heappush(open_list, (self.initial_state.f_cost, node_idx, self.initial_state))
        node_idx += 1

        f_costs: Dict[Tuple,int] = {self.get_key(self.initial_state): self.initial_state.f_cost} #dict of {state key: f_cost}

        while open_list:
            _, _, current_node = heapq.heappop(open_list)
            current_node_key = self.get_key(current_node)

            if current_node.is_balanced():
                print("Found solution.")
                break
            
            if current_node_key in closed_set:
                continue
            
            #at this point, node is not solution nor fully explored, and has lowest f_cost
            for successor in current_node.get_successors():
                successor_key = self.get_key(successor)
                successor_current_cost = successor.f_cost #get_successor() must update each successor node's g_cost (and maybe h_cost) within the function!!
                current_best_cost = f_costs.get(successor_key)

                if current_best_cost is not None and current_best_cost < successor_current_cost:
                    continue
                
                #at this point, we found a successor that is better
                f_costs[successor_key] = successor_current_cost

                if successor_key in closed_set:
                    closed_set.remove(successor_key)
                
                heapq.heappush(open_list, (successor.f_cost, node_idx, successor))
                node_idx += 1

            closet_set.add(current_node_key)

        if not current_node.is_balanced():
            print("Failed to find a solution.")

    def get_key(self, node):
        key_list = []
        for slot in node.used_slots:
            key_list.append(slot.weight, slot.row, slot.col)
        
        return tuple(sorted(key_list))


                




        

