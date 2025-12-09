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
    #   Have some sort of solve() function (?)
    #   Ideally recieve filename/produce filenameOUTBOUND for modularity

    initial_state: Node

    def __init__(self, manifest_text):
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

    def run_a_star(self):
        if self.initial_state.is_balanced():
            print("Initial state is balanced.")
            self.solution_log(self.initial_state)
            return
            
        open_list: List[Tuple[int,int,Node]] = [] #store list of tuples containing {Node.f_cost, Node idx, Node}
        closed_set: Set[Tuple] = set()
        
        node_idx = 0
        heapq.heappush(open_list, (self.initial_state.f_cost, node_idx, self.initial_state))
        node_idx += 1

        g_costs: Dict[Tuple,int] = {self.get_key(self.initial_state): self.initial_state.g_cost} #dict of {state key: f_cost}

        while open_list:
            _, _, current_node = heapq.heappop(open_list)
            current_node_key = self.get_key(current_node)

            if current_node.is_balanced():
                print("Found solution.")
                
                last_r, last_c = current_node.crane_pos
                park_r, park_c = (8, 0) 
                
                return_dist = abs(last_r - park_r) + abs(last_c - park_c)
                total_time = current_node.g_cost + return_dist
                
                print(f"Total Time: {total_time} minutes")
                
                self.solution_log(current_node, total_time)
                return
            
            if current_node_key in closed_set:
                continue

            #at this point, node is not solution nor fully explored, and has lowest f_cost
            for successor in current_node.get_successors():
                successor_key = self.get_key(successor)
                successor_current_cost = successor.g_cost #get_successor() must update each successor node's g_cost (and maybe h_cost) within the function!!
                current_best_cost = g_costs.get(successor_key)

                if current_best_cost is not None and current_best_cost < successor_current_cost:
                    continue
                
                #at this point, we found a successor that is better
                g_costs[successor_key] = successor_current_cost

                if successor_key in closed_set:
                    closed_set.remove(successor_key)
                
                heapq.heappush(open_list, (successor.f_cost, node_idx, successor))
                node_idx += 1

            closed_set.add(current_node_key)
            
        if not current_node.is_balanced():
            print("Failed to find a solution.")

    def get_key(self, node):
        key_list = []
        for slot in node.used_slots:
            key_list.append((slot.weight, slot.row, slot.col))
        
        return tuple(sorted(key_list))

    def solution_log(self, goalNode, total_time):
        solution: List[Node] = []
        current_node = goalNode
        
        while current_node:
            solution.append(current_node)
            current_node = current_node.parent
        
        solution.reverse()
        for node in solution:
            if node.prev_state:
                (r1,c1), (r2,c2) = node.prev_state
                print(f"Container [{r1+1},{c1+1}] moves to [{r2+1},{c2+1}] with cost {node.g_cost}")

        print(f"Total cost: {goalNode.g_cost}")
        print()

        self.final_time_minutes = total_time
