import json
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import pydantic
from typing import List, Optional

load_dotenv(override=True)

class YtComments(pydantic.BaseModel):
    video: str # ['snippet']['videoId']
    text: str # ['snippet']['topLevelComment']['snippet']['textOriginal']
    commentor: str # "" authorDisplayName 
    commentor_dp: str # "" authorProfileImageUrl
    commentor_channel: str # "" authorChannelUrl
    likes: int # "" likeCount
    replies: int # "" totalReplyCount
    
class YtSearchResultVideo(pydantic.BaseModel):
    video_id: str
    title: str
    channel_name: str
    video_url: str
    thumbnail_url: str
    description: str
    published_at: str
    
class YtSearchResult(pydantic.BaseModel):
    total_results: int
    results_per_page: int
    next_page_token: Optional[str] = None 
    videos: List[YtSearchResultVideo]

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
            
            video_objects_list = []
            
            for item in search_response.get("items", []):
                if item.get("id", {}).get("kind") == "youtube#video":
                    
                    snippet = item.get("snippet", {})
                    vid_id = item.get("id", {}).get("videoId")

                    video_obj = YtSearchResultVideo(
                        video_id=vid_id,
                        title=snippet.get("title", ""),
                        channel_name=snippet.get("channelTitle", ""),
                        video_url=f"https://www.youtube.com/watch?v={vid_id}",
                        thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                        description=snippet.get("description", ""),
                        published_at=snippet.get("publishedAt", "")
                    )
                    video_objects_list.append(video_obj)
            
            search_result = YtSearchResult(
                total_results=search_response.get("pageInfo", {}).get("totalResults", 0),
                results_per_page=search_response.get("pageInfo", {}).get("resultsPerPage", 0),
                next_page_token=search_response.get("nextPageToken", ""),
                videos=video_objects_list
            )
            
            return search_result
        
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
# print(yt.youtube_search("Ken broken cycle"))
# yt.get_top_comments('VMQ4c3XK6CI', max_results=5)

