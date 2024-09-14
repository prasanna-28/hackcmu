import os
from dotenv import load_dotenv
import googleapiclient.discovery

load_dotenv()

def youtube_search(query, max_results=5):
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("API Key not found in environment.")

    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    request = youtube.search().list(
        part="snippet",
        maxResults=max_results,
        q=query,
        type="video"
    )
    response = request.execute()

    results = []
    for item in response.get('items', []):
        video_info = {
            'title': item['snippet']['title'],
            'videoId': item['id']['videoId'],
            'description': item['snippet']['description'],
            'channelTitle': item['snippet']['channelTitle'],
            'publishedAt': item['snippet']['publishedAt'],
        }
        results.append(video_info)

    return results
