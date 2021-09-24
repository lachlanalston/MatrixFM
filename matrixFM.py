import requests, json, time, requests_cache
import numpy as np
import pandas as pd


API_KEY = '###'
USER_AGENT = 'MatrixFM'
url = 'https://ws.audioscrobbler.com/2.0/'
limit = 500
headers = {
    'user-agent': USER_AGENT
}    

#wk(ArtistName) -> getArtists(userName, ArtistName) -> getPlayCount()

def lastfm_get(payload):
    # define headers and URL
    headers = {'user-agent': USER_AGENT}
    url = 'https://ws.audioscrobbler.com/2.0/'

    # Add API key and format to the payload
    payload['api_key'] = API_KEY
    payload['format'] = 'json'

    response = requests.get(url, headers=headers, params=payload)
    return response

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def getFriends(userName):
	r = lastfm_get({
    	'method': 'user.getFriends',
    	'user': userName
	})
	r = r.json()['friends']['user']
	for i in r:
		print(i['name'])


def getRecentTracks(userName):
	r = lastfm_get({
    	'method': 'user.getRecentTracks',
    	'user': userName,
    	'limit': 1
	})
	r = r.json()
	r = r['recenttracks']['track']
	album = (r[0]['album'])['#text']
	artist = (r[0]['artist'])['#text']
	title = r[0]['name']

	try:
		playing = (r[0]['@attr'])['nowplaying']
		print(userName + " currently playing " + title + " - " + album + " - " + artist)
	except Exception:
		print(userName+" not playing anything")	
	
def pages(userName):
	r = lastfm_get({
    	'method': 'library.getArtists',
    	'user': userName,
    	'limit': limit
    	})
	r = r.json()
	r = r['artists']['@attr']
	total = r['totalPages']
	return int(total)
	
def wk(artistName):
	usernames = pd.read_json('usernames.json')
	for i in range(len(usernames)):
		try:
			user = usernames.loc[i, 'usernames']
			value = getArtists(user, artistName)
			print(user +" "+ value)
		except Exception:
			print(user + " doesn't know " + artistName)
def getArtists(userName, artistName):

	responses = []
	
	page = 1
	total_pages = pages(userName)
	
	while page <= total_pages:
		payload = {
			'method':'library.getArtists',
			'user': userName,
			'limit': limit,
			'page': page
		}
		
		#print("Requesting page {}/{}".format(page, total_pages))

		clear_output(wait = True)
		response = lastfm_get(payload)
		
		if response.status_code != 200:
			print(response.text)
			return
	
		page = int(response.json()['artists']['@attr']['page'])
		total_pages = int(response.json()['artists']['@attr']['totalPages'])

		responses.append(response)

		if not getattr(response, 'from_cache', False):
        		time.sleep(0.25)

		page += 1	
		
	r0 = responses[0]
	r0_json = r0.json()
	r0_artists = r0_json
	r0_df = pd.DataFrame(r0_artists)
	frames = [pd.DataFrame(r.json()['artists']['artist']) for r in responses]
	artists = pd.concat(frames)
		
	artists = artists.drop(columns='url')
	artists = artists.drop(columns='mbid')
	artists = artists.drop(columns='streamable')
	artists = artists.drop(columns='image')
	artists = artists[["name","playcount","tagcount"]]
	playCount = artists.loc[artists['name'] == artistName]
	name = playCount['name'].values[0]
	playcount = playCount['playcount'].values[0]
	return (name +" "+  playcount)
	
def createUsernameJson():
	df = ['']
	df = pd.DataFrame(df, columns=['usernames'])
	df.to_json('usernames.json')

#wk('Elliott Smith')
