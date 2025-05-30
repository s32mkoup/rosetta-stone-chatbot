import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import hashlib
import pickle
from pathlib import Path

@dataclass
class ConversationTurn:
    """Single conversation turn (user input + agent response)"""
    timestamp: datetime
    user_input: str
    agent_response: str
    tools_used: List[str]
    reasoning_trace: Optional[str] = None
    emotional_state: Optional[str] = None
    topics_mentioned: List[str] = None
    
    def __post_init__(self):
        if self.topics_mentioned is None:
            self.topics_mentioned = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationTurn':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

@dataclass
class UserProfile:
    """Persistent user information and preferences"""
    user_id: str
    first_interaction: datetime
    last_interaction: datetime
    total_conversations: int
    favorite_topics: List[str]
    interaction_style: str  # curious, academic, casual, etc.
    preferred_response_length: str  # brief, standard, detailed
    historical_interests: Dict[str, int]  # topic -> frequency count
    language_preference: str = "english"
    
    def update_interests(self, topics: List[str]):
        """Update user's historical interests based on conversation topics"""
        for topic in topics:
            self.historical_interests[topic] = self.historical_interests.get(topic, 0) + 1
        
        # Update favorite topics (top 5 most mentioned)
        sorted_interests = sorted(self.historical_interests.items(), key=lambda x: x[1], reverse=True)
        self.favorite_topics = [topic for topic, _ in sorted_interests[:5]]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['first_interaction'] = self.first_interaction.isoformat()
        data['last_interaction'] = self.last_interaction.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        data['first_interaction'] = datetime.fromisoformat(data['first_interaction'])
        data['last_interaction'] = datetime.fromisoformat(data['last_interaction'])
        return cls(**data)

@dataclass
class StoneMemory:
    """The Rosetta Stone's accumulated "experiences" and memories"""
    memorable_conversations: List[str]  # Summaries of interesting conversations
    learned_connections: Dict[str, List[str]]  # topic -> related topics discovered
    emotional_experiences: List[Tuple[str, str, datetime]]  # (emotion, context, when)
    wisdom_gained: List[str]  # Insights accumulated over time
    favorite_stories: List[str]  # Stories the Stone particularly enjoys telling
    
    def add_memorable_moment(self, summary: str, topics: List[str], emotion: str):
        """Record a memorable conversation moment"""
        self.memorable_conversations.append(summary)
        
        # Update learned connections
        for topic in topics:
            if topic not in self.learned_connections:
                self.learned_connections[topic] = []
            for other_topic in topics:
                if other_topic != topic and other_topic not in self.learned_connections[topic]:
                    self.learned_connections[topic].append(other_topic)
        
        # Record emotional experience
        self.emotional_experiences.append((emotion, summary, datetime.now()))
        
        # Keep only last 50 memorable conversations
        if len(self.memorable_conversations) > 50:
            self.memorable_conversations = self.memorable_conversations[-50:]
    
    def get_related_topics(self, topic: str) -> List[str]:
        """Get topics related to the given topic"""
        return self.learned_connections.get(topic.lower(), [])
    
    def get_emotional_context(self, topic: str) -> Optional[str]:
        """Get emotional context for a topic based on past experiences"""
        for emotion, context, _ in self.emotional_experiences:
            if topic.lower() in context.lower():
                return emotion
        return None

class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, max_short_term: int = 20, max_long_term: int = 100):
        # Short-term memory: recent conversation turns
        self.short_term: deque = deque(maxlen=max_short_term)
        
        # Long-term memory: summarized conversation history
        self.long_term: List[str] = []
        self.max_long_term = max_long_term
        
        # Current conversation context
        self.current_topics: List[str] = []
        self.conversation_start_time = datetime.now()
        self.last_user_intent: Optional[str] = None
        self.conversation_mood: str = "neutral"
    
    def add_turn(self, turn: ConversationTurn):
        """Add a new conversation turn to memory"""
        self.short_term.append(turn)
        
        # Update current topics
        if turn.topics_mentioned:
            for topic in turn.topics_mentioned:
                if topic not in self.current_topics:
                    self.current_topics.append(topic)
        
        # Keep only recent topics (last 10)
        self.current_topics = self.current_topics[-10:]
    
    def get_recent_context(self, turns: int = 5) -> List[ConversationTurn]:
        """Get recent conversation turns for context"""
        return list(self.short_term)[-turns:]
    
    def get_conversation_summary(self) -> str:
        """Generate a summary of the current conversation"""
        if not self.short_term:
            return "No conversation yet."
        
        topics = set()
        tools_used = set()
        
        for turn in self.short_term:
            topics.update(turn.topics_mentioned or [])
            tools_used.update(turn.tools_used)
        
        duration = datetime.now() - self.conversation_start_time
        
        summary = f"Conversation lasted {duration.seconds // 60} minutes. "
        summary += f"Discussed: {', '.join(list(topics)[:5])}. "
        summary += f"Tools used: {', '.join(list(tools_used))}."
        
        return summary
    
    def should_summarize(self) -> bool:
        """Check if conversation should be summarized and moved to long-term memory"""
        return len(self.short_term) >= self.short_term.maxlen * 0.8
    
    def summarize_and_archive(self):
        """Summarize current conversation and move to long-term memory"""
        if self.short_term:
            summary = self.get_conversation_summary()
            self.long_term.append(summary)
            
            # Keep only max_long_term summaries
            if len(self.long_term) > self.max_long_term:
                self.long_term = self.long_term[-self.max_long_term:]
            
            # Clear short-term memory
            self.short_term.clear()
            self.current_topics = []
            self.conversation_start_time = datetime.now()

class MemoryManager:
    """Central memory management system for the Rosetta Stone Agent"""
    
    def __init__(self, config, persistence_path: str = "data/memory/"):
        self.config = config
        self.persistence_path = Path(persistence_path)
        self.persistence_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize memory components
        self.conversation = ConversationMemory(
            max_short_term=config.memory.max_short_term_items,
            max_long_term=config.memory.max_long_term_items
        )
        
        self.user_profiles: Dict[str, UserProfile] = {}
        self.stone_memory = StoneMemory(
            memorable_conversations=[],
            learned_connections={},
            emotional_experiences=[],
            wisdom_gained=[],
            favorite_stories=[]
        )
        
        # Current session info
        self.current_user_id: Optional[str] = None
        self.session_start = datetime.now()
        
        # Load persistent data
        if config.memory.memory_enabled:
            self._load_persistent_memory()
    
    def start_session(self, user_id: str = "default_user"):
        """Start a new conversation session"""
        self.current_user_id = user_id
        self.session_start = datetime.now()
        
        # Load or create user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                first_interaction=datetime.now(),
                last_interaction=datetime.now(),
                total_conversations=0,
                favorite_topics=[],
                interaction_style="curious",
                preferred_response_length="standard",
                historical_interests={}
            )
        else:
            self.user_profiles[user_id].last_interaction = datetime.now()
    
    def add_conversation_turn(self, user_input: str, agent_response: str, 
                            tools_used: List[str], reasoning_trace: Optional[str] = None,
                            emotional_state: Optional[str] = None, 
                            topics_mentioned: Optional[List[str]] = None):
        """Add a new conversation turn to memory"""
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_input=user_input,
            agent_response=agent_response,
            tools_used=tools_used,
            reasoning_trace=reasoning_trace,
            emotional_state=emotional_state,
            topics_mentioned=topics_mentioned or []
        )
        
        # Add to conversation memory
        self.conversation.add_turn(turn)
        
        # Update user profile
        if self.current_user_id and topics_mentioned:
            profile = self.user_profiles[self.current_user_id]
            profile.update_interests(topics_mentioned)
            profile.total_conversations += 1
        
        # Add to Stone's memory if particularly interesting
        if self._is_memorable_conversation(turn):
            self.stone_memory.add_memorable_moment(
                f"Discussed {', '.join(topics_mentioned or [])} with user",
                topics_mentioned or [],
                emotional_state or "neutral"
            )
        
        # Auto-save if enabled
        if self.config.memory.auto_save_conversations:
            self._save_conversation_log(turn)
    
    def get_context_for_response(self) -> Dict[str, Any]:
        """Get relevant context for generating the next response"""
        context = {
            'recent_conversation': self.conversation.get_recent_context(3),
            'current_topics': self.conversation.current_topics,
            'conversation_mood': self.conversation.conversation_mood,
            'user_profile': None,
            'stone_memories': [],
            'related_topics': []
        }
        
        # Add user profile if available
        if self.current_user_id and self.current_user_id in self.user_profiles:
            context['user_profile'] = self.user_profiles[self.current_user_id]
        
        # Add relevant Stone memories
        for topic in self.conversation.current_topics[-3:]:  # Last 3 topics
            memories = [mem for mem in self.stone_memory.memorable_conversations 
                       if topic.lower() in mem.lower()]
            context['stone_memories'].extend(memories[:2])  # Max 2 per topic
            
            # Add related topics
            related = self.stone_memory.get_related_topics(topic)
            context['related_topics'].extend(related[:3])  # Max 3 per topic
        
        return context
    
    def get_personality_context(self) -> Dict[str, Any]:
        """Get context that influences the Stone's personality"""
        return {
            'wisdom_gained': self.stone_memory.wisdom_gained[-5:],  # Recent wisdom
            'favorite_stories': self.stone_memory.favorite_stories,
            'emotional_experiences': [exp for exp in self.stone_memory.emotional_experiences[-10:]],
            'learned_connections': dict(list(self.stone_memory.learned_connections.items())[:10])
        }
    
    def _is_memorable_conversation(self, turn: ConversationTurn) -> bool:
        """Determine if a conversation turn is worth remembering long-term"""
        memorable_criteria = [
            len(turn.tools_used) > 1,  # Used multiple tools
            len(turn.topics_mentioned or []) > 2,  # Multiple topics discussed
            len(turn.agent_response) > 500,  # Detailed response
            turn.emotional_state and turn.emotional_state != "neutral",  # Emotional response
            any(keyword in turn.user_input.lower() for keyword in 
                ['egypt', 'ptolemy', 'hieroglyph', 'ancient', 'pharaoh'])  # Core topics
        ]
        return sum(memorable_criteria) >= 2
    
    def _save_conversation_log(self, turn: ConversationTurn):
        """Save conversation turn to persistent storage"""
        if not self.config.memory.auto_save_conversations:
            return
        
        log_file = self.persistence_path / f"conversation_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(turn.to_dict()) + '\n')
    
    def _load_persistent_memory(self):
        """Load persistent memory from disk"""
        try:
            # Load user profiles
            profiles_file = self.persistence_path / "user_profiles.json"
            if profiles_file.exists():
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    profiles_data = json.load(f)
                    for user_id, profile_data in profiles_data.items():
                        self.user_profiles[user_id] = UserProfile.from_dict(profile_data)
            
            # Load Stone memory
            stone_file = self.persistence_path / "stone_memory.pkl"
            if stone_file.exists():
                with open(stone_file, 'rb') as f:
                    self.stone_memory = pickle.load(f)
                    
        except Exception as e:
            print(f"Warning: Could not load persistent memory: {e}")
    
    def save_persistent_memory(self):
        """Save persistent memory to disk"""
        try:
            # Save user profiles
            profiles_data = {user_id: profile.to_dict() 
                           for user_id, profile in self.user_profiles.items()}
            
            profiles_file = self.persistence_path / "user_profiles.json"
            with open(profiles_file, 'w', encoding='utf-8') as f:
                json.dump(profiles_data, f, indent=2, ensure_ascii=False)
            
            # Save Stone memory
            stone_file = self.persistence_path / "stone_memory.pkl"
            with open(stone_file, 'wb') as f:
                pickle.dump(self.stone_memory, f)
                
        except Exception as e:
            print(f"Warning: Could not save persistent memory: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage"""
        return {
            'short_term_turns': len(self.conversation.short_term),
            'long_term_summaries': len(self.conversation.long_term),
            'user_profiles': len(self.user_profiles),
            'memorable_conversations': len(self.stone_memory.memorable_conversations),
            'learned_connections': len(self.stone_memory.learned_connections),
            'emotional_experiences': len(self.stone_memory.emotional_experiences),
            'current_topics': len(self.conversation.current_topics),
            'session_duration': (datetime.now() - self.session_start).total_seconds() / 60
        }
    
    def clear_session_memory(self):
        """Clear current session memory (keep persistent data)"""
        self.conversation.short_term.clear()
        self.conversation.current_topics = []
        self.conversation.conversation_start_time = datetime.now()
        self.current_user_id = None
    
    def export_conversation_history(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Export conversation history for a user"""
        history = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Read conversation logs
        for log_file in self.persistence_path.glob("conversation_*.jsonl"):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    turn_data = json.loads(line)
                    turn_date = datetime.fromisoformat(turn_data['timestamp'])
                    
                    if turn_date >= cutoff_date:
                        history.append(turn_data)
        
        return sorted(history, key=lambda x: x['timestamp'])