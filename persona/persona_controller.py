class PersonaController:
    def __init__(self, agent):
        self.agent = agent
        self.current_persona = "mystical"  # Default
        
    def switch_persona(self, user_id: str, new_style: str) -> str:
        """Switch user's interaction style to change persona"""
        
        style_map = {
            'academic': 'academic',
            'scholar': 'academic', 
            'casual': 'casual',
            'friendly': 'casual',
            'mystical': 'mystical',  # Fixed: was 'curious'
            'oracle': 'mystical'
        }
        
        if new_style.lower() in style_map:
            # CRITICAL FIX: Store persona in controller AND update user profile
            self.current_persona = style_map[new_style.lower()]
            
            # Also update user profile for persistence
            if user_id in self.agent.memory_manager.user_profiles:
                self.agent.memory_manager.user_profiles[user_id].interaction_style = self.current_persona
            
            print(f"🎭 Persona switched to: {self.current_persona}")
            return f"✅ Switched to {new_style} persona mode"
        else:
            return f"❌ Unknown persona: {new_style}. Available: academic, casual, mystical"
    
    def get_current_persona(self) -> str:
        """Get current active persona"""
        return self.current_persona
    
    def get_available_personas(self) -> str:
        return """
🎭 **Available Personas:**
- **academic/scholar**: Scholarly, precise, educational tone
- **casual/friendly**: Warm, conversational, storytelling approach  
- **mystical/oracle**: Ethereal, poetic, mystical (default)
        """