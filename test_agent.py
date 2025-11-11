"""
Simple test script for agent system
Tests basic supervisor functionality without full FastAPI server
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_simple_supervisor():
    """
    Test simple supervisor without sub-agents
    """
    print("=" * 60)
    print("Testing Simple Supervisor")
    print("=" * 60)
    
    try:
        from agents.supervisor import create_simple_supervisor
        
        # Create simple supervisor
        workflow = create_simple_supervisor()
        
        # Test input
        test_message = "What are the key steps to create a professional video?"
        
        print(f"\n📨 User: {test_message}\n")
        
        # Execute workflow
        result = workflow.invoke({
            "messages": [{"role": "user", "content": test_message}]
        })
        
        # Print response
        for msg in result["messages"]:
            if hasattr(msg, "content"):
                role = "User" if msg.type == "human" else "Assistant"
                print(f"💬 {role}: {msg.content}\n")
        
        print("✅ Simple supervisor test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing simple supervisor: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_supervisor():
    """
    Test full supervisor with all sub-agents
    """
    print("\n" + "=" * 60)
    print("Testing Full Supervisor with Sub-Agents")
    print("=" * 60)
    
    try:
        from agents.supervisor import create_supervisor_workflow
        
        # Create full supervisor
        workflow = create_supervisor_workflow()
        
        # Test input
        test_message = "I need to create a 30-second product demo video"
        
        print(f"\n📨 User: {test_message}\n")
        
        # Execute workflow with config
        config = {
            "configurable": {
                "thread_id": "test-thread-1"
            }
        }
        
        result = workflow.invoke({
            "messages": [{"role": "user", "content": test_message}]
        }, config)
        
        # Print all messages
        print("\n📋 Agent Conversation:\n")
        for i, msg in enumerate(result["messages"], 1):
            if hasattr(msg, "content") and msg.content:
                role = "User" if msg.type == "human" else "Agent"
                name = getattr(msg, "name", "System")
                print(f"{i}. [{role}] {name}")
                print(f"   {msg.content[:200]}...")
                print()
        
        print("✅ Full supervisor test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing full supervisor: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_health_check():
    """
    Test server health endpoint
    """
    print("\n" + "=" * 60)
    print("Testing Server Health")
    print("=" * 60)
    
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            
            if response.status_code == 200:
                print(f"✅ Server is healthy: {response.json()}")
                return True
            else:
                print(f"❌ Server returned status {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("⚠️  Server not running. Start with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error testing health: {e}")
        return False


async def main():
    """
    Run all tests
    """
    print("\n🧪 OpenCut Agent System Tests\n")
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Copy .env.example to .env and add your API keys")
        return
    
    print("✅ Environment variables loaded\n")
    
    # Run tests
    results = []
    
    # Test 1: Simple supervisor
    results.append(await test_simple_supervisor())
    
    # Test 2: Full supervisor (may fail if dependencies missing)
    results.append(await test_full_supervisor())
    
    # Test 3: Server health (only if server is running)
    results.append(await test_health_check())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("   Check error messages above for details")


if __name__ == "__main__":
    asyncio.run(main())
