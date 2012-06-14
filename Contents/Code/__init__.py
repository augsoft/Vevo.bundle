# VEVO
VEVO_TITLE_INFO             = 'http://videoplayer.vevo.com/VideoService/AuthenticateVideo?isrc=%s&authToken=%s&domain=http://www.vevo.com'
VEVO_API_URL                = 'http://api.vevo.com/mobile/v1/%s/list.jsonp'
VEVO_SEARCH_URL             = 'http://api.vevo.com/mobile/v1/lookahead.json?q=%s&fullItems=true&newSearch=yes'
VIDEO_URL                   = 'http://www.vevo.com/watch/%s/%s/%s'

# BrightCove
BC_PLAYER_ID               = 105891355001
BC_PUBLISHER_ID            = 62009797001
BC_PLAYER                  = 'http://x.brightcove.com/plex/video.php?publisherId=%d&playerId=%d&videoId=%%d' % (BC_PUBLISHER_ID, BC_PLAYER_ID)

VIDEO_PREFIX = "/video/vevo"
NAME = 'Vevo'
ART  = 'art-default.jpg'
ICON = 'icon-default.png'
SEARCHICON = 'search.png'

FEEDBASE = "http://www.vevo.com"

MRSS  = {'media':'http://search.yahoo.com/mrss/'}
RTE   = {'rte':'http://www.rte.ie/schemas/vod'}

CACHE_TIME = 3600

authToken = str(uuid3(NAMESPACE_URL,"http://vevo.com"))
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
    #dir.Append(Function(InputDirectoryItem(RSS_Search_parser,"Search...","Search", art=R(ART), thumb=R("search.png")),pageurl = FEEDBASE + "/search?q="))

    return oc

####################################################################################################
def VideosSubMenu(title=None, genre=None):
    if title:
        oc = ObjectContainer(title1="Videos", title2=title)
    else:
        oc = ObjectContainer(title2="Videos")

    oc.add(DirectoryObject(key=Callback(API_List, title="Most Recent", group="video", request="MostRecent", genre=genre), title="Most Recent")))
    oc.add(DirectoryObject(key=Callback(API_List, title="Most Viewed today", group="video", request="MostViewedToday", genre=genre), title="Most Viewed today")))
    oc.add(DirectoryObject(key=Callback(API_List, title="Most Viewed this week", group="video", request="MostViewedThisWeek", genre=genre), title="Most Viewed this week")))
    oc.add(DirectoryObject(key=Callback(API_List, title="Most Viewed this month", group="video", request="MostViewedThisMonth", genre=genre), title="Most Viewed this month")))
    oc.add(DirectoryObject(key=Callback(API_List, title="Most Viewed of All Time", group="video", request="MostViewedAllTime", genre=genre), title="Most Viewed of All Time")))
    
    return oc

####################################################################################################
def ArtistsSubMenu(title=None, genre=None):
    if title:
        oc = ObjectContainer(title1="Videos", title2=title)
    else:
        oc = ObjectContainer(title2="Videos")

    oc.add(DirectoryObject(key=Callback(API_List, title="Most Recent", group="artist", request="MostRecent", genre=genre), title="Most Recent")))
    oc.add(DirectoryObject(key=Callback(API_List, title="Most Viewed today", group="artist", request="MostViewedToday", genre=genre), title="Most Viewed today")))
    oc.add(DirectoryObject(key=Callback(API_List, title="Most Viewed this week", group="artist", request="MostViewedThisWeek", genre=genre), title="Most Viewed this week")))
    oc.add(DirectoryObject(key=Callback(API_List, title="Most Viewed this month", group="artist", request="MostViewedThisMonth", genre=genre), title="Most Viewed this month")))
    oc.add(DirectoryObject(key=Callback(API_List, title="Most Viewed of All Time", group="artist", request="MostViewedAllTime", genre=genre), title="Most Viewed of All Time")))
    
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
def VideoListing(title, group=None, request=None, genres=None, offset=None):
    oc = ObjectContainer(title2=title)
    results = API_Call(group, request, genres, offset)['result']
    for result in results:
        title = result['title']
        thumb = result['image_url']
        duration = int(result['duration_in_seconds'])*1000
        artists = result['artists_main']
        featured_artists = result['artists_featured']
        url = VIDEO_URL % (result['artists_main'][0]['url_safename'], result['url_safe_title'], result['isrc'])
        summary = ''
        if len(artists) == 1:
            summary = 'Artist: %s' % artist['name']
        elif len(artists) > 1:
            summary = 'Artists: '
            for artist in artists:
                summary = summary + artist['name'] + ', '
            summary = summary.strip(', ')
        else:
            pass
    return oc

####################################################################################################
def ArtistListing(title, group=None, request=None, genres=None, offset=None):
    oc = ObjectContainer(title2=title)
    results = API_Call(group, request, genres, offset)
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
    if params[0] != '?':
        params = '?' + params
    if params[-1] != '?':
        params = params + '&'
    return (params + new_param)