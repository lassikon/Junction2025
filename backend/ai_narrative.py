"""
AI narrative generation for LifeSim using Gemini.

This module handles:
- Generating event narratives
- Creating consequence narratives
- Providing learning moments
- Adapting tone based on player profile
"""

from typing import List, Dict, Optional
from google import genai
import os
import json
from pathlib import Path

from models import PlayerProfile, GameState, RiskAttitude, EducationPath


# Load prompt templates
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt_template(filename: str) -> Dict:
    """Load a prompt template from JSON file"""
    filepath = PROMPTS_DIR / filename
    with open(filepath, 'r') as f:
        return json.load(f)


# Load all prompt templates at module level
NARRATIVE_PROMPTS = load_prompt_template("narrative_prompt.json")
CONSEQUENCE_PROMPTS = load_prompt_template("consequence_prompt.json")
LEARNING_PROMPTS = load_prompt_template("learning_moment_prompt.json")
FALLBACK_NARRATIVES = load_prompt_template("fallback_narratives.json")
OPTIONS_PROMPTS = load_prompt_template("options_prompt.json")


def get_ai_client():
    """Get configured Gemini AI client"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def generate_event_narrative(
    event_type: str,
    state: GameState,
    profile: PlayerProfile,
    curveball: Optional[Dict] = None,
    client: Optional[genai.Client] = None
) -> str:
    """
    Generate narrative for a game event using AI.

    Args:
        event_type: Type of event
        state: Current game state
        profile: Player profile
        curveball: Optional curveball details
        client: Gemini client (optional)

    Returns:
        Narrative text
    """
    if client is None:
        client = get_ai_client()

    # If no AI available, use fallback narratives
    if client is None:
        return get_fallback_narrative(event_type, state, curveball)

    try:
        prompt = build_narrative_prompt(event_type, state, profile, curveball)

        print("\n" + "="*80)
        print(f"🤖 GEMINI API CALL - Event Narrative ({event_type})")
        print("="*80)
        print("PROMPT:")
        print(prompt)
        print("\n" + "-"*80)

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )

        print("RESPONSE:")
        print(response.text.strip())
        print("="*80 + "\n")

        return response.text.strip()

    except Exception as e:
        print(f"AI narrative generation failed: {e}")
        return get_fallback_narrative(event_type, state, curveball)


def generate_consequence_narrative(
    chosen_option: str,
    option_effect: Dict,
    state: GameState,
    profile: PlayerProfile,
    client: Optional[genai.Client] = None
) -> str:
    """
    Generate consequence narrative after a decision using AI.

    Args:
        chosen_option: The option the player chose
        option_effect: Effect details
        state: Updated game state
        profile: Player profile
        client: Gemini client (optional)

    Returns:
        Consequence narrative text
    """
    if client is None:
        client = get_ai_client()

    if client is None:
        return option_effect.get("explanation", "You made your choice.")

    try:
        prompt = build_consequence_prompt(
            chosen_option, option_effect, state, profile)

        print("\n" + "="*80)
        print("🤖 GEMINI API CALL - Consequence Narrative")
        print("="*80)
        print("PROMPT:")
        print(prompt)
        print("\n" + "-"*80)

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )

        print("RESPONSE:")
        print(response.text.strip())
        print("="*80 + "\n")

        return response.text.strip()

    except Exception as e:
        print(f"AI consequence generation failed: {e}")
        return option_effect.get("explanation", "You made your choice.")


def generate_learning_moment(
    chosen_option: str,
    state: GameState,
    profile: PlayerProfile,
    client: Optional[genai.Client] = None
) -> Optional[str]:
    """
    Generate an educational insight based on the decision (RAG-enhanced).

    Args:
        chosen_option: The option chosen
        state: Current game state
        profile: Player profile
        client: Gemini client (optional)

    Returns:
        Learning moment text or None
    """
    # RAG-ENHANCED: Retrieve relevant concepts instead of random chance
    try:
        from rag_service import get_rag_service
        rag = get_rag_service()
        
        # Build query from context
        query = f"{chosen_option}. Age {state.current_age}, FI score {state.fi_score:.1f}%, financial knowledge {state.financial_knowledge}/100"
        print(f"🔎 RAG Query for learning moment: {query}")
        # Retrieve relevant financial concepts
        difficulty = "beginner" if state.financial_knowledge < 50 else "intermediate"
        concepts = rag.retrieve_financial_concepts(
            query=query,
            difficulty_filter=difficulty,
            top_k=2
        )
        print(f"🔍 Retrieved {len(concepts)} concepts for learning moment")
        for concept in concepts:
            print(f"   - {concept['title']} (score: {concept['score']:.2f})")

        # Only generate if we found relevant concepts (score > 0.7)
        if not concepts or concepts[0]['score'] < 0.7:
            print("⚠️ No relevant concepts found with sufficient score for learning moment")
            return None  # No relevant tip available
        
        if client is None:  
            client = get_ai_client()
        
        if client is None:
            return None
        
        print(f"🔎 Using concept for learning moment: {concepts[0]['title']} (score: {concepts[0]['score']:.2f})")
        # Build enhanced prompt with retrieved context
        prompt = f"""You are a friendly financial education coach. Provide a brief, practical tip.

RETRIEVED FINANCIAL CONCEPT:
{concepts[0]['content']}

PLAYER CONTEXT:
- Age: {state.current_age}
- FI Score: {state.fi_score:.1f}%
- Money: €{state.money:,.0f}
- Investments: €{state.investments:,.0f}
- Debts: €{state.debts:,.0f}
- Income: €{state.monthly_income:,.0f}/month
- Financial Knowledge: {state.financial_knowledge}/100

RECENT DECISION:
{chosen_option}

Provide a 1-2 sentence tip related to the retrieved concept, tailored to their situation.
Be encouraging and practical. Make it actionable."""

        print("\n" + "="*80)
        print("🤖 GEMINI API CALL - Learning Moment (RAG-Enhanced)")
        print("="*80)
        print(f"📚 Retrieved concept: {concepts[0]['title']} (score: {concepts[0]['score']:.2f})")
        print("PROMPT:")
        print(prompt)
        print("\n" + "-"*80)

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )

        tip = response.text.strip()
        print("RESPONSE:")
        print(tip)
        print("="*80 + "\n")
        
        return tip
        
    except Exception as e:
        print(f"⚠️ RAG learning moment failed: {e}")
        # Fallback to original 30% random logic
        import random
        if random.random() > 0.7:
            return None
        
        if client is None:
            client = get_ai_client()
        
        if client is None:
            return None
        
        try:
            # Original prompt without RAG
            prompt = f"""{LEARNING_PROMPTS['system_context']} {LEARNING_PROMPTS['template'].format(
                chosen_option=chosen_option,
                fi_score=state.fi_score,
                money=state.money,
                monthly_income=state.monthly_income,
                investments=state.investments,
                debts=state.debts,
                financial_knowledge=state.financial_knowledge
            )}

{LEARNING_PROMPTS['instruction']}"""

            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            return response.text.strip()
            
        except Exception as e2:
            print(f"Learning moment generation failed: {e2}")
            return None


def generate_option_texts(
    option_descriptions: List[Dict],
    event_type: str,
    state: GameState,
    profile: PlayerProfile,
    client: Optional[genai.Client] = None
) -> List[str]:
    """
    Generate varied option texts using AI while keeping effects hardcoded.

    Args:
        option_descriptions: List of option metadata with explanations
        event_type: Type of event
        state: Current game state
        profile: Player profile
        client: Gemini client (optional)

    Returns:
        List of AI-generated option texts
    """
    if client is None:
        client = get_ai_client()

    # Fallback to default texts if no AI
    if client is None:
        return [opt.get("fallback_text", opt["explanation"]) for opt in option_descriptions]

    try:
        # Build prompt for option generation
        options_context = "\n".join([
            f"{i+1}. {opt['explanation']}"
            for i, opt in enumerate(option_descriptions)
        ])

        # Build prompt from template
        template_filled = OPTIONS_PROMPTS['template'].format(
            age=profile.age,
            city=profile.city,
            education=profile.education_path.value,
            risk_attitude=profile.risk_attitude.value,
            money=state.money,
            monthly_income=state.monthly_income,
            monthly_expenses=state.monthly_expenses,
            fi_score=state.fi_score,
            event_type=event_type,
            options_context=options_context
        )

        prompt = f"""{OPTIONS_PROMPTS['system_context']}

{template_filled}

{OPTIONS_PROMPTS['instruction']}

{OPTIONS_PROMPTS['format_instruction']}"""

        print("\n" + "="*80)
        print("🤖 GEMINI API CALL - Option Texts")
        print("="*80)
        print("PROMPT:")
        print(prompt)
        print("\n" + "-"*80)

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )

        print("RESPONSE:")
        print(response.text.strip())
        print("="*80 + "\n")

        # Parse the response
        lines = response.text.strip().split('\n')
        generated_options = []

        for line in lines:
            line = line.strip()
            # Remove numbering (1., 2., etc.) and asterisks
            if line and (line[0].isdigit() or line.startswith('*') or line.startswith('-')):
                # Remove leading number and punctuation
                cleaned = line.lstrip('0123456789.*- ').strip()
                if cleaned:
                    generated_options.append(cleaned)

        # If we got the right number of options, use them
        if len(generated_options) == len(option_descriptions):
            return generated_options

        # Otherwise fallback to explanations
        print(
            f"Warning: Generated {len(generated_options)} options but expected {len(option_descriptions)}, using fallbacks")
        return [opt.get("fallback_text", opt["explanation"]) for opt in option_descriptions]

    except Exception as e:
        print(f"Option text generation failed: {e}")
        return [opt.get("fallback_text", opt["explanation"]) for opt in option_descriptions]


def build_narrative_prompt(
    event_type: str,
    state: GameState,
    profile: PlayerProfile,
    curveball: Optional[Dict] = None
) -> str:
    """Build prompt for event narrative generation"""

    # Format assets for display
    assets_text = ""
    if state.assets:
        assets_list = []
        for key, value in state.assets.items():
            if isinstance(value, dict):
                asset_details = ", ".join([f"{k}: {v}" for k, v in value.items()])
                assets_list.append(f"  • {key.replace('_', ' ').title()}: {asset_details}")
            else:
                assets_list.append(f"  • {key.replace('_', ' ').title()}: {value}")
        assets_text = "Assets Owned:\n" + "\n".join(assets_list) if assets_list else "No major assets yet"
    else:
        assets_text = "Assets Owned: None yet"

    # Context about the player
    context = f"""{NARRATIVE_PROMPTS['system_context']}

Player Profile:
- Age: {state.current_age} (started at {profile.age})
- Time in game: {state.years_passed:.1f} years
- City: {profile.city}
- Education: {profile.education_path.value}
- Risk Attitude: {profile.risk_attitude.value}

Current Situation (Step {state.current_step}):
- Money: €{state.money:.0f}
- Monthly Income: €{state.monthly_income:.0f}
- Monthly Expenses: €{state.monthly_expenses:.0f}
- FI Score: {state.fi_score:.1f}% (financial independence)
- Energy: {state.energy}/100
- Motivation: {state.motivation}/100
- Social Life: {state.social_life}/100
- Financial Knowledge: {state.financial_knowledge}/100

{assets_text}
"""

    # Tone guidance based on profile
    tone = NARRATIVE_PROMPTS['tone_guidance'].get(
        profile.risk_attitude.value,
        NARRATIVE_PROMPTS['tone_guidance']['balanced']
    )

    # Event-specific instructions
    if event_type == "curveball" and curveball:
        event_prompt = NARRATIVE_PROMPTS['curveball_instruction'].format(
            narrative=curveball['narrative']
        )
    else:
        description = NARRATIVE_PROMPTS['event_descriptions'].get(
            event_type,
            "A decision point has arrived."
        )
        event_prompt = NARRATIVE_PROMPTS['regular_event_instruction'].format(
            event_type=event_type,
            description=description
        )

    return f"""{context}

Tone: {tone}

Task: {event_prompt}

{NARRATIVE_PROMPTS['format_instruction']}"""


def build_consequence_prompt(
    chosen_option: str,
    option_effect: Dict,
    state: GameState,
    profile: PlayerProfile
) -> str:
    """Build prompt for consequence narrative generation"""

    prompt_content = CONSEQUENCE_PROMPTS['template'].format(
        chosen_option=chosen_option,
        explanation=option_effect.get('explanation', ''),
        money=state.money,
        fi_score=state.fi_score,
        energy=state.energy,
        motivation=state.motivation,
        social_life=state.social_life
    )

    return f"""{CONSEQUENCE_PROMPTS['system_context']}

{prompt_content}

{CONSEQUENCE_PROMPTS['instruction']}"""


def get_fallback_narrative(
    event_type: str,
    state: GameState,
    curveball: Optional[Dict] = None
) -> str:
    """Fallback narratives when AI is not available"""

    if event_type == "curveball" and curveball:
        return curveball["narrative"]

    # Get narrative template from JSON
    template = FALLBACK_NARRATIVES.get(
        event_type, FALLBACK_NARRATIVES['default'])

    # Format template with state variables
    return template.format(
        monthly_income=state.monthly_income,
        monthly_expenses=state.monthly_expenses,
        target=state.monthly_expenses * 3,
        money=state.money,
        debts=state.debts
    )
