import asyncio
import httpx
import json

async def test_agent():
    url = "http://localhost:8081/api/analyze"
    payload = {
        "prompt": "90210",
        "session_id": "test_script_session_1",
        "user_id": "test_script_user"
    }
    
    print(f"Sending request to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60.0)
            
            print(f"Status Code: {response.status_code}")
            try:
                # Assuming streaming response, let's just collect the text
                print("Response text:", response.text)
            except Exception as e:
                print("Could not read response text:", e)
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent())
