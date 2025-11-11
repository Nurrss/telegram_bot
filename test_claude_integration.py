"""
Test script for Claude API integration.
Run this after:
1. pip install -r requirements.txt
2. Setting ANTHROPIC_API_KEY in .env
3. Setting USE_FAKE_AI=false in .env
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_claude_integration():
    """Test Claude API integration."""
    print("=" * 60)
    print("Claude API Integration Test")
    print("=" * 60)

    # Check environment variables
    print("\n1. Checking environment variables...")
    api_key = os.getenv('ANTHROPIC_API_KEY')
    use_fake = os.getenv('USE_FAKE_AI', 'true').lower() == 'true'

    if not api_key or api_key == 'your_anthropic_api_key_here':
        print("   ❌ ANTHROPIC_API_KEY not set in .env file")
        print("   Please set your API key from https://console.anthropic.com/")
        return False
    else:
        print(f"   ✓ ANTHROPIC_API_KEY found ({api_key[:8]}...)")

    if use_fake:
        print("   ⚠️  USE_FAKE_AI=true (set to false to use real Claude API)")
    else:
        print("   ✓ USE_FAKE_AI=false")

    # Test imports
    print("\n2. Testing imports...")
    try:
        from ai.factory import create_ai, get_ai_info
        from ai.claude_ai import ClaudeAI
        from utils.cost_tracker import CostTracker
        print("   ✓ All modules imported successfully")
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

    # Create AI instance
    print("\n3. Creating AI instance...")
    try:
        ai = create_ai()
        info = get_ai_info(ai)
        print(f"   ✓ AI instance created")
        print(f"   Model: {info['model_name']}")
        print(f"   Is Claude: {info.get('is_claude', False)}")
        print(f"   Is Fake: {info.get('is_fake', False)}")
        print(f"   Has cost tracking: {info.get('has_cost_tracking', False)}")
    except Exception as e:
        print(f"   ❌ Failed to create AI instance: {e}")
        return False

    # Test if using real Claude API
    if not info.get('is_claude'):
        print("\n   ⚠️  Currently using FakeAI")
        print("   Set USE_FAKE_AI=false in .env to test real Claude API")
        return True

    # Test basic response generation
    print("\n4. Testing response generation...")
    try:
        style = {
            'formality': 'casual',
            'language': 'russian',
            'emoji_usage': 'low',
            'verbosity': 'brief'
        }

        response = await ai.generate_response(
            prompt="Привет! Как дела?",
            user_id=12345,
            style=style
        )

        print(f"   ✓ Response generated successfully")
        print(f"   Response: {response[:100]}...")

    except Exception as e:
        print(f"   ❌ Response generation failed: {e}")
        return False

    # Test cost tracking
    print("\n5. Testing cost tracking...")
    try:
        cost_tracker = CostTracker()
        summary = cost_tracker.get_summary()

        print(f"   ✓ Cost tracking working")
        print(f"   Total requests: {summary['total']['requests']}")
        print(f"   Total cost: ${summary['total']['cost']:.4f}")
        print(f"   Today's cost: ${summary['today'].get('cost', 0):.4f}")

    except Exception as e:
        print(f"   ❌ Cost tracking failed: {e}")
        return False

    # Test plan generation (optional - costs more tokens)
    print("\n6. Testing plan generation (optional)...")
    user_input = input("   Test plan generation? This will use more tokens (y/n): ")

    if user_input.lower() == 'y':
        try:
            user_data = {
                'user_id': 12345,
                'name': 'Тест',
                'age': 25,
                'goals': 'стать программистом',
                'preferred_language': 'russian'
            }

            plan = await ai.generate_plan(user_data)

            print(f"   ✓ Plan generated successfully")
            print(f"   Years: {len(plan.get('years', []))}")
            print(f"   First year: {plan['years'][0]['title']}")

        except Exception as e:
            print(f"   ❌ Plan generation failed: {e}")
            return False
    else:
        print("   ⏭️  Skipped")

    # Test daily tasks generation (optional)
    print("\n7. Testing daily tasks generation (optional)...")
    user_input = input("   Test tasks generation? (y/n): ")

    if user_input.lower() == 'y':
        try:
            plan_data = {
                'user_id': 12345,
                'language': 'russian',
                'years': [
                    {
                        'year': 1,
                        'title': 'Основы программирования',
                        'milestones': ['Python', 'Git', 'Алгоритмы']
                    }
                ]
            }

            tasks = await ai.generate_daily_tasks(plan_data, day=1)

            print(f"   ✓ Tasks generated successfully")
            print(f"   Number of tasks: {len(tasks)}")
            for i, task in enumerate(tasks, 1):
                print(f"   {i}. {task}")

        except Exception as e:
            print(f"   ❌ Tasks generation failed: {e}")
            return False
    else:
        print("   ⏭️  Skipped")

    # Final summary
    print("\n" + "=" * 60)
    print("Test completed successfully! ✅")
    print("=" * 60)

    # Show final cost
    final_summary = cost_tracker.get_summary()
    print(f"\nTotal API cost: ${final_summary['total']['cost']:.4f}")
    print(f"Requests made: {final_summary['total']['requests']}")

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_claude_integration())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
