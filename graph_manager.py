import networkx as nx
import uuid
from typing import Optional, List, Dict
from engine import SimulationState # Import your working schema

class WorldGraph:
    def __init__(self):
        # We use DiGraph (Directed Graph) because time/choices flow forward
        self.graph = nx.DiGraph()
        self.root_id: Optional[str] = None

    def add_node(self, state: SimulationState, parent_id: Optional[str] = None, choice_made: Optional[str] = None) -> str:
        """Adds a new state to the graph and links it to its parent."""
        node_id = str(uuid.uuid4())[:8]  # Unique short ID for this 'reality'
        
        # Store the actual Pydantic object inside the node
        self.graph.add_node(node_id, data=state)
        
        if parent_id:
            # The edge represents the 'Choice' that led to this state
            self.graph.add_edge(parent_id, node_id, action=choice_made)
        else:
            self.root_id = node_id
            
        return node_id

    def get_history_str(self, current_node_id: str) -> str:
        """
        Traces the path from root to current node.
        Returns a string for the LLM to understand the context of this specific branch.
        """
        path = nx.shortest_path(self.graph, source=self.root_id, target=current_node_id)
        history_parts = []
        
        for n_id in path:
            state: SimulationState = self.graph.nodes[n_id]['data']
            # We fetch the action that led HERE from the incoming edge
            incoming_edges = self.graph.in_edges(n_id, data=True)
            action = next(iter(incoming_edges))[2].get('action', 'START') if incoming_edges else "START"
            
            history_parts.append(f"Action: {action}\nOutcome: {state.narrative_segment}")
            
        return "\n\n".join(history_parts)

    def get_state(self, node_id: str) -> SimulationState:
        return self.graph.nodes[node_id]['data']