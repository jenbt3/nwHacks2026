import google.generativeai as genai
from ..core.config import settings # Use settings instead of os.getenv

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
            if diff.seconds < 3600:
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
            # Note: We use the async-safe call if using a library that supports it, 
            # otherwise standard generate_content is fine for this low-volume project.
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return f"Look, {name} is here to see you." # Safe fallback

# Initialize singleton
gemini_service = GeminiService()