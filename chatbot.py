import ollama
import json
from pydantic import ValidationError, BaseModel, Field
from typing import Literal, Optional
from prompts import EXTRACTION_PROMPT_BASE, CLARIFICATION_PROMPT, DEPT_RESPONSE_PROMPT

# Define models here to avoid import issues
class ExtractionPayload(BaseModel):
    department: Literal['Revenue', 'Police', 'Health', 'Education', 'Transport', 'Agriculture', None] = Field(
        description="Exact department match or None if unclear"
    )
    prompt: str = Field(description="Cleaned user query")

class GovernmentChatbot:
    def __init__(self, model="gemma3:4b"):
        self.model = model
        self.history = []

    def extract_payload(self, user_input: str) -> ExtractionPayload:
        """Step 1: Extract department & prompt with structured output."""
        # Replace placeholder with actual user input
        prompt = EXTRACTION_PROMPT_BASE.replace("USER_INPUT_PLACEHOLDER", user_input)
        
        print(f"DEBUG: Sending prompt to Ollama...")
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            format=ExtractionPayload.model_json_schema()
        )
        
        try:
            content = response['message']['content']
            payload = ExtractionPayload.model_validate_json(content)
            print(f"DEBUG: Extracted {payload.dict()}") 
            return payload
        except (ValidationError, KeyError, json.JSONDecodeError) as e:
            print(f"Extraction failed: {e}. Using fallback.", file=sys.stderr)
            return ExtractionPayload(department=None, prompt=user_input)

    def needs_clarification(self, payload: ExtractionPayload) -> str:
        if payload.department is None:
            return CLARIFICATION_PROMPT.format(prompt=payload.prompt)
        return None

    def generate_response(self, payload: ExtractionPayload) -> str:
        dept_prompt = DEPT_RESPONSE_PROMPT.format(
            department=payload.department,
            prompt=payload.prompt
        )
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": dept_prompt}]
        )
        return response['message']['content']

    def process(self, user_input: str) -> str:
        payload = self.extract_payload(user_input)
        clarification = self.needs_clarification(payload)
        
        if clarification:
            return clarification
        else:
            return self.generate_response(payload)

def main():
    bot = GovernmentChatbot()
    print("GovChatBot ready! (Type 'quit' to exit)")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit']:
            break
        
        if not user_input:
            continue
            
        response = bot.process(user_input)
        print(f"\nBot: {response}")

if __name__ == "__main__":
    main()
