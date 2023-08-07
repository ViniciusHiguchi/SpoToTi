# -*- coding: utf-8 -*-
"""
Created on Sun Aug  6 01:20:14 2023

@author: vinic
"""

# -*- coding: utf-8 -*-
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "playlist-read-private,user-library-read,user-follow-read"
#setting up spotify client
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, cache_path='cache.txt'))

#%%
#Setting up objects to automate requisitions to the api and have a standard dict/class to work on
#
#
#
class Album():
    
    def __init__(self, raw):
        self.raw = raw
        self.album = {'title' : '', 'artists': [], 'tracks' : [], 'tid' : None}
        for item in self.raw['tracks']['items']:
            self.album['tracks'].append(item)
        self.album['title'] = self.raw['name']
        self.album['artists'] = [{'name': x['name'], 'sid' : x['uri']} for x in self.raw['artists']]
        
    #most of these methods won't be used. Remove later
    def dic(self): return self.album
    
    def artist(self): return self.album['title']
    
    def tracks(self): return self.album['tracks']
    
    def set_tidalid(self, tid): self.album['tid'].update({'tid' : tid})
    
    
class Artist():
    
    def __init__(self, raw=None, sid=None):
        if not raw:
            raw = spotify.artist(sid)
        self.raw = raw
        self.sid = raw['uri']
        self.artist = {'name' : '', 'albums' : []}
        self.artist['name'] = self.raw['name']
        self.name = self.artist['name']
        
    def _setAlbums(self):
        self.albums_raw = spotify.artist_albums(self.sid)
        self.artist['albums'] = [x['name'] for x in self.albums_raw['items']]
        
    def dic(self): return self.artist
    
    #def artist(self): return self.artist['name']
    
    #def albums(self): return self.artist['name']


class Playlist():
    
    def __init__(self, playlist_id):
        self.raw = spotify.playlist(playlist_id)
        self.playlist = {'title' : '', 'tracks' : []}
        for track in self.raw['tracks']['items']:
            self.playlist['tracks'].append(track['track'])
        self.playlist['title'] = self.raw['name']
        
    def dic(self): return self.playlist
    
    def tracks(self): return self.playlist['tracks']

    
#class to host liked songs items, 
#could be made into a dict, but i feel like it is more orgazined and scalable this way (could easily add support for other platforms, etc...)
class Lib():
    
    def __init__(self):
        self.liked_songs = getAllResults(spotify.current_user_saved_tracks(limit = 50, offset = 0))
        self.lib = []
        for results in self.liked_songs:
            for item in results['items']:
                self.lib.append(item['track'])
        
    def dic(self): return self.lib

#function to handle paginated requests from spotipy
def getAllResults(results):
    if 'artists' in results.keys(): results = results['artists']
    arr = [results]
    while results['next']:
        results = spotify.next(results)
        arr.append(results)
    return arr

#gather all artists from any source in a dict. 
#This facilitates acessing the artist catalog and indexing id's to use in the receiver platform
def collectAllArtists(col):
    for i in album_objs:
        for j in i.album['artists']:
            col.update({j['name']: {'tid':None, 'sid':j['sid'], 'self':j['name'], 'albums' : {}}})
            
    for i in lib.lib:
        for j in i['artists']:
            col.update({j['name']: {'tid':None, 'sid':j['uri'], 'self' : j['name'], 'albums' : {}}})
            
    for i in playlists:
        for j in i['playlist']['tracks']:
            for k in j['artists']:
                col.update({k['name']: {'tid':None, 'sid':k['uri'], 'self' : k['name'], 'albums' : {}}})
                
    for i in artist_objs:
        col.update({i.name: {'tid' : None, 'sid' : i.sid, 'self':i.name, 'albums' : {}}})
        
#same idea here, this is used alongside with the artist_collection to complete the catalog of all the relevant songs an user has in their library
def collectAllSongs(col):
    
    for i in lib.lib:
            col.update({i['name'] : {'tid':None, 'sid':i['uri'], 'self' : i['name'], 'artist' : i['album']['artists'][0]['name'], 'album' : i['album']['name']}})
    
    for i in playlists_d:
        for j in i['tracks']:
            col.update({j['name'] : {'tid':None, 'sid':j['uri'], 'self' : j['name'], 'artist' : j['artists'][0]['name'], 'album' : j['album']['name']}})
        
        
#%%
#getting the paginated requests into lists (each index is a page) 
playlists = getAllResults(spotify.current_user_playlists(limit = 50, offset = 0))
albums = getAllResults(spotify.current_user_saved_albums(limit = 50))
artists = getAllResults(spotify.current_user_followed_artists(limit = 50)['artists'])


'''
col.update({k['name']: {'tid':None, 'sid':k['uri'], 'self' : k['name'],
                'albums' : {j['album']['name'] : {'tid':None, 'sid':j['album']['uri'], 'self':j['album']['name']}}
                        }})
'''
#%%
lib = Lib() #starting the Lib object

#normalizing all the requests into their respective objects
playl_objs = []
for result in playlists:
    for j in result['items']:
        #this takes time, because playlists from spotify.current_user_playlists don't bring tracks along with the data
        #so the playlists have to be requested one by one using the __init__ method
        playl_objs.append(Playlist(j['uri']))

#luckily, these two already bring all the data needed to index the user library
album_objs = []
for result in albums:
    for j in result['items']:
        album_objs.append(Album(j['album']))
        
artist_objs = []
for result in artists:
    for j in result['items']:
        artist_objs.append(Artist(raw = j))
        
#this has been used for debug, because Spyder can't access my classes. There should be a fix for this
playlists_d = [x.dic() for x in playl_objs]
albums_d = [x.dic() for x in album_objs]
artists_d = [x.dic() for x in artist_objs]

#%%
#both dicitionaries used to create library catalog
#not the best way, but good enough
artist_collection = {}
song_collection = {}

collectAllArtists(artist_collection)
collectAllSongs(song_collection)

#creating entries for albums in each artist based on song_collection info
#the hierarchy of the dictionary follows:
#{artist : {
#     ...   
#     albums: {
#           album0_key : {..., tracks:[track0_dict, track1_dict...]}
#             }
#          }
#}
#artist, albums, and tracks dicts all have a 'self' key, with value referencing the key that leads to that dict (artist name, album title, track title)
#
for k, v in song_collection.items():
    if v['album'] not in artist_collection[v['artist']]['albums'].keys():
        artist_collection[v['artist']]['albums'].update({v['album'] : {'self' : v['album'], 'tracks': [v]}})
    else:
        artist_collection[v['artist']]['albums'][v['album']]['tracks'].append(v)

#now we have to index all Tidal id's into the artist_collection
#later, we use the objs arrays along with the indexed collection to create the playlists, like the songs, and follow artists and albums in Tidal











    
    
