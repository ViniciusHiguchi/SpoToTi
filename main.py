# -*- coding: utf-8 -*-
"""
Created on Sun Aug  6 01:20:14 2023

@author: vinic
"""

# -*- coding: utf-8 -*-
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "playlist-read-private,user-library-read,user-follow-read"

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, cache_path='cache.txt'))

#%%
class Album():
    
    def __init__(self, sid):
        self.raw = spotify.album(sid)
        self.album = {'title' : '', 'artists': [], 'tracks' : []}
        for track in self.raw['tracks']['items']:
            self.album['tracks'].append(track['track'])
        self.album['title'] = self.raw['name']
        self.album['artists'] = [x['name'] for x in self.raw['artists']]
        
    def dic(self): return self.album
    
    
class Artist():
    
    def __init__(self, sid):
        self.raw = spotify.artist(sid)
        self.artist = {'name' : '', 'albums' : []}
        self.artist['name'] = self.raw['name']
        albums_raw = spotify.artist_albums(sid)
        artist['albums'] = [x for i in raw[]]
        
    def dic(self): return self.playlist


class Playlist():
    
    def __init__(self, playlist_id):
        self.raw = spotify.playlist(playlist_id)
        self.playlist = {'title' : '', 'tracks' : []}
        for track in self.raw['tracks']['items']:
            self.playlist['tracks'].append(track['track'])
        self.playlist['title'] = self.raw['name']
        
    def dic(self): return self.playlist


class Lib():
    
    def __init__(self):
        self.liked_songs = getAllResults(spotify.current_user_saved_tracks(limit = 50, offset = 0))
        self.lib = []
        for results in self.liked_songs:
            for item in results['items']:
                self.lib.append(item['track'])
        
    def dic(self): return self.lib


def getAllResults(results):
    if 'artists' in results.keys(): results = results['artists']
    arr = [results]
    while results['next']:
        results = spotify.next(results)
        arr.append(results)
    return arr

#%%
playlists = getAllResults(spotify.current_user_playlists(limit = 50, offset = 0))
albums = getAllResults(spotify.current_user_saved_albums(limit = 50))
artists = getAllResults(spotify.current_user_followed_artists(limit = 50)['artists'])

#%%
playl_objs = []
for result in playlists:
    for j in result['items']:
        playl_objs.append(Playlist(j['uri']))
        #%%
album_objs = []
for result in albums:
    for j in result['items']:
        album_objs.append(Album(j['album']['uri']))
        
artist_objs = []
for result in artists:
    for j in result['items']:
        artist_objs.append(Artist(j['uri']))
#%%
        
playlists = [x.dic() for x in playl_objs]
albums = [x.dic() for x in album_objs]
artists = [x.dic() for x in artist_objs]