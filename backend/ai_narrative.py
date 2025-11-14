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
    Generate an educational insight based on the decision.

    Args:
        chosen_option: The option chosen
        state: Current game state
        profile: Player profile
        client: Gemini client (optional)

    Returns:
        Learning moment text or None
    """
    # Only generate learning moments occasionally (30% chance)
    import random
    if random.random() > 0.3:
        return None

    if client is None:
        client = get_ai_client()

    if client is None:
        return None

    try:
        # Build prompt from template
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

        print("\n" + "="*80)
        print("🤖 GEMINI API CALL - Learning Moment")
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
        print(f"Learning moment generation failed: {e}")
        return None


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
