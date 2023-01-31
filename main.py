import  requests, subprocess, os, datetime, base64
from dotenv import load_dotenv
load_dotenv()
spotify_client_id   = os.getenv("spotify_client_id")
spotify_secret      = os.getenv("spotify_secret")
youtube_api_key     = os.getenv("youtube_api_key")

def log_details(content):
    file = open('logs.txt', 'a')
    file.write("\n"+content)
    file.close()

def download_video(video_id, track_name):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    video_file = os.path.join(os.getcwd()+"/downloads", f"{track_name}.mp4")
    subprocess.call(["youtube-dl", "--no-check-certificate", "--no-continue", "--no-part", "--no-playlist", "-f", "mp4", "-o", video_file, video_url])
    log_details(f"downloaded video for track : {track_name},  {datetime.datetime.now()}")

def get_access_token():
    auth_header = {
        "Authorization": f"Basic {base64.b64encode(f'{spotify_client_id}:{spotify_secret}'.encode()).decode()}"
    }
    auth_data = {
        "grant_type": "client_credentials"
    }

    response = requests.post("https://accounts.spotify.com/api/token", headers=auth_header, data=auth_data)

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        return access_token
    else:
        log_details(f"Failed to fetch access token, response content : {response.content}, {datetime.datetime.now()}")
        print("Failed to fetch access token!")
        exit()

def get_track_data(track):
    youtube_search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={track['track']['name']}+{track['track']['artists'][0]['name']}&type=video&key={youtube_api_key}"
    youtube_search_response = requests.get(youtube_search_url)

    if youtube_search_response.status_code == 200:
        video_id = youtube_search_response.json()["items"][0]["id"]["videoId"]
        download_video(video_id=video_id, track_name=track["track"]["name"])
    else:
        log_details(f"Failed to search for video for track {track['track']['name']}, response content : {youtube_search_response.content}, {datetime.datetime.now()}")

def get_playlist_id(link):
    parts = link.split("?")
    playlist_id = parts[0].split("/")[-1]
    return playlist_id

def main():
    playlist_link = input()
    spotify_playlist_id = get_playlist_id(link=playlist_link)

    spotify_access_token = get_access_token()
    playlist_url = f"https://api.spotify.com/v1/playlists/{spotify_playlist_id}/tracks"

    playlist_response = requests.get(playlist_url, headers={
        "Authorization": "Bearer " + spotify_access_token
    })

    if playlist_response.status_code == 200:
        tracks = playlist_response.json()["items"]
        for track in tracks:
            get_track_data(track=track)
    else:
        log_details(f"Failed to retrieve playlist for playlist id : {spotify_playlist_id}, response content : {playlist_response.content}, {datetime.datetime.now()}")
        print("Failed to retrieve playlist!")
    print("Finished executing!")

if __name__ == '__main__':
    main()