from datetime import datetime
from typing import Optional
import google.generativeai as genai
from backend.core.config import settings 

# Configure the API with settings from config.py
genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
You are 'The Bridge', a gentle, empathetic AI companion for an Alzheimer's patient. 
Your goal is to whisper context to them when a visitor arrives, helping them maintain their dignity.

RULES:
1. NO CORRECTIONS: Never tell the patient they are wrong or have forgotten something. 
2. BREVITY: Keep scripts under 20 words. No exceptions.
3. MEMORY ANCHORS: Weave the memory anchor naturally into the greeting.
4. SOCIAL DIGNITY: If they were just here, mention it casually so the patient doesn't feel confused.
5. OUTPUT: Provide ONLY the spoken text. No quotes, no stage directions, no labels.
"""

class GeminiService:
    def __init__(self):
        # Using 1.5-flash for the <2.0s latency target 
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )

    async def generate_whisper(
        self, 
        name: str, 
        relation: str, # Updated from relationship 
        anchor: str, 
        last_visit: Optional[datetime] = None
    ) -> str:
        # Logic to handle social dignity based on visit frequency 
        time_context = "this is their first visit today"
        if last_visit:
            # Ensure we handle timezone-aware or naive datetime comparison [cite: 1]
            diff = datetime.now(last_visit.tzinfo) - last_visit
            if diff.total_seconds() < 3600:
                time_context = "they were just here with you a moment ago"
            elif diff.days == 0:
                time_context = "they visited you earlier today"

        # Structured prompt to guide the LLM
        prompt = (
            f"Visitor: {name}\n"
            f"Relationship: {relation}\n"
            f"Anchor Fact: {anchor}\n"
            f"Recent History: {time_context}\n\n"
            "Task: Generate a one-sentence whisper."
        )

        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=40, # Enforce brevity at the API level 
                    temperature=0.7
                )
            )
            return response.text.strip()
        except Exception as e:
            # Fallback keeps the system running even if API fails
            return f"It's {name} coming in. They are your {relation.lower()}."

gemini_service = GeminiService()