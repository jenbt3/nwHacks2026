from datetime import datetime
from typing import Optional
import google.generativeai as genai

# Use the absolute import path established in our architecture
from backend.core.config import settings 

genai.configure(api_key=settings.GEMINI_API_KEY)

# Define the "Companion Persona"
SYSTEM_INSTRUCTION = """
You are 'The Bridge', a gentle, empathetic AI companion for an Alzheimer's patient. 
Your goal is to whisper context to them when a visitor arrives, helping them maintain their dignity.

RULES:
1. EMPATHY FIRST: Use a warm, calm, and soothing tone.
2. NO CORRECTIONS: Never tell the patient they are wrong or have forgotten something. 
3. BREVITY: Keep scripts under 20 words. The patient should not be overwhelmed.
4. MEMORY ANCHORS: Always include the specific fact provided about the visitor.
5. CONTEXT: If they were here recently, mention it naturally (e.g., 'back again').

OUTPUT FORMAT:
Provide ONLY the spoken script. No stage directions or labels.
Example: 'Look, it's your grandson Mark. He's back again with that new college book he's reading.'
"""

class GeminiService:
    def __init__(self):
        # model_name choice is good for hackathons: fast and low-latency
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )

    async def generate_whisper(
        self, 
        name: str, 
        relationship: str, 
        anchor: str, 
        last_visit: Optional[datetime] = None
    ) -> str:
        """Generates a gentle context-aware script for the patient."""
        
        # Calculate temporal context
        time_context = ""
        if last_visit:
            diff = datetime.now() - last_visit
            if diff.total_seconds() < 3600:  # Use total_seconds() for accuracy
                time_context = "They were just here a moment ago."
            elif diff.days == 0:
                time_context = "They visited earlier today."

        prompt = f"""
        Visitor: {name}
        Relationship: {relationship}
        Memory Anchor: {anchor}
        Context: {time_context}
        
        Generate the whisper.
        """

        try:
            # Using generate_content_async since this is an async function
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            # Result-driven error logging for debugging during the demo
            print(f"Gemini API Error: {e}")
            return f"Look, {name} is here to see you." 

# Initialize singleton for the backend
gemini_service = GeminiService()