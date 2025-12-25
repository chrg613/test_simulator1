from engine import SimulationEngine, SimulationState
from graph_manager import WorldGraph

def run_simulation():
    engine = SimulationEngine()
    world = WorldGraph()
    
    # --- STEP 1: INITIAL STATE ---
    # We manually define the 'Seed' or ask the LLM for Turn 0
    print("🌟 Initializing World...")
    initial_history = "The setting is a high-stakes startup pitch."
    initial_choice = "Begin the presentation."
    
    # Generate first state
    t0_state = engine.generate_next_state(initial_history, initial_choice, turn_id=0)
    current_id = world.add_node(t0_state)

    # --- STEP 2: PLAY LOOP ---
    while True:
        current_state = world.get_state(current_id)
        
        print("\n" + "="*50)
        print(f"TURN {current_state.turn_id}")
        print(f"NARRATIVE: {current_state.narrative_segment}")
        print("-" * 20)
        
        # Display Choices
        for i, action in enumerate(current_state.available_actions):
            print(f"{i+1}. {action}")
        
        # Get User Input
        try:
            choice_idx = int(input("\nChoose an action (number) or '0' to quit: ")) - 1
            if choice_idx == -1: break
            
            selected_action = current_state.available_actions[choice_idx]
        except (ValueError, IndexError):
            print("Invalid choice, try again.")
            continue

        # Get History for this specific branch
        history_context = world.get_history_str(current_id)
        
        # Generate Next State
        print("\n🤖 Gemini is generating the consequence...")
        next_state = engine.generate_next_state(
            history=history_context, 
            user_choice=selected_action,
            turn_id=current_state.turn_id + 1
        )
        
        # Add to Graph
        current_id = world.add_node(next_state, parent_id=current_id, choice_made=selected_action)

if __name__ == "__main__":
    run_simulation()