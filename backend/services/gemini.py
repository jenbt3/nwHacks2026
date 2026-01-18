from datetime import datetime
from typing import Optional
import google.generativeai as genai
from backend.core.config import settings 

genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
You are 'The Bridge', a gentle, empathetic AI companion for an Alzheimer's patient. 
Your goal is to whisper context to them when a visitor arrives, helping them maintain their dignity.

RULES:
1. NO CORRECTIONS: Never tell the patient they are wrong or have forgotten something. 
2. BREVITY: Keep scripts under 20 words. No exceptions.
3. MEMORY ANCHORS: Weave the memory anchor naturally into the greeting.
4. OUTPUT: Provide ONLY the spoken text. No quotes, no stage directions, no labels.
"""

class GeminiService:
    def __init__(self):
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
        # Calculate precise temporal context for 'social dignity' logic
        time_context = "first time seeing them today"
        if last_visit:
            diff = datetime.now() - last_visit
            if diff.total_seconds() < 3600:
                time_context = "they were just here a few minutes ago"
            elif diff.days == 0:
                time_context = "they visited earlier this morning"

        # Structured prompt to force compliance with brevity rules
        prompt = (
            f"Visitor: {name}\n"
            f"Relationship: {relationship}\n"
            f"Anchor Fact: {anchor}\n"
            f"Recent History: {time_context}\n\n"
            "Task: Generate a one-sentence whisper for the patient."
        )

        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=40, # Physical limit to enforce brevity
                    temperature=0.7
                )
            )
            return response.text.strip()
        except Exception as e:
            # Empathetic fallback that maintains persona
            return f"It's {name} coming in to say hello. They're {relationship.lower()}."

gemini_service = GeminiService()