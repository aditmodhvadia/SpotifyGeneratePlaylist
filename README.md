# SpotifyYouTubeGeneratePlaylists
A simple python command line script that either converts your Spotify Playlists of songs to YouTube Playlist of videos or takes your liked videos on Youtube, and generates a Spotify playlist based on the song in your liked videos.

## Table of Contents
* [Video](#Video)
* [Technologies](#Technologies)
* [Setup](#LocalSetup)
* [ToDo](#ToDo)
* [Troubleshooting](#Troubleshooting)

## Video
Check out the youtube video for a step by step walk through 
[Youtube Video]

## Technologies
* [Youtube Data API v3]
* [Spotify Web API]
* [Requests Library v 2.22.0]
* [Youtube_dl v 2020.01.24]

## LocalSetup
1) Install All Dependencies   
`pip3 install -r requirements.txt`

2) Collect You Spotify User ID and Oauth Token From Spotfiy and add it to secrets.py file
    * To Collect your User ID, Log into Spotify then go here: [Account Overview] and its your **Username**
    ![alt text](images/userid.png)
    * To Collect your Oauth Token, Visit this url here: [Get Oauth] and click the **Get Token** button
    ![alt text](images/spotify_token.png)

3) Enable Oauth For Youtube and download the client_secrets.json   
    * Ok this part is tricky but its worth it! Just follow the guide here [Set Up Youtube Oauth] ! 
    If you are having issues check this out [Oauth Setup 2] and this one too [Oauth Setup 3]
    * **Note**: Choose desktop client when selecting the application type.  

4) Run the File  
`python3 create_playlist.py`   
    * You'll immediately see your browser opened and asking you to sign in into your google account. Select the appropriate account.
    * It will automatically collect your `authorization code`
    * You get to choose your option from the menu
    * Choose a playlist and it will create a YouTube playlist for you
    
## Use cases
1.  Trying to play songs from Spotify Playlists on [Discord] server using [Rhythm Bot] manually? Convert your spotify playlist to Youtube playlist and just play the playlist
2.  Want to watch your favorite music playlists music videos on screen, convert your playlist using SpotifyYouTubeGeneratePlaylist
3.  And many more......

## Limitation
1.   Google's API quota limit for a day is 10,000 counts. One search request costs 100 units and one playlist insert query costs 50 units. 
So I had to limit adding 50 videos per day.
2.  You have to manually update the Spotify authorization token after it expires every time.

## ToDo
* Tests
* Add Error Handling
* Pagination Handling (Spotify)
* Workaround for [Youtube Data API v3] daily quota limits for searching

## Troubleshooting
* Spotify Oauth token expires very quickly, If you come across a `KeyError` this could
be caused by an expired token. So just refer back to step 3 in local setup, and generate a new
token!
* Google's API quota limit for a day is 10,000 counts. One search request costs 100 units and one playlist insert query costs 50 units.
So I had to limit adding 50 videos per day.


   [Youtube Data API v3]: <https://developers.google.com/youtube/v3>
   [Spotify Web API]: <https://developer.spotify.com/documentation/web-api/>
   [Requests Library v 2.22.0]: <https://requests.readthedocs.io/en/master/>
   [Account Overview]: <https://www.spotify.com/us/account/overview/>
   [Get Oauth]: <https://developer.spotify.com/console/post-playlists/>
   [Set Up Youtube Oauth]: <https://developers.google.com/youtube/v3/getting-started/>
   [Oauth Setup 2]:<https://stackoverflow.com/questions/11485271/google-oauth-2-authorization-error-redirect-uri-mismatch/>
   [Youtube Video]:<https://www.youtube.com/watch?v=7J_qcttfnJA/>
   [Youtube_dl v 2020.01.24]:<https://github.com/ytdl-org/youtube-dl/>
   [Discord]:<https://discord.com/>
   [Rhythm Bot]:<https://rythmbot.co/>
   [Oauth Setup 3]:<https://github.com/googleapis/google-api-python-client/blob/master/docs/client-secrets.md/>