import os
from dotenv import load_dotenv
import googleapiclient.discovery
import isodate

load_dotenv()

def get_video_details(video_id, api_key):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(
        part="contentDetails,player",
        id=video_id
    )
    response = request.execute()
    video_details = response.get('items', [])[0]
    duration_iso = video_details['contentDetails']['duration']
    duration_parsed = isodate.parse_duration(duration_iso)
    embed_html = video_details['player']['embedHtml']
    return {
        'duration': str(duration_parsed),
        'embedHtml': embed_html
    }

def youtube_search(query, max_results=1):
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
    search_response = request.execute()
    results = []
    for item in search_response.get('items', []):
        video_info = {
            'title': item['snippet']['title'],
            'videoId': item['id']['videoId'],
            'description': item['snippet']['description'],
            'channelTitle': item['snippet']['channelTitle'],
            'publishedAt': item['snippet']['publishedAt'],
        }
        details = get_video_details(item['id']['videoId'], api_key)
        video_info['duration'] = details['duration']
        video_info['embedHtml'] = details['embedHtml']
        results.append(video_info)
    return results

