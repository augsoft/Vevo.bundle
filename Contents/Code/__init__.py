# VEVO
VEVO_TITLE_INFO             = 'http://videoplayer.vevo.com/VideoService/AuthenticateVideo?isrc=%s&authToken=%s&domain=http://www.vevo.com'
VEVO_API_URL                = 'http://api.vevo.com/mobile/v1/%s/list.json'
VEVO_URL                    = 'http://www.vevo.com'
VIDEO_URL                   = 'http://www.vevo.com/watch/%s/%s/%s'
ARTIST_VIDEOS_URL           = 'http://www.vevo.com/data/artist/%s'
SEARCH_URL                  = 'http://api.vevo.com/mobile/v1/lookahead.json?q=%s&fullItems=true&newSearch=yes'

VIDEO_PREFIX = "/video/vevo"
NAME = 'Vevo'
ART  = 'art-default.jpg'
ICON = 'icon-default.png'
SEARCHICON = 'search.png'

CACHE_TIME = 3600

####################################################################################################
def Start():

    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, L('Title'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)
    
    HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
#Navigation
def MainMenu():

    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(VideosSubMenu), title = "Videos"))
    oc.add(DirectoryObject(key=Callback(ArtistsSubMenu), title = "Artists"))
    oc.add(DirectoryObject(key=Callback(AllGenresSubMenu), title = "Genres"))
    ### write a search service ###
    oc.add(DirectoryObject(key=Callback(SearchMenu), title="Search", thumb=R(SEARCHICON)))
    
    return oc

####################################################################################################
def SearchMenu():
    oc = ObjectContainer(title2="Search")
    oc.add(InputDirectoryObject(key=Callback(ArtistSearch), title="Search for Artists", prompt="Search for...",
        thumb=R(SEARCHICON)))
    oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.vevo", title="Search for Videos", prompt="Search for...",
        thumb=R(SEARCHICON)))
    return oc

####################################################################################################
def ArtistSearch(query):
    oc = ObjectContainer(title2='Search Results')
    results = JSON.ObjectFromURL(SEARCH_URL % query)['Artists']
    for artist in results:
        title = artist['name']
        thumb = artist['img']
        oc.add(DirectoryObject(key=Callback(ArtistVideoListing, name=title, urlsafe_name=artist['urlKey']), title=title,
            thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))
    if len(oc) == 0:
        return ObjectContainer(header=NAME, message="Sorry. No results found")
    return oc

####################################################################################################
def VideosSubMenu(title=None, genre=None):
    if title:
        oc = ObjectContainer(title1="Videos", title2=title)
    else:
        oc = ObjectContainer(title2="Videos")

    oc.add(DirectoryObject(key=Callback(VideoListing, title="Most Recent", request="MostRecent", genres=genre), title="Most Recent"))
    oc.add(DirectoryObject(key=Callback(VideoListing, title="Most Viewed today", request="MostViewedToday", genres=genre), title="Most Viewed today"))
    oc.add(DirectoryObject(key=Callback(VideoListing, title="Most Viewed this week", request="MostViewedThisWeek", genres=genre), title="Most Viewed this week"))
    oc.add(DirectoryObject(key=Callback(VideoListing, title="Most Viewed this month", request="MostViewedThisMonth", genres=genre), title="Most Viewed this month"))
    oc.add(DirectoryObject(key=Callback(VideoListing, title="Most Viewed of All Time", request="MostViewedAllTime", genres=genre), title="Most Viewed of All Time"))
    
    return oc

####################################################################################################
def ArtistsSubMenu(title=None, genre=None):
    if title:
        oc = ObjectContainer(title1="Videos", title2=title)
    else:
        oc = ObjectContainer(title2="Videos")

    oc.add(DirectoryObject(key=Callback(ArtistListing, title="Most Recent", request="MostRecent", genres=genre), title="Most Recent"))
    oc.add(DirectoryObject(key=Callback(ArtistListing, title="Most Viewed today", request="MostViewedToday", genres=genre), title="Most Viewed today"))
    oc.add(DirectoryObject(key=Callback(ArtistListing, title="Most Viewed this week", request="MostViewedThisWeek", genres=genre), title="Most Viewed this week"))
    oc.add(DirectoryObject(key=Callback(ArtistListing, title="Most Viewed this month", request="MostViewedThisMonth", genres=genre), title="Most Viewed this month"))
    oc.add(DirectoryObject(key=Callback(ArtistListing, title="Most Viewed of All Time", request="MostViewedAllTime", genres=genre), title="Most Viewed of All Time"))
    
    return oc

####################################################################################################
def AllGenresSubMenu():
    oc = ObjectContainer()
    genres = JSON.ObjectFromURL(VEVO_API_URL % 'genre')['result']
    for genre in genres:
        oc.add(DirectoryObject(key=Callback(GenreSubMenu, title=genre['Value'], genre=genre['Key']), title=genre['Value']))
    return oc

####################################################################################################
def GenreSubMenu(title, genre):
    oc = ObjectContainer(title2=title)
    
    oc.add(DirectoryObject(key=Callback(VideosSubMenu, title=title, genre=genre), title="Videos"))
    oc.add(DirectoryObject(key=Callback(ArtistsSubMenu, title=title, genre=genre), title="Artists"))
    
    return oc

####################################################################################################
def VideoListing(title, group='video', request=None, genres=None, offset=0):
    if offset != 0:
        oc = ObjectContainer(title2=title, replace_parent=True)
        oc.add(DirectoryObject(key=Callback(VideoListing, title=title, request=request, genres=genres, offset=(offset-20)), title="Previous"))
    else:
        oc = ObjectContainer(title2=title)
    results = API_Call(group, request, genres, offset)['result']
    for result in results:
        video_title = result['title']
        thumb = result['image_url']
        duration = int(result['duration_in_seconds'])*1000
        artists = result['artists_main']
        featured_artists = result['artists_featured']
        url = VIDEO_URL % (result['artists_main'][0]['url_safename'], result['url_safe_title'], result['isrc'])
        summary = ''
        if len(artists) == 1:
            summary = 'Artist: %s' % artists[0]['name']
        elif len(artists) > 1:
            summary = 'Artists: '
            for artist in artists:
                summary = summary + artist['name'] + ', '
            summary = summary.strip(', ')
        else:
            pass
        if len(featured_artists) > 0:
            summary = summary + '\nFeaturing: '
            for featured in featured_artists:
                summary = summary + featured['name'] + ', '
            summary = summary.strip(', ')
        oc.add(VideoClipObject(url=url, title=video_title, summary=summary, duration=duration,
            thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))
    oc.add(DirectoryObject(key=Callback(VideoListing, title=title, request=request, genres=genres, offset=(offset+20)), title="More"))
    if len(oc) == 0:
        return ObjectContainer(header=NAME, message="No entries found.")
    return oc

####################################################################################################
def ArtistListing(title, group='artist', request=None, genres=None, offset=0):
    if offset != 0:
        oc = ObjectContainer(title2=title, replace_parent=True)
        oc.add(DirectoryObject(key=Callback(ArtistListing, title=title, request=request, genres=genres, offset=(offset-20)), title="Previous"))
    else:
        oc = ObjectContainer(title2=title)
    results = API_Call(group, request, genres, offset)['result']
    for artist in results:
        name = artist['name']
        thumb = artist['image_url']
        oc.add(DirectoryObject(key=Callback(ArtistVideoListing, name=name, urlsafe_name=artist['url_safename']), title=name))
    oc.add(DirectoryObject(key=Callback(ArtistListing, title=title, request=request, genres=genres, offset=(offset+20)), title="More"))
    if len(oc) == 0:
        return ObjectContainer(header=NAME, message="No entries found.")
    return oc

####################################################################################################
def ArtistVideoListing(name, urlsafe_name):
    oc = ObjectContainer(title2=name)
    videos = JSON.ObjectFromURL(ARTIST_VIDEOS_URL % urlsafe_name)['Videos']
    for video in videos:
        title = video['title']
        thumb = video['img']
        url = VEVO_URL + video['url']
        oc.add(VideoClipObject(url=url, title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))
    if len(oc) == 0:
        return ObjectContainer(header=NAME, message="No entries found.")
    return oc
    
####################################################################################################
def API_Call(group=None, request=None, genres=None, offset=None):
    params = ''
    if request:
        params = BuildParams(params, "order=%s" % request)
    if offset:
        params = BuildParams(params, "offset=%s" % offset)
    if group != 'genre':
        params = BuildParams(params, "max=%s" % '25')
    if genres:
        params = BuildParams(params, "genres=%s" % genres)
        
    url = (VEVO_API_URL % group) + params
    return JSON.ObjectFromURL(url) 

####################################################################################################
def BuildParams(params, new_param):
    if not params.startswith('?'):
        params = '?' + params
    if params[-1] != '?':
        params = params + '&'
    return (params + new_param)