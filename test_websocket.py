"""
Test WebSocket /stream endpoint
"""

import asyncio
import websockets
import json


async def test_stream_endpoint():
    """Test the /stream WebSocket endpoint"""
    uri = "ws://localhost:8000/agents/voice/stream"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Send a test message
            test_message = {
                "type": "message",
                "message": "Hello from test client",
                "context": {}
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent: {test_message}")
            
            # Receive responses
            timeout = 10  # 10 seconds timeout
            start_time = asyncio.get_event_loop().time()
            
            while True:
                try:
                    # Check for timeout
                    if asyncio.get_event_loop().time() - start_time > timeout:
                        print("⏱️  Timeout reached")
                        break
                    
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    print(f"📥 Received: {data.get('type')} - {data}")
                    
                    # Stop after completion
                    if data.get("type") == "completed":
                        print("✅ Test completed successfully")
                        break
                    
                    if data.get("type") == "error":
                        print(f"❌ Error: {data.get('error')}")
                        break
                
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Error receiving: {e}")
                    break
    
    except ConnectionRefusedError:
        print("❌ Connection refused - is the server running on port 8000?")
        print("   Start with: cd apps/agents && python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Connection error: {e}")


if __name__ == "__main__":
    print("🧪 Testing WebSocket /stream endpoint...")
    asyncio.run(test_stream_endpoint())
