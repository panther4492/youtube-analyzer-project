from googleapiclient.discovery import build
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from config import API_KEY

# Initialize YouTube API
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Get channel info
def get_channel_stats(channel_id):
    request = youtube.channels().list(
        part='snippet,statistics,contentDetails',
        id=channel_id
    )
    response = request.execute()

    if not response['items']:
        print("Invalid Channel ID")
        return None

    data = response['items'][0]

    channel_stats = {
        'channelTitle': data['snippet']['title'],
        'subscribers': int(data['statistics'].get('subscriberCount', 0)),
        'totalViews': int(data['statistics'].get('viewCount', 0)),
        'totalVideos': int(data['statistics'].get('videoCount', 0)),
        'uploadsPlaylist': data['contentDetails']['relatedPlaylists']['uploads']
    }

    return channel_stats

# Get videos from upload playlist
def get_video_ids(playlist_id):
    video_ids = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

# Get video stats
def get_video_details(video_ids):
    stats = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute()

        for video in response['items']:
            snippet = video['snippet']
            statistics = video['statistics']

            stats.append({
                'title': snippet['title'],
                'published': snippet['publishedAt'],
                'views': int(statistics.get('viewCount', 0)),
                'likes': int(statistics.get('likeCount', 0)),
                'comments': int(statistics.get('commentCount', 0))
            })

    return pd.DataFrame(stats)

# Visualize
def visualize(df, channel_stats):
    print("\n📊 Channel Statistics:")
    print(f"Channel Name: {channel_stats['channelTitle']}")
    print(f"Subscribers: {channel_stats['subscribers']:,}")
    print(f"Total Views: {channel_stats['totalViews']:,}")
    print(f"Total Videos: {channel_stats['totalVideos']}")

    df['published'] = pd.to_datetime(df['published'])
    df = df.sort_values('published')

    plt.figure(figsize=(10,5))
    plt.plot(df['published'], df['views'], marker='o')
    plt.title('Views Over Time')
    plt.xlabel('Publish Date')
    plt.ylabel('Views')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid()
    plt.show()

    top_video = df.sort_values('views', ascending=False).iloc[0]
    print("\n🔥 Most Popular Video:")
    print(f"Title: {top_video['title']}")
    print(f"Views: {top_video['views']:,}")
    print(f"Published on: {top_video['published'].date()}")

# Main
if __name__ == "__main__":
    # Example: TechBurner Channel ID
    channel_id = input("Enter YouTube Channel ID: ")

    channel_stats = get_channel_stats(channel_id)
    if channel_stats:
        video_ids = get_video_ids(channel_stats['uploadsPlaylist'])
        df = get_video_details(video_ids)
        visualize(df, channel_stats)
        
