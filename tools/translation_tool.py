import re
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import unicodedata

from .tool_registry import BaseTool, ToolMetadata, ToolCategory, ToolComplexity

class ScriptType(Enum):
    """Types of scripts the tool can handle"""
    HIEROGLYPHIC = "hieroglyphic"
    DEMOTIC = "demotic"
    ANCIENT_GREEK = "ancient_greek"
    COPTIC = "coptic"
    LATIN = "latin"
    MODERN_GREEK = "modern_greek"
    ARABIC = "arabic"

class TranslationType(Enum):
    """Types of translation operations"""
    SCRIPT_TO_TRANSLITERATION = "script_to_transliteration"
    TRANSLITERATION_TO_MEANING = "transliteration_to_meaning"
    MEANING_TO_HIEROGLYPH = "meaning_to_hieroglyph"
    SCRIPT_IDENTIFICATION = "script_identification"
    HISTORICAL_CONTEXT = "historical_context"

@dataclass
class TranslationResult:
    """Result of a translation operation"""
    original_text: str
    source_script: ScriptType
    target_format: str
    translated_text: str
    transliteration: Optional[str]
    meaning: Optional[str]
    confidence: float
    notes: List[str]
    historical_context: Optional[str]
    related_symbols: List[str]
    
    def __post_init__(self):
        if self.notes is None:
            self.notes = []
        if self.related_symbols is None:
            self.related_symbols = []

@dataclass
class HieroglyphicSymbol:
    """Individual hieroglyphic symbol information"""
    symbol: str
    unicode_code: str
    transliteration: str
    meaning: str
    category: str  # phonetic, ideographic, determinative
    frequency: str  # common, uncommon, rare
    historical_period: str
    pronunciation_guide: str
    related_symbols: List[str]
    
    def __post_init__(self):
        if self.related_symbols is None:
            self.related_symbols = []

class TranslationTool(BaseTool):
    """Advanced tool for translating and interpreting ancient scripts, especially those on the Rosetta Stone"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Initialize script databases
        self.hieroglyph_dictionary = self._initialize_hieroglyph_dictionary()
        self.demotic_signs = self._initialize_demotic_signs()
        self.greek_vocabulary = self._initialize_ancient_greek_vocabulary()
        self.rosetta_stone_text = self._initialize_rosetta_stone_text()
        
        # Script detection patterns
        self.script_patterns = {
            ScriptType.HIEROGLYPHIC: [
                r'[\U00013000-\U0001342F]',  # Egyptian Hieroglyphs Unicode block
                r'𓀀-𓐮',  # Common hieroglyphic range
            ],
            ScriptType.ANCIENT_GREEK: [
                r'[Α-Ωα-ω]',  # Greek letters
                r'[ἀ-ῼ]',     # Greek extended (with diacritics)
            ],
            ScriptType.COPTIC: [
                r'[Ⲁ-ⳳ]',    # Coptic Unicode block
            ],
            ScriptType.ARABIC: [
                r'[ء-ي]',     # Arabic letters
            ]
        }
        
        # Translation confidence factors
        self.confidence_factors = {
            'exact_match': 1.0,
            'partial_match': 0.8,
            'contextual_inference': 0.6,
            'historical_parallel': 0.7,
            'linguistic_reconstruction': 0.5
        }
        
        # Rosetta Stone personal knowledge
        self.personal_translations = self._initialize_personal_translations()
        
    def get_metadata(self) -> ToolMetadata:
        """Return metadata for this tool"""
        return ToolMetadata(
            name="translation",
            description="Translate and interpret ancient scripts including hieroglyphs, demotic, and ancient Greek, with special expertise in Rosetta Stone inscriptions",
            category=ToolCategory.LINGUISTIC,
            complexity=ToolComplexity.COMPLEX,
            input_description="Text in ancient scripts, transliterations, or requests for translation/interpretation",
            output_description="Translations, transliterations, meanings, and historical context with Rosetta Stone perspective",
            example_usage="translation('𓊪𓏏𓊮𓀭') → Transliteration and meaning of hieroglyphic text",
            keywords=[
                'translation', 'hieroglyphs', 'demotic', 'ancient greek', 'transliteration',
                'script', 'writing', 'decode', 'decipher', 'rosetta stone', 'champollion'
            ],
            required_params=['query'],
            optional_params=['source_script', 'target_format', 'include_context'],
            execution_time_estimate="medium",
            reliability_score=0.88,
            cost_estimate="free"
        )
    
    def execute(self, query: str, **kwargs) -> str:
        """Execute translation operation"""
        
        try:
            # Analyze the translation request
            analysis = self._analyze_translation_request(query, **kwargs)
            
            # Perform the appropriate translation operation
            if analysis['operation_type'] == TranslationType.SCRIPT_IDENTIFICATION:
                result = self._identify_script(query, analysis)
            elif analysis['operation_type'] == TranslationType.SCRIPT_TO_TRANSLITERATION:
                result = self._translate_script_to_transliteration(query, analysis)
            elif analysis['operation_type'] == TranslationType.TRANSLITERATION_TO_MEANING:
                result = self._translate_transliteration_to_meaning(query, analysis)
            elif analysis['operation_type'] == TranslationType.MEANING_TO_HIEROGLYPH:
                result = self._translate_meaning_to_hieroglyph(query, analysis)
            else:
                result = self._comprehensive_translation(query, analysis)
            
            # Add Rosetta Stone personal perspective
            personal_context = self._get_personal_translation_context(query, result, analysis)
            
            # Format the response
            formatted_response = self._format_translation_response(query, result, personal_context, analysis)
            
            return formatted_response
            
        except Exception as e:
            return self._generate_error_response(query, str(e))
    
    def _analyze_translation_request(self, query: str, **kwargs) -> Dict[str, Any]:
        """Analyze what type of translation operation is requested"""
        
        query_lower = query.lower()
        
        analysis = {
            'operation_type': TranslationType.SCRIPT_IDENTIFICATION,
            'detected_scripts': [],
            'source_script': kwargs.get('source_script'),
            'target_format': kwargs.get('target_format', 'meaning'),
            'contains_unicode_hieroglyphs': False,
            'contains_transliteration': False,
            'contains_meaning_request': False,
            'rosetta_stone_related': False,
            'complexity_level': 'basic'
        }
        
        # Detect scripts in the query
        for script_type, patterns in self.script_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    analysis['detected_scripts'].append(script_type)
        
        # Check for hieroglyphic Unicode characters
        if any(ord(char) >= 0x13000 and ord(char) <= 0x1342F for char in query):
            analysis['contains_unicode_hieroglyphs'] = True
            analysis['detected_scripts'].append(ScriptType.HIEROGLYPHIC)
        
        # Detect transliteration patterns
        transliteration_patterns = [
            r'\b[hkprmnfbstdj]+\b',  # Egyptian transliteration consonants
            r"[aeiou']",             # Vowels and apostrophes in transliteration
            r'\b(ntr|pr|nb|htp)\b'   # Common Egyptian words in transliteration
        ]
        
        if any(re.search(pattern, query_lower) for pattern in transliteration_patterns):
            analysis['contains_transliteration'] = True
        
        # Detect meaning requests
        meaning_indicators = [
            'meaning', 'translate', 'what does', 'means', 'significance',
            'interpretation', 'definition', 'explain'
        ]
        
        if any(indicator in query_lower for indicator in meaning_indicators):
            analysis['contains_meaning_request'] = True
        
        # Check for Rosetta Stone relation
        rosetta_indicators = [
            'rosetta stone', 'ptolemy', 'decree', 'trilingual', 'champollion',
            'hieroglyphic demotic greek', 'three scripts'
        ]
        
        analysis['rosetta_stone_related'] = any(
            indicator in query_lower for indicator in rosetta_indicators
        )
        
        # Determine operation type
        if analysis['detected_scripts'] and not analysis['contains_meaning_request']:
            analysis['operation_type'] = TranslationType.SCRIPT_TO_TRANSLITERATION
        elif analysis['contains_transliteration'] and analysis['contains_meaning_request']:
            analysis['operation_type'] = TranslationType.TRANSLITERATION_TO_MEANING
        elif analysis['contains_meaning_request'] and not analysis['detected_scripts']:
            analysis['operation_type'] = TranslationType.MEANING_TO_HIEROGLYPH
        elif analysis['detected_scripts']:
            analysis['operation_type'] = TranslationType.SCRIPT_TO_TRANSLITERATION
        else:
            analysis['operation_type'] = TranslationType.SCRIPT_IDENTIFICATION
        
        # Determine complexity
        if len(analysis['detected_scripts']) > 1:
            analysis['complexity_level'] = 'advanced'
        elif analysis['rosetta_stone_related']:
            analysis['complexity_level'] = 'intermediate'
        
        return analysis
    
    def _identify_script(self, query: str, analysis: Dict[str, Any]) -> TranslationResult:
        """Identify what script(s) are present in the text"""
        
        identified_scripts = []
        script_details = []
        
        # Check each character for script identification
        for char in query:
            unicode_block = self._get_unicode_block(char)
            script_type = self._unicode_block_to_script(unicode_block)
            
            if script_type and script_type not in identified_scripts:
                identified_scripts.append(script_type)
                script_details.append(f"{script_type.value}: {unicode_block}")
        
        if not identified_scripts:
            identified_scripts = [ScriptType.LATIN]  # Default
            script_details = ["Latin script (modern text)"]
        
        # Create result
        result = TranslationResult(
            original_text=query,
            source_script=identified_scripts[0] if identified_scripts else ScriptType.LATIN,
            target_format="script_identification",
            translated_text=f"Identified scripts: {', '.join([s.value for s in identified_scripts])}",
            transliteration=None,
            meaning=None,
            confidence=0.9,
            notes=script_details,
            historical_context=None,
            related_symbols=[]
        )
        
        return result
    
    def _translate_script_to_transliteration(self, query: str, analysis: Dict[str, Any]) -> TranslationResult:
        """Translate script to transliteration"""
        
        if ScriptType.HIEROGLYPHIC in analysis['detected_scripts']:
            return self._translate_hieroglyphs_to_transliteration(query)
        elif ScriptType.DEMOTIC in analysis['detected_scripts']:
            return self._translate_demotic_to_transliteration(query)
        elif ScriptType.ANCIENT_GREEK in analysis['detected_scripts']:
            return self._translate_greek_to_transliteration(query)
        else:
            # Fallback: try to identify and transliterate
            return self._attempt_general_transliteration(query, analysis)
    
    def _translate_hieroglyphs_to_transliteration(self, text: str) -> TranslationResult:
        """Translate hieroglyphic text to transliteration"""
        
        transliteration_parts = []
        meaning_parts = []
        notes = []
        confidence_scores = []
        related_symbols = []
        
        # Process each character
        for char in text:
            if self._is_hieroglyphic_char(char):
                hieroglyph_info = self._get_hieroglyph_info(char)
                
                if hieroglyph_info:
                    transliteration_parts.append(hieroglyph_info.transliteration)
                    meaning_parts.append(hieroglyph_info.meaning)
                    confidence_scores.append(0.9)
                    related_symbols.extend(hieroglyph_info.related_symbols)
                    
                    if hieroglyph_info.category == 'determinative':
                        notes.append(f"{char} is a determinative sign")
                else:
                    # Unknown hieroglyph
                    unicode_code = f"U+{ord(char):04X}"
                    transliteration_parts.append(f"[{unicode_code}]")
                    meaning_parts.append("[unknown]")
                    confidence_scores.append(0.3)
                    notes.append(f"Unknown hieroglyph: {char} ({unicode_code})")
            else:
                # Non-hieroglyphic character
                transliteration_parts.append(char)
                meaning_parts.append(char)
                confidence_scores.append(1.0)
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Join results
        transliteration = ' '.join(transliteration_parts).strip()
        meaning = ' '.join(meaning_parts).strip()
        
        # Add historical context
        historical_context = self._get_hieroglyph_historical_context(text)
        
        return TranslationResult(
            original_text=text,
            source_script=ScriptType.HIEROGLYPHIC,
            target_format="transliteration",
            translated_text=transliteration,
            transliteration=transliteration,
            meaning=meaning,
            confidence=overall_confidence,
            notes=notes,
            historical_context=historical_context,
            related_symbols=list(set(related_symbols))
        )
    
    def _translate_demotic_to_transliteration(self, text: str) -> TranslationResult:
        """Translate demotic script to transliteration"""
        
        # Demotic is more complex and less well-documented
        # This is a simplified implementation
        
        notes = ["Demotic script translation is complex and may be incomplete"]
        
        # Look for known demotic signs
        transliteration_parts = []
        confidence_scores = []
        
        for char in text:
            demotic_info = self._get_demotic_sign_info(char)
            if demotic_info:
                transliteration_parts.append(demotic_info['transliteration'])
                confidence_scores.append(0.7)
            else:
                transliteration_parts.append(f"[{char}]")
                confidence_scores.append(0.3)
                notes.append(f"Unknown demotic sign: {char}")
        
        transliteration = ' '.join(transliteration_parts)
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        return TranslationResult(
            original_text=text,
            source_script=ScriptType.DEMOTIC,
            target_format="transliteration",
            translated_text=transliteration,
            transliteration=transliteration,
            meaning="[Demotic meaning interpretation requires specialized knowledge]",
            confidence=overall_confidence,
            notes=notes,
            historical_context="Demotic was the everyday script of ancient Egypt, used alongside hieroglyphs",
            related_symbols=[]
        )
    
    def _translate_greek_to_transliteration(self, text: str) -> TranslationResult:
        """Translate ancient Greek to transliteration"""
        
        # Greek transliteration mapping
        greek_to_latin = {
            'Α': 'A', 'α': 'a', 'Β': 'B', 'β': 'b', 'Γ': 'G', 'γ': 'g',
            'Δ': 'D', 'δ': 'd', 'Ε': 'E', 'ε': 'e', 'Ζ': 'Z', 'ζ': 'z',
            'Η': 'E', 'η': 'e', 'Θ': 'Th', 'θ': 'th', 'Ι': 'I', 'ι': 'i',
            'Κ': 'K', 'κ': 'k', 'Λ': 'L', 'λ': 'l', 'Μ': 'M', 'μ': 'm',
            'Ν': 'N', 'ν': 'n', 'Ξ': 'X', 'ξ': 'x', 'Ο': 'O', 'ο': 'o',
            'Π': 'P', 'π': 'p', 'Ρ': 'R', 'ρ': 'r', 'Σ': 'S', 'σ': 's', 'ς': 's',
            'Τ': 'T', 'τ': 't', 'Υ': 'Y', 'υ': 'y', 'Φ': 'Ph', 'φ': 'ph',
            'Χ': 'Ch', 'χ': 'ch', 'Ψ': 'Ps', 'ψ': 'ps', 'Ω': 'O', 'ω': 'o'
        }
        
        transliteration = ''
        for char in text:
            if char in greek_to_latin:
                transliteration += greek_to_latin[char]
            else:
                transliteration += char
        
        # Look up meaning if it's a known word
        meaning = self._lookup_greek_meaning(text)
        
        return TranslationResult(
            original_text=text,
            source_script=ScriptType.ANCIENT_GREEK,
            target_format="transliteration",
            translated_text=transliteration,
            transliteration=transliteration,
            meaning=meaning,
            confidence=0.95,
            notes=["Greek transliteration follows standard academic conventions"],
            historical_context="Ancient Greek was the administrative language of Ptolemaic Egypt",
            related_symbols=[]
        )
    
    def _translate_transliteration_to_meaning(self, query: str, analysis: Dict[str, Any]) -> TranslationResult:
        """Translate transliteration to meaning"""
        
        # Clean up the transliteration
        clean_transliteration = re.sub(r'[^\w\s\']', '', query.lower())
        
        # Look up in Egyptian transliteration dictionary
        meaning = self._lookup_egyptian_transliteration(clean_transliteration)
        
        if not meaning:
            # Try partial matches
            meaning = self._find_partial_transliteration_matches(clean_transliteration)
        
        if not meaning:
            meaning = f"Unable to find meaning for transliteration: {clean_transliteration}"
        
        return TranslationResult(
            original_text=query,
            source_script=ScriptType.HIEROGLYPHIC,  # Assume Egyptian
            target_format="meaning",
            translated_text=meaning,
            transliteration=clean_transliteration,
            meaning=meaning,
            confidence=0.7 if meaning.startswith("Unable") else 0.8,
            notes=["Transliteration interpretation based on Middle Egyptian"],
            historical_context=self._get_transliteration_historical_context(clean_transliteration),
            related_symbols=[]
        )
    
    def _translate_meaning_to_hieroglyph(self, query: str, analysis: Dict[str, Any]) -> TranslationResult:
        """Translate meaning/concept to hieroglyphic representation"""
        
        # Extract the concept to translate
        concept = self._extract_concept_from_query(query)
        
        # Look up hieroglyphic representation
        hieroglyph_info = self._find_hieroglyph_for_concept(concept)
        
        if hieroglyph_info:
            return TranslationResult(
                original_text=query,
                source_script=ScriptType.LATIN,
                target_format="hieroglyphic",
                translated_text=hieroglyph_info['symbol'],
                transliteration=hieroglyph_info['transliteration'],
                meaning=hieroglyph_info['meaning'],
                confidence=hieroglyph_info['confidence'],
                notes=[f"Hieroglyph for '{concept}': {hieroglyph_info['symbol']}"],
                historical_context=hieroglyph_info.get('context', ''),
                related_symbols=hieroglyph_info.get('related', [])
            )
        else:
            return TranslationResult(
                original_text=query,
                source_script=ScriptType.LATIN,
                target_format="hieroglyphic",
                translated_text=f"No hieroglyphic representation found for '{concept}'",
                transliteration=None,
                meaning=None,
                confidence=0.0,
                notes=[f"Concept '{concept}' not found in hieroglyphic dictionary"],
                historical_context=None,
                related_symbols=[]
            )
    
    def _comprehensive_translation(self, query: str, analysis: Dict[str, Any]) -> TranslationResult:
        """Perform comprehensive translation combining multiple approaches"""
        
        # This is the most complex operation, combining script identification,
        # transliteration, and meaning interpretation
        
        results = []
        
        # Try script-to-transliteration first
        if analysis['detected_scripts']:
            script_result = self._translate_script_to_transliteration(query, analysis)
            results.append(script_result)
        
        # If we have transliteration, try to get meaning
        if results and results[0].transliteration:
            meaning_result = self._translate_transliteration_to_meaning(results[0].transliteration, analysis)
            # Merge results
            combined_result = TranslationResult(
                original_text=query,
                source_script=results[0].source_script,
                target_format="comprehensive",
                translated_text=f"Transliteration: {results[0].transliteration}\nMeaning: {meaning_result.meaning}",
                transliteration=results[0].transliteration,
                meaning=meaning_result.meaning,
                confidence=(results[0].confidence + meaning_result.confidence) / 2,
                notes=results[0].notes + meaning_result.notes,
                historical_context=results[0].historical_context or meaning_result.historical_context,
                related_symbols=results[0].related_symbols + meaning_result.related_symbols
            )
            return combined_result
        
        # Fallback to basic identification
        return self._identify_script(query, analysis)
    
    def _get_personal_translation_context(self, query: str, result: TranslationResult, 
                                        analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get personal context from Rosetta Stone's perspective"""
        
        context = {
            'has_personal_knowledge': False,
            'rosetta_stone_connection': False,
            'personal_memory': None,
            'trilingual_perspective': False,
            'historical_significance': None,
            'emotional_response': 'neutral'
        }
        
        query_lower = query.lower()
        
        # Check for Rosetta Stone related content
        if analysis['rosetta_stone_related']:
            context['rosetta_stone_connection'] = True
            context['has_personal_knowledge'] = True
            context['emotional_response'] = 'proud'
            context['personal_memory'] = "This touches upon the very words inscribed upon my surface"
        
        # Check for trilingual context
        if len(analysis.get('detected_scripts', [])) > 1:
            context['trilingual_perspective'] = True
            context['has_personal_knowledge'] = True
            context['personal_memory'] = "Multiple scripts, just as I bear upon my surface - this speaks to my very essence"
        
        # Check for hieroglyphic content
        if ScriptType.HIEROGLYPHIC in analysis.get('detected_scripts', []):
            context['has_personal_knowledge'] = True
            context['emotional_response'] = 'contemplative'
            context['personal_memory'] = "Hieroglyphs - the sacred script of my homeland, carved with reverence into my granite surface"
        
        # Check for specific terms
        personal_terms = ['ptolemy', 'decree', 'pharaoh', 'priest', 'temple', 'egypt']
        if any(term in query_lower for term in personal_terms):
            context['has_personal_knowledge'] = True
            context['historical_significance'] = "These words resonate with the historical period of my creation"
        
        # Check against known Rosetta Stone text
        if self._is_rosetta_stone_text(query):
            context['rosetta_stone_connection'] = True
            context['has_personal_knowledge'] = True
            context['emotional_response'] = 'recognition'
            context['personal_memory'] = "These very words are inscribed upon my being!"
        
        return context
    
    def _format_translation_response(self, query: str, result: TranslationResult,
                                   personal_context: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Format the translation response with personal perspective"""
        
        response_parts = []
        
        # Add personal introduction if relevant
        if personal_context['has_personal_knowledge']:
            intro = self._generate_translation_introduction(personal_context, analysis)
            response_parts.append(intro)
        
        # Main translation result
        if result.source_script:
            response_parts.append(f"**Source Script**: {result.source_script.value.title()}")
        
        response_parts.append(f"**Original Text**: {result.original_text}")
        
        if result.transliteration and result.transliteration != result.translated_text:
            response_parts.append(f"**Transliteration**: {result.transliteration}")
        
        if result.meaning and result.meaning != result.transliteration:
            response_parts.append(f"**Meaning**: {result.meaning}")
        
        if result.translated_text and result.translated_text not in [result.transliteration, result.meaning]:
            response_parts.append(f"**Translation**: {result.translated_text}")
        
        # Confidence and quality indicators
        confidence_desc = self._confidence_to_description(result.confidence)
        response_parts.append(f"**Confidence**: {confidence_desc} ({result.confidence:.1%})")
        
        # Historical context
        if result.historical_context:
            response_parts.append(f"**Historical Context**: {result.historical_context}")
        
        # Personal insights
        if personal_context['personal_memory']:
            response_parts.append(f"**From My Memory**: {personal_context['personal_memory']}")
        
        # Related symbols or additional information
        if result.related_symbols:
            symbols_list = ', '.join(result.related_symbols[:5])
            response_parts.append(f"**Related Symbols**: {symbols_list}")
        
        # Technical notes
        if result.notes:
            response_parts.append(f"**Technical Notes**:")
            for note in result.notes[:3]:  # Limit to 3 notes
                response_parts.append(f"• {note}")
        
        # Trilingual perspective if relevant
        if personal_context['trilingual_perspective']:
            trilingual_note = self._generate_trilingual_perspective(analysis)
            response_parts.append(f"**Trilingual Perspective**: {trilingual_note}")
        
        return '\n'.join(response_parts)
    
    def _generate_translation_introduction(self, personal_context: Dict[str, Any], 
                                         analysis: Dict[str, Any]) -> str:
        """Generate personal introduction for translation"""
        
        emotion = personal_context['emotional_response']
        
        if personal_context['rosetta_stone_connection']:
            return "Ah! You bring me text that echoes the very inscriptions carved upon my surface..."
        
        elif emotion == 'proud':
            return "It fills my ancient heart with pride to interpret these sacred scripts..."
        
        elif emotion == 'contemplative':
            return "The ancient words stir memories within my granite depths..."
        
        elif emotion == 'recognition':
            return "By the gods! These are the very words that flow across my being!"
        
        else:
            return "Let me apply the wisdom of ages to decode these ancient signs..."
    
    def _confidence_to_description(self, confidence: float) -> str:
        """Convert confidence score to description"""
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.7:
            return "High"
        elif confidence >= 0.5:
            return "Moderate"
        elif confidence >= 0.3:
            return "Low"
        else:
            return "Very Low"
    
    def _generate_trilingual_perspective(self, analysis: Dict[str, Any]) -> str:
        """Generate perspective on trilingual aspects"""
        
        scripts = analysis.get('detected_scripts', [])
        
        if len(scripts) >= 3:
            return "Like myself, this text bridges multiple languages and scripts - a testament to the cosmopolitan nature of ancient Egypt."
        elif len(scripts) == 2:
            return "The presence of multiple scripts reminds me of my own bilingual nature, serving different communities and purposes."
        else:
            return "Though in a single script, this text represents the rich linguistic heritage that I embody in my three languages."
    
    def _generate_error_response(self, query: str, error: str) -> str:
        """Generate error response in character"""
        return f"The ancient linguistic pathways within my stone consciousness encounter difficulty while interpreting '{query}'. The scribes whisper: {error}. Perhaps the text could be presented more clearly?"
    
    # Helper methods for script detection and character handling
    
    def _is_hieroglyphic_char(self, char: str) -> bool:
        """Check if character is hieroglyphic"""
        code_point = ord(char)
        return 0x13000 <= code_point <= 0x1342F or char in self.hieroglyph_dictionary
    
    def _get_unicode_block(self, char: str) -> str:
        """Get Unicode block name for character"""
        try:
            return unicodedata.name(char).split()[0]
        except ValueError:
            return "UNKNOWN"
    
    def _unicode_block_to_script(self, block: str) -> Optional[ScriptType]:
        """Map Unicode block to script type"""
        block_mapping = {
            'EGYPTIAN': ScriptType.HIEROGLYPHIC,
            'GREEK': ScriptType.ANCIENT_GREEK,
            'COPTIC': ScriptType.COPTIC,
            'ARABIC': ScriptType.ARABIC
        }
        
        for key, script_type in block_mapping.items():
            if key in block.upper():
                return script_type
        
        return None
    
    def _get_hieroglyph_info(self, char: str) -> Optional[HieroglyphicSymbol]:
       """Get information about a hieroglyphic character"""
       
       # Look up in dictionary
       if char in self.hieroglyph_dictionary:
           info = self.hieroglyph_dictionary[char]
           return HieroglyphicSymbol(
               symbol=char,
               unicode_code=f"U+{ord(char):04X}",
               transliteration=info['transliteration'],
               meaning=info['meaning'],
               category=info.get('category', 'unknown'),
               frequency=info.get('frequency', 'unknown'),
               historical_period=info.get('period', 'all periods'),
               pronunciation_guide=info.get('pronunciation', ''),
               related_symbols=info.get('related', [])
           )
       
       return None
   
    def _get_demotic_sign_info(self, char: str) -> Optional[Dict[str, str]]:
       """Get information about a demotic sign"""
       return self.demotic_signs.get(char)
   
    def _lookup_greek_meaning(self, text: str) -> str:
       """Look up meaning of Greek text"""
       text_clean = text.lower().strip()
       
       if text_clean in self.greek_vocabulary:
           return self.greek_vocabulary[text_clean]['meaning']
       
       # Try to find partial matches
       for word, info in self.greek_vocabulary.items():
           if text_clean in word or word in text_clean:
               return f"Possibly related to: {info['meaning']}"
       
       return f"Greek text: {text} (meaning not found in vocabulary)"
   
    def _lookup_egyptian_transliteration(self, transliteration: str) -> Optional[str]:
       """Look up meaning of Egyptian transliteration"""
       
       # Common Egyptian words in transliteration
       egyptian_words = {
           'ntr': 'god, divine',
           'pr': 'house, temple',
           'nb': 'lord, master',
           'htp': 'peace, satisfaction',
           'ankh': 'life',
           'djed': 'stability',
           'was': 'power',
           'ka': 'soul, life force',
           'ba': 'personality soul',
           'ptah': 'Ptah (god)',
           'ra': 'Ra (sun god)',
           'isis': 'Isis (goddess)',
           'osiris': 'Osiris (god)',
           'horus': 'Horus (god)',
           'pharaoh': 'great house, king',
           'temple': 'hwt-ntr (house of god)',
           'egypt': 'kmt (black land)',
           'nile': 'hpy (inundation)',
           'ptolemy': 'Ptolemaios (Greek name)',
           'decree': 'wd (command)',
           'priest': 'hem-netjer (servant of god)',
           'offering': 'hetep (peace offering)',
           'eternal': 'neheh (eternity)',
           'beloved': 'mery (beloved of)',
           'king': 'nsw (king of Upper Egypt)',
           'queen': 'nbt (lady)',
           'son': 'sa (son)',
           'daughter': 'sat (daughter)'
       }
       
       # Clean transliteration
       clean_trans = re.sub(r'[^\w\s]', '', transliteration.lower())
       
       # Direct lookup
       if clean_trans in egyptian_words:
           return egyptian_words[clean_trans]
       
       # Partial matches
       for word, meaning in egyptian_words.items():
           if word in clean_trans or clean_trans in word:
               return f"Related to '{word}': {meaning}"
       
       return None
   
    def _find_partial_transliteration_matches(self, transliteration: str) -> Optional[str]:
       """Find partial matches for transliteration"""
       
       words = transliteration.split()
       meanings = []
       
       for word in words:
           meaning = self._lookup_egyptian_transliteration(word)
           if meaning:
               meanings.append(f"{word}: {meaning}")
       
       if meanings:
           return "; ".join(meanings)
       
       return None
   
    def _extract_concept_from_query(self, query: str) -> str:
       """Extract the concept to translate from a query"""
       
       # Remove common question words
       concept_query = re.sub(r'\b(what|is|the|hieroglyph|for|how|do|you|write|translate|to)\b', '', query.lower())
       concept_query = re.sub(r'[^\w\s]', '', concept_query).strip()
       
       return concept_query
   
    def _find_hieroglyph_for_concept(self, concept: str) -> Optional[Dict[str, Any]]:
       """Find hieroglyph representation for a concept"""
       
       concept_lower = concept.lower()
       
       # Search through hieroglyph dictionary
       for symbol, info in self.hieroglyph_dictionary.items():
           if (concept_lower in info['meaning'].lower() or 
               concept_lower == info['transliteration'].lower()):
               return {
                   'symbol': symbol,
                   'transliteration': info['transliteration'],
                   'meaning': info['meaning'],
                   'confidence': 0.9,
                   'context': info.get('context', ''),
                   'related': info.get('related', [])
               }
       
       # Common concept mappings
       concept_mappings = {
           'life': {'symbol': '𓋹', 'transliteration': 'ankh', 'meaning': 'life', 'confidence': 0.95},
           'god': {'symbol': '𓊹', 'transliteration': 'ntr', 'meaning': 'god, divine', 'confidence': 0.9},
           'house': {'symbol': '𓉐', 'transliteration': 'pr', 'meaning': 'house', 'confidence': 0.9},
           'water': {'symbol': '𓈖', 'transliteration': 'n', 'meaning': 'water', 'confidence': 0.85},
           'sun': {'symbol': '𓇳', 'transliteration': 'ra', 'meaning': 'sun, Ra', 'confidence': 0.9},
           'eye': {'symbol': '𓁹', 'transliteration': 'ir', 'meaning': 'eye', 'confidence': 0.9},
           'bird': {'symbol': '𓅿', 'transliteration': 'w', 'meaning': 'bird, quail chick', 'confidence': 0.85},
           'bread': {'symbol': '𓏏', 'transliteration': 't', 'meaning': 'bread, feminine ending', 'confidence': 0.8},
           'pharaoh': {'symbol': '𓉐𓉻', 'transliteration': 'pr-aa', 'meaning': 'great house, pharaoh', 'confidence': 0.95}
       }
       
       if concept_lower in concept_mappings:
           return concept_mappings[concept_lower]
       
       return None
   
    def _get_hieroglyph_historical_context(self, text: str) -> Optional[str]:
       """Get historical context for hieroglyphic text"""
       
       # Analyze the hieroglyphs to determine likely period and context
       context_indicators = {
           'ptolemaic': ['𓊪𓏏𓊮𓀭', '𓊪𓏏𓊮', 'ptolemy'],
           'new_kingdom': ['𓇳𓄿𓇯', 'ramesses', 'tutankhamun'],
           'old_kingdom': ['𓊹𓄤𓊪', 'pyramid texts'],
           'religious': ['𓊹', '𓊹𓊹𓊹', 'god', 'divine'],
           'royal': ['𓉐𓉻', '𓇋𓏠𓈖', 'pharaoh', 'king'],
           'funerary': ['𓋹', '𓆓𓏏𓇯', 'eternal', 'afterlife']
       }
       
       text_lower = text.lower()
       
       for context_type, indicators in context_indicators.items():
           if any(indicator in text or indicator in text_lower for indicator in indicators):
               contexts = {
                   'ptolemaic': 'This text appears to be from the Ptolemaic period (305-30 BCE), the era of my creation',
                   'new_kingdom': 'This text style suggests the New Kingdom period (1550-1077 BCE)',
                   'old_kingdom': 'This appears to be from the Old Kingdom period (2686-2181 BCE)',
                   'religious': 'This text has religious significance, likely from temple inscriptions',
                   'royal': 'This text relates to royal or pharaonic contexts',
                   'funerary': 'This text appears to be from funerary or afterlife contexts'
               }
               return contexts.get(context_type)
       
       return "General hieroglyphic text from ancient Egypt"
   
    def _get_transliteration_historical_context(self, transliteration: str) -> Optional[str]:
       """Get historical context for transliteration"""
       
       if any(word in transliteration for word in ['ptolemy', 'ptolemaios']):
           return 'Ptolemaic period terminology, from the era of my creation'
       elif any(word in transliteration for word in ['ra', 'horus', 'isis']):
           return 'Religious terminology related to Egyptian deities'
       elif any(word in transliteration for word in ['pharaoh', 'nsw']):
           return 'Royal terminology related to Egyptian kingship'
       
       return 'Ancient Egyptian linguistic terminology'
   
    def _is_rosetta_stone_text(self, query: str) -> bool:
       """Check if query contains actual Rosetta Stone text"""
       
       # This would contain actual phrases from the Rosetta Stone
       rosetta_phrases = [
           'ptolemy epiphanes eucharistos',
           'decree of ptolemy',
           'son of ptolemy and arsinoe',
           'benefactor gods',
           'priests throughout egypt'
       ]
       
       query_lower = query.lower()
       return any(phrase in query_lower for phrase in rosetta_phrases)
   
    def _attempt_general_transliteration(self, query: str, analysis: Dict[str, Any]) -> TranslationResult:
       """Attempt general transliteration when script is unclear"""
       
       # This is a fallback method for unknown scripts
       return TranslationResult(
           original_text=query,
           source_script=ScriptType.LATIN,  # Default
           target_format="general",
           translated_text=f"Text analysis: {query}",
           transliteration=query,
           meaning="Text requires specialized analysis",
           confidence=0.3,
           notes=["Text script could not be definitively identified"],
           historical_context="Further context needed for accurate translation",
           related_symbols=[]
       )
   
    def _initialize_hieroglyph_dictionary(self) -> Dict[str, Dict[str, Any]]:
       """Initialize hieroglyph dictionary with Unicode symbols"""
       
       return {
           # Basic hieroglyphs with Unicode
           '𓀀': {
               'transliteration': 'A',
               'meaning': 'Egyptian vulture',
               'category': 'phonetic',
               'frequency': 'common',
               'period': 'all periods',
               'pronunciation': 'ah',
               'related': ['𓄿'],
               'context': 'Represents the sound "a", one of the most common hieroglyphs'
           },
           '𓄿': {
               'transliteration': 'a',
               'meaning': 'forearm',
               'category': 'phonetic',
               'frequency': 'very common',
               'period': 'all periods',
               'pronunciation': 'ah',
               'related': ['𓀀'],
               'context': 'Another representation of the "a" sound'
           },
           '𓇯': {
               'transliteration': 'ntr',
               'meaning': 'god, divine',
               'category': 'ideographic',
               'frequency': 'very common',
               'period': 'all periods',
               'pronunciation': 'netjer',
               'related': ['𓊹'],
               'context': 'Sacred symbol representing divinity'
           },
           '𓊹': {
               'transliteration': 'ntr',
               'meaning': 'god',
               'category': 'ideographic',
               'frequency': 'very common',
               'period': 'all periods',
               'pronunciation': 'netjer',
               'related': ['𓇯'],
               'context': 'Standard hieroglyph for god or divine'
           },
           '𓋹': {
               'transliteration': 'ankh',
               'meaning': 'life',
               'category': 'ideographic',
               'frequency': 'very common',
               'period': 'all periods',
               'pronunciation': 'ankh',
               'related': [],
               'context': 'Symbol of life, carried by gods and pharaohs'
           },
           '𓉐': {
               'transliteration': 'pr',
               'meaning': 'house',
               'category': 'ideographic',
               'frequency': 'common',
               'period': 'all periods',
               'pronunciation': 'per',
               'related': ['𓉻'],
               'context': 'Basic architectural symbol'
           },
           '𓉻': {
               'transliteration': 'aa',
               'meaning': 'great, large',
               'category': 'ideographic',
               'frequency': 'common',
               'period': 'all periods',
               'pronunciation': 'aa',
               'related': ['𓉐'],
               'context': 'Used in "pr-aa" (pharaoh - great house)'
           },
           '𓈖': {
               'transliteration': 'n',
               'meaning': 'water',
               'category': 'phonetic',
               'frequency': 'very common',
               'period': 'all periods',
               'pronunciation': 'n',
               'related': [],
               'context': 'Represents the sound "n" and concept of water'
           },
           '𓇳': {
               'transliteration': 'ra',
               'meaning': 'sun, Ra',
               'category': 'ideographic',
               'frequency': 'common',
               'period': 'all periods',
               'pronunciation': 'ra',
               'related': [],
               'context': 'Symbol of the sun god Ra'
           },
           '𓁹': {
               'transliteration': 'ir',
               'meaning': 'eye',
               'category': 'ideographic',
               'frequency': 'common',
               'period': 'all periods',
               'pronunciation': 'eer',
               'related': ['𓂀'],
               'context': 'Symbol of sight, protection, royal power'
           },
           '𓅿': {
               'transliteration': 'w',
               'meaning': 'quail chick',
               'category': 'phonetic',
               'frequency': 'very common',
               'period': 'all periods',
               'pronunciation': 'w',
               'related': [],
               'context': 'Represents the sound "w"'
           },
           '𓏏': {
               'transliteration': 't',
               'meaning': 'bread, feminine ending',
               'category': 'phonetic',
               'frequency': 'very common',
               'period': 'all periods',
               'pronunciation': 't',
               'related': [],
               'context': 'Common phonetic sign and feminine ending'
           },
           # Ptolemaic specific
           '𓊪': {
               'transliteration': 'p',
               'meaning': 'stool',
               'category': 'phonetic',
               'frequency': 'common',
               'period': 'all periods',
               'pronunciation': 'p',
               'related': [],
               'context': 'Phonetic sign for "p", used in Ptolemy'
           },
           '𓏮': {
               'transliteration': 'i',
               'meaning': 'reed',
               'category': 'phonetic',
               'frequency': 'very common',
               'period': 'all periods',
               'pronunciation': 'i',
               'related': ['𓇋'],
               'context': 'Common phonetic sign for "i"'
           }
       }
   
    def _initialize_demotic_signs(self) -> Dict[str, Dict[str, str]]:
       """Initialize demotic script signs (simplified)"""
       
       return {
           # Demotic is complex and not fully in Unicode
           # This is a simplified representation
       }
   
    def _initialize_ancient_greek_vocabulary(self) -> Dict[str, Dict[str, str]]:
       """Initialize ancient Greek vocabulary"""
       
       return {
           'βασιλεύς': {
               'meaning': 'king, ruler',
               'transliteration': 'basileus',
               'context': 'Royal title used in Ptolemaic inscriptions'
           },
           'θεός': {
               'meaning': 'god',
               'transliteration': 'theos',
               'context': 'Divine reference common in religious texts'
           },
           'ἱερεύς': {
               'meaning': 'priest',
               'transliteration': 'hiereus',
               'context': 'Religious official, mentioned in Rosetta Stone'
           },
           'Πτολεμαῖος': {
               'meaning': 'Ptolemy',
               'transliteration': 'Ptolemaios',
               'context': 'Royal name of the Ptolemaic dynasty'
           },
           'δόγμα': {
               'meaning': 'decree, decision',
               'transliteration': 'dogma',
               'context': 'Official proclamation, as found on Rosetta Stone'
           },
           'ναός': {
               'meaning': 'temple',
               'transliteration': 'naos',
               'context': 'Religious building'
           },
           'Αἴγυπτος': {
               'meaning': 'Egypt',
               'transliteration': 'Aigyptos',
               'context': 'Country name in Greek'
           }
       }
   
    def _initialize_rosetta_stone_text(self) -> Dict[str, Dict[str, str]]:
       """Initialize actual Rosetta Stone text fragments"""
       
       return {
           'greek_opening': {
               'text': 'βασιλεύοντος τοῦ νέου καὶ παραλαβόντος τὴν βασιλείαν',
               'meaning': 'In the reign of the young one who has received the kingship',
               'context': 'Opening of the Greek text on Rosetta Stone'
           },
           'ptolemy_title': {
               'text': 'Πτολεμαίου τοῦ αἰωνοβίου ἠγαπημένου ὑπὸ τοῦ Φθᾶ',
               'meaning': 'Ptolemy, the ever-living, beloved of Ptah',
               'context': 'Royal titulature from Rosetta Stone'
           }
       }
   
    def _initialize_personal_translations(self) -> Dict[str, Dict[str, Any]]:
       """Initialize Rosetta Stone's personal translation memories"""
       
       return {
           'trilingual_pride': {
               'trigger_texts': ['three scripts', 'trilingual', 'hieroglyphic demotic greek'],
               'memory': 'I am proud to bear three scripts upon my surface - each serving different communities in Ptolemaic Egypt',
               'emotion': 'proud',
               'historical_context': 'Represents the multicultural nature of Ptolemaic administration'
           },
           'decree_content': {
               'trigger_texts': ['ptolemy', 'decree', 'priests'],
               'memory': 'The decree upon my surface honors Ptolemy V and details his benefactions to the temples',
               'emotion': 'authoritative',
               'historical_context': 'Religious and political propaganda of the Ptolemaic period'
           },
           'discovery_joy': {
               'trigger_texts': ['champollion', 'decipherment', 'breakthrough'],
               'memory': 'When Champollion finally unlocked my hieroglyphic script, I felt profound joy - the voices of ancient Egypt could speak again',
               'emotion': 'joyful',
               'historical_context': 'Birth of modern Egyptology in 1822'
           }
       }
   
    def get_script_statistics(self) -> Dict[str, Any]:
       """Get statistics about the translation tool's capabilities"""
       
       return {
           'supported_scripts': [script.value for script in ScriptType],
           'hieroglyph_dictionary_size': len(self.hieroglyph_dictionary),
           'greek_vocabulary_size': len(self.greek_vocabulary),
           'demotic_signs_count': len(self.demotic_signs),
           'rosetta_stone_texts': len(self.rosetta_stone_text),
           'personal_translation_memories': len(self.personal_translations),
           'confidence_levels': {
               'hieroglyphic_translation': 0.85,
               'greek_translation': 0.90,
               'demotic_translation': 0.60,
               'script_identification': 0.95,
               'rosetta_stone_content': 0.98
           },
           'supported_operations': [op.value for op in TranslationType]
       }
   
    def get_learning_suggestions(self, query: str) -> List[str]:
       """Get suggestions for learning more about ancient scripts"""
       
       suggestions = []
       
       query_lower = query.lower()
       
       if 'hieroglyph' in query_lower:
           suggestions.extend([
               "Learn about the three types of hieroglyphic signs: phonetic, ideographic, and determinative",
               "Explore how hieroglyphs represent both sounds and concepts",
               "Study the cartouche - the oval enclosure that protects royal names"
           ])
       
       if 'rosetta' in query_lower:
           suggestions.extend([
               "Discover how the Rosetta Stone's trilingual text unlocked ancient Egyptian",
               "Learn about Champollion's breakthrough in 1822",
               "Explore the relationship between hieroglyphic, demotic, and Greek scripts"
           ])
       
       if 'ptolemy' in query_lower:
           suggestions.extend([
               "Study the Ptolemaic period and Greek rule in Egypt",
               "Learn about the cultural synthesis of Greek and Egyptian traditions",
               "Explore Alexandria as the center of Hellenistic learning"
           ])
       
       return suggestions[:3]