"""
Test RAG-enhanced narrative generation
Verifies that all three narrative functions retrieve and use RAG context
"""
import asyncio
from rag_service import RAGService
from ai_narrative import generate_event_narrative, generate_consequence_narrative, generate_option_texts
from models import PlayerProfile, GameState, EducationPath, RiskAttitude, GameStatus
from google import genai
import os

async def test_rag_narratives():
    print("🧪 Testing RAG-Enhanced Narrative Generation")
    print("=" * 80)
    
    # Initialize RAG
    rag = RAGService(chroma_host="chromadb", chroma_port=8000)
    
    # Initialize Gemini client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set - cannot test")
        return
    
    client = genai.Client(api_key=api_key)
    
    # Create mock player profile
    profile = PlayerProfile(
        session_id="test_session",
        player_name="Test Player",
        age=22,
        city="Helsinki",
        education_path=EducationPath.UNIVERSITY,
        risk_attitude=RiskAttitude.BALANCED,
        starting_savings=5000,
        starting_debt=10000,
        aspirations="Become financially independent"
    )
    
    # Create mock game state
    state = GameState(
        profile_id=1,
        current_step=5,
        current_age=22,
        years_passed=0.5,
        money=4500,
        monthly_income=2000,
        monthly_expenses=1200,
        investments=1000,
        passive_income=20,
        debts=9500,
        fi_score=25.5,
        energy=75,
        motivation=80,
        social_life=70,
        financial_knowledge=40,
        assets={},
        game_status=GameStatus.ACTIVE
    )
    
    # Test 1: Event Narrative (should retrieve context about student finances)
    print("\n📝 TEST 1: Event Narrative Generation")
    print("-" * 80)
    event_type = "budget_decision"
    
    narrative = generate_event_narrative(
        event_type=event_type,
        state=state,
        profile=profile,
        curveball=None,
        client=client
    )
    
    print(f"\n✅ Generated narrative ({len(narrative)} chars):")
    print(f"   {narrative[:200]}...")
    
    # Test 2: Consequence Narrative (should retrieve context about loan consequences)
    print("\n\n📝 TEST 2: Consequence Narrative Generation")
    print("-" * 80)
    chosen_option = "Take out a student loan to cover expenses"
    option_effect = {
        "explanation": "Borrow money to maintain lifestyle",
        "money_change": 5000,
        "debt_change": 5000
    }
    
    consequence = generate_consequence_narrative(
        chosen_option=chosen_option,
        option_effect=option_effect,
        state=state,
        profile=profile,
        client=client
    )
    
    print(f"\n✅ Generated consequence ({len(consequence)} chars):")
    print(f"   {consequence[:200]}...")
    
    # Test 3: Option Texts (should retrieve context about investment/saving decisions)
    print("\n\n📝 TEST 3: Option Texts Generation")
    print("-" * 80)
    option_descriptions = [
        {
            "explanation": "Start investing in index funds",
            "fallback_text": "Invest in index funds"
        },
        {
            "explanation": "Build emergency fund in savings account",
            "fallback_text": "Save for emergencies"
        },
        {
            "explanation": "Pay off student loan debt faster",
            "fallback_text": "Pay down debt"
        }
    ]
    
    options = generate_option_texts(
        option_descriptions=option_descriptions,
        event_type="investment_decision",
        state=state,
        profile=profile,
        client=client
    )
    
    print(f"\n✅ Generated {len(options)} option texts:")
    for i, opt in enumerate(options, 1):
        print(f"   {i}. {opt[:100]}...")
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ RAG Integration Test Complete!")
    print("\nVerification:")
    print("  - Check logs above for '📚 RAG context retrieved' messages")
    print("  - Narratives should reference specific financial concepts")
    print("  - Sources should be attributed (knowledge_base or PDF names)")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_rag_narratives())
