import json
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv(override=True)
YT_KEY = os.getenv("API_KEY")
YT_SERVICE_NAME = "youtube"
YT_API_VERSION = "v3"

def youtube_search(query: str):
    try:
        yt = build(
            YT_SERVICE_NAME,
            YT_API_VERSION,
            developerKey=YT_KEY
        )
        
        search_response = yt.search().list(
            q=query,
            part="snippet",
            maxResults=5
        ).execute()
        
        print(f"--- Search results for: '{query}' ---")
        for item in search_response.get("items", []):
            if item["id"]["kind"] == "youtube#video":
                title = item["snippet"]["title"]
                video_id = item["id"]["videoId"]
                print(f"Video: {title} (ID: {video_id})")
        
        print("------------------------------------------")
        
        print(json.dumps(search_response))
        
        return search_response
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
youtube_search("A game faln song")

