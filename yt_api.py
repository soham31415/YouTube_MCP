import json
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import pydantic

load_dotenv(override=True)

class YtComments(pydantic.BaseModel):
    video: str # ['snippet']['videoId']
    text: str # ['snippet']['topLevelComment']['snippet']['textOriginal']
    commentor: str # "" authorDisplayName 
    commentor_dp: str # "" authorProfileImageUrl
    commentor_channel: str # "" authorChannelUrl
    likes: int # "" likeCount
    replies: int # "" totalReplyCount

class YoutubeAPI:
    def __init__(self):
        self.YT_KEY = os.getenv("API_KEY")
        self.YT_SERVICE_NAME = "youtube"
        self.YT_API_VERSION = "v3"
        self.yt = build(
                self.YT_SERVICE_NAME,
                self.YT_API_VERSION,
                developerKey=self.YT_KEY
            )

    def youtube_search(self, query: str):
        try: 
            search_response = self.yt.search().list(
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

    def get_top_comments(self, video_id: str, max_results=50):
        try: 
            comments = self.yt.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                textFormat='plainText'
            ).execute()
            # print(f'Res:\n{comments}')
            print(f"--- Comments for: '{video_id}' ---")
            result = []
            for i,item in enumerate(comments.get("items", [])):

                top = item.get('snippet').get('topLevelComment').get('snippet') 
                
                text=top.get('textOriginal', '')
                commentor=top.get('authorDisplayName', '')
                commentor_dp=top.get('authorProfileImageUrl', '')
                commentor_channel=top.get('authorChannelUrl', '')
                likes=top.get('likeCount', 0)
                replies=top.get('totalReplyCount', 0)
            

                comment = YtComments(
                    video=video_id,
                    text=text,
                    commentor=commentor,
                    commentor_dp=commentor_dp,
                    commentor_channel=commentor_channel,
                    likes=likes,
                    replies=replies
                )
                print(f'Comment {i}: \n{comment.model_dump_json(indent=2)}')
                result.append(comment)
            print("------------------------------------------")
            return result
        except Exception as e:
            print(f'Oops: {e}')

yt = YoutubeAPI()    
# yt.youtube_search("A game faln song")
yt.get_top_comments('VMQ4c3XK6CI', max_results=5)

