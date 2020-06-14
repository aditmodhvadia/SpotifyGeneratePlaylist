import json
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests
import youtube_dl

from exceptions import ResponseException
from secrets import spotify_token, spotify_user_id


def get_youtube_client():
    """ Log Into Youtube, Copied from Youtube Data API """
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client, this allows full read write access
    scopes = ["https://www.googleapis.com/auth/youtube"]
    # scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    # scopes = ["https://www.googleapis.com/auth/youtube.read-only"]
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server()

    youtube_client = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    return youtube_client


def create_spotify_playlist() -> str:
    """
    Create A New Spotify Playlist
    :return: id of newly created Spotify playlist
    """
    request_body = json.dumps({
        "name": "Youtube Liked Vids",
        "description": "All Liked Youtube Videos",
        "public": True
    })

    query = "https://api.spotify.com/v1/users/{}/playlists".format(
        spotify_user_id)
    response = requests.post(
        query,
        data=request_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)
        }
    )
    response_json = response.json()

    # playlist id
    return response_json["id"]


def search_and_get_spotify_uri(song_name: str, artist: str) -> str:
    """
    Search For the Song in Spotify
    :param song_name: Name of the song
    :param artist: Name of the Artist
    :return: URI of the song searched
    """
    query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
        song_name,
        artist
    )
    response = requests.get(
        query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)
        }
    )
    response_json = response.json()
    songs = response_json["tracks"]["items"]

    # only use the first song
    uri = songs[0]["uri"]

    return uri


def list_spotify_playlists():
    """
    Get a List of Current User's Playlists
    :return: List of user's playlists
    """

    url = "https://api.spotify.com/v1/me/playlists"
    response = requests.get(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)
        }
    )
    response_json = response.json()

    return response_json


def list_spotify_playlist_items(playlist_id: str):
    """
    Get a Spotify Playlist's Items
    :param playlist_id: Spotify Playlist id
    :return: List of given playlist items
    """
    # only get the items and their track names and artists names
    # for now just fetching the first 100 items in the playlist
    url = "https://api.spotify.com/v1/playlists/{}/tracks?items(track(name%2Cartists(name)))&limit=50&offset=0".format(
        playlist_id)
    response = requests.get(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify_token)
        }
    )
    response_json = response.json()

    return response_json


class CreatePlaylist:
    def __init__(self):
        self.youtube_client = get_youtube_client()
        self.all_song_info = {}

    def get_youtube_liked_videos(self):
        """Grab Our Liked Videos from YouTube & Create A Dictionary Of Important Song Information"""
        request = self.youtube_client.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like",
            maxResults=50
        )
        response = request.execute()

        print("Found", response["pageInfo"]["totalResults"], "songs from YouTube playlist")

        # collect each video and get important information
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["id"])

            print("YouTube URL:", youtube_url, "Title:", video_title)

            # use youtube_dl to collect the song name & artist name
            video = youtube_dl.YoutubeDL({}).extract_info(
                youtube_url, download=False)
            song_name = video["track"]
            artist = video["artist"]

            print("Song Name:", song_name, "Artist:", artist)

            if song_name is not None and artist is not None:
                # save all important info and skip any missing song and artist
                self.all_song_info[video_title] = {
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,
                    # add the uri, easy to get song to put into playlist
                    "spotify_uri": search_and_get_spotify_uri(song_name, artist)

                }

    def add_favorite_youtube_song_to_new_spotify_playlist(self):
        """Add all liked songs into a new Spotify playlist"""
        # populate dictionary with our liked songs
        self.get_youtube_liked_videos()

        # collect all of uri
        uris = [info["spotify_uri"]
                for song, info in self.all_song_info.items()]

        # create a new playlist
        playlist_id = create_spotify_playlist()

        # add all songs into new playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        # check for valid response status
        if response.status_code != 200 and response.status_code != 201:
            raise ResponseException(response.status_code)

        response_json = response.json()
        return response_json

    def add_songs_to_new_youtube_playlist(self, playlist_name, spotify_items):
        """
        Create a new youtube playlist and add all the songs received from spotify
        by searching using the track name and artist name
        :return:
        """
        # create a new youtube playlist
        youtube_playlist = self.create_new_youtube_playlist(playlist_name)
        print("Created new YouTube Playlist", youtube_playlist["id"], youtube_playlist["snippet"]["title"])
        youtube_video_ids = []

        # search for every song from spotify in youtube and get the id for the video
        for spotify_song in spotify_items:
            youtube_video_ids.insert(0, self.get_youtube_video_id(
                "{} {} Official Music Video".format(spotify_song["track"]["name"],
                                                    spotify_song["track"]["artists"][0][
                                                        "name"])))

        print(youtube_video_ids)
        # add all the videos searched for the song to the newly created youtube playlist one by one with a delay of
        self.add_to_youtube_playlist(youtube_video_ids, playlist_id=youtube_playlist["id"])

    def get_youtube_video_id(self, search_str):
        """
        Search for a YouTube video given the search string
        :param search_str: given search string
        :return: YouTube video ID
        """
        request = self.youtube_client.search().list(
            part="snippet",
            maxResults=1,
            q=search_str
        )
        response = request.execute()
        print(response["items"][0]["id"]["videoId"])
        return response["items"][0]["id"]["videoId"]

    def create_new_youtube_playlist(self, playlist_title):
        """
        Create a new YouTube playlist with given title
        :param playlist_title: Playlist title
        :return: Newly created playlist
        """
        request = self.youtube_client.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": playlist_title,
                    "description": "This playlist consists of songs from Spotify. Created using "
                                   "Spotify Youtube Generate Playlist.",
                    "tags": [
                        "Spotify Playlist",
                        "API call"
                    ],
                    "defaultLanguage": "en"
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
        )
        response = request.execute()

        return response

    def add_to_youtube_playlist(self, youtube_video_ids, playlist_id: str):
        """
        Add all the videos with given video ID to the given playlist id
        :param playlist_id: Playlist ID to add the videos to
        :param youtube_video_ids: List of ids of videos to add to the playlist
        :return:
        """
        for video_id in youtube_video_ids:
            request = self.youtube_client.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )
            response = request.execute()
            # time.sleep(3)

        print("Added videos to YouTube")


if __name__ == '__main__':
    cp = CreatePlaylist()
    selection = int(eval(input(
        "Choose your option \n1. Add Spotify Playlists songs to new YouTube playlist"
        " \n2. Add YouTube liked video to new Spotify playlist\n")))
    if selection == 1:
        # List all spotify playlist
        play_lists = list_spotify_playlists()
        print("Found", play_lists["total"], "playlists")
        index = 1
        for playlist in play_lists["items"]:
            print(index, "Name:", playlist["name"], playlist["tracks"]["total"], "tracks")
            index += 1

        playlist_index = int(input("\nEnter the index of the playlist: ")) - 1

        # Get list of track items in the selected Spotify playlist
        playlist_items = list_spotify_playlist_items(play_lists["items"][playlist_index]["id"])
        # Add spotify track items to new YouTube playlist
        cp.add_songs_to_new_youtube_playlist(playlist_name=play_lists["items"][playlist_index]["name"],
                                             spotify_items=playlist_items["items"])

    elif selection == 2:
        cp.add_favorite_youtube_song_to_new_spotify_playlist()
        print("Task complete")
    else:
        print("Thank you")
