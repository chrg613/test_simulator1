import vertexai
from vertexai.generative_models import GenerativeModel
from pydantic import BaseModel, Field, ValidationError
from typing import List


# -------------------------------
# 1. DATA SCHEMA
# -------------------------------

class Entity(BaseModel):
    name: str
    role: str
    mood: str


class SimulationState(BaseModel):
    turn_id: int
    narrative_segment: str
    entities: List[Entity]
    available_actions: List[str] = Field(min_length=2, max_length=3)


# -------------------------------
# 2. SIMULATION ENGINE
# -------------------------------

class SimulationEngine:
    def __init__(self):
        vertexai.init(
            project="project_id_here",
            location="us-central1"
        )
        # Vertex-supported model
        self.model = GenerativeModel("gemini-2.5-flash")

    def generate_next_state(
        self,
        history: str,
        user_choice: str,
        turn_id: int = 1
    ) -> SimulationState:

        # IMPORTANT: All braces are ESCAPED ({{ }}) because this is an f-string
        prompt = f"""
You are a simulation engine.

Return ONLY valid JSON.
Do NOT include explanations.
Do NOT include markdown.
Do NOT add or remove fields.

The JSON MUST match this schema EXACTLY:

{{
  "turn_id": number,
  "narrative_segment": string,
  "entities": [
    {{
      "name": string,
      "role": string,
      "mood": string
    }}
  ],
  "available_actions": [string, string]
}}

Example output:
{{
  "turn_id": {turn_id},
  "narrative_segment": "The judges exchange glances as the room falls silent.",
  "entities": [
    {{ "name": "Lead Judge", "role": "judge", "mood": "curious" }},
    {{ "name": "Angel Investor", "role": "investor", "mood": "impressed" }}
  ],
  "available_actions": ["Answer confidently", "Wait silently"]
}}

Current History:
{history}

User Choice:
{user_choice}

Generate the next state now.
"""

        response = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        raw_json = response.text

        try:
            return SimulationState.model_validate_json(raw_json)
        except ValidationError as e:
            print("\n❌ MODEL RETURNED INVALID JSON")
            print("RAW OUTPUT:")
            print(raw_json)
            raise e


# -------------------------------
# 3. TEST RUN
# -------------------------------

if __name__ == "__main__":
    engine = SimulationEngine()

    history = "You are at a startup pitch competition. You just finished your presentation."
    choice = "Wait for the judges to speak."

    print("🤖 Reality Engine is thinking...\n")

    next_state = engine.generate_next_state(history, choice, turn_id=1)

    print(f"[Turn {next_state.turn_id}]")
    print("STORY:", next_state.narrative_segment)
    print("NPCS:", [f"{e.name} is {e.mood}" for e in next_state.entities])
    print("CHOICES:", next_state.available_actions)
