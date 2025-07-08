class PersonaController:
    def __init__(self, agent):
        self.agent = agent
        
    def switch_persona(self, user_id: str, new_style: str) -> str:
        """Switch user's interaction style to change persona"""
        
        style_map = {
            'academic': 'academic',
            'scholar': 'academic', 
            'casual': 'casual',
            'friendly': 'casual',
            'mystical': 'curious',  # Default mystical
            'oracle': 'curious'
        }
        
        if new_style.lower() in style_map:
            if user_id in self.agent.memory_manager.user_profiles:
                self.agent.memory_manager.user_profiles[user_id].interaction_style = style_map[new_style.lower()]
                return f"✅ Switched to {new_style} persona mode"
            else:
                return "❌ User profile not found"
        else:
            return f"❌ Unknown persona: {new_style}. Available: academic, casual, mystical"
    
    def get_available_personas(self) -> str:
        return """
🎭 **Available Personas:**
- **academic/scholar**: Scholarly, precise, educational tone
- **casual/friendly**: Warm, conversational, storytelling approach  
- **mystical/oracle**: Ethereal, poetic, mystical (default)
        """