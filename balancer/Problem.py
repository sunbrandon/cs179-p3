import sys
from typing import Tuple, List #is this a repeated import?
from .Node import Node, Slot, SHIP_ROWS, SHIP_COLS

class Problem: 
    # PROBLEM CLASS 
    # -------------
    # Represents entire problem given filename of unedited, initial manifest.
    # Functionality:
    #   Recieve filename input
    #   Read initial manifest, convert to Node form and store in initial_state
    #   Keep track of visited_nodes for A* (?)
    #   Create filenameOUTBOUND.txt
    #   Have some sort of solve() function (?)

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

    def run(self): #solve(), currently just tests if initial input is balanced
        if self.initial_state.is_balanced():
            print("Balanced")
        else:
            print("Unbalanced")
