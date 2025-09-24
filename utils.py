import aiohttp
import os
from dotenv import load_dotenv
import asyncio 

load_dotenv()

async def keep_alive():
    while True:
        async with aiohttp.ClientSession() as session:
            try:
                await session.get("https://checkban-api-wotax.vercel.app/check?uid=2479382299")
            except:
                pass
        await asyncio.sleep(600)


async def check_ban(uid: str) -> dict | None:
    api_url = f"https://checkban-api-wotax.vercel.app/check?uid={uid}"
    
    timeout = aiohttp.ClientTimeout(total=30) 

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url) as response:

                response.raise_for_status() 

                response_data = await response.json()

                
                if response_data.get("status") == "success":
                    data = response_data.get("data")
                    if data: 
                        return {
                            "is_banned": data.get("is_banned", 0),
                            "nickname": data.get("nickname", ""),
                            "period": data.get("period", 0),
                            "region": data.get('region', "")
                        }
                
                return None
    except aiohttp.ClientError as e:
        print(f"API request failed for UID {uid}: {e}")
        return None
    except asyncio.TimeoutError:
        print(f"API request timed out for UID {uid}.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred for UID {uid}: {e}")
        return None
