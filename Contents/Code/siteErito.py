import PAsearchSites
import PAgenres

def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchSiteID):
    if searchSiteID != 9999:
        siteNum = searchSiteID
    sceneID = encodedTitle.split('%20', 1)[0]
    Log("SceneID: " + sceneID)
    try:
        sceneTitle = encodedTitle.split('%20', 1)[1].replace('%20',' ')
    except:
        sceneTitle = ''
    Log("Scene Title: " + sceneTitle)
    url = PAsearchSites.getSearchSearchURL(siteNum) + sceneID + "/1"
    searchResults = HTML.ElementFromURL(url)
    for searchResult in searchResults.xpath('//div[@class="wxt7nk-0 JqBNK"]//div[1]/h1'):
        titleNoFormatting = searchResult.xpath('//div[1]/h1')[0].text_content().replace('Trailer','').strip()
        curID = url.replace('/','_').replace('?','!')
        if sceneTitle:
            score = 100 - Util.LevenshteinDistance(sceneTitle.lower(), titleNoFormatting.lower())
        else:
            score = 90
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting + " [Erito] ", score = score, lang = lang))

    return results

def update(metadata,siteID,movieGenres,movieActors):
    Log('******UPDATE CALLED*******')

    url = str(metadata.id).split("|")[0].replace('_','/').replace('?','!')
    detailsPageElements = HTML.ElementFromURL(url)
    art = []
    metadata.collections.clear()
    movieGenres.clearGenres()
    movieActors.clearActors()

    # Studio
    metadata.studio = 'Erito'

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@class="wxt7nk-4 fSsARZ"]')[0].text_content().strip()

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//div[@class="tjb798-2 flgKJM"]/span[2]/div[2]')[0].text_content().strip()
    except:
        pass

    #Tagline and Collection(s)
    tagline = 'Erito'
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    genres = detailsPageElements.xpath('//div[@class="tjb798-2 flgKJM"]/span[1]/a')
    if len(genres) > 0:
        for genreLink in genres:
            genreName = genreLink.text_content().replace(',','').strip().lower()
            movieGenres.addGenre(genreName)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="tjb798-2 flgKJM"]/span[last()]')
    if len(date) > 0:
        date = date[0].text_content().strip().replace('Release Date:','')
        date_object = datetime.strptime(date, '%B %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    ### Posters and artwork ###

    # Video trailer background image
    try:
        twitterBG = detailsPageElements.xpath('//div[@class="tg5e7m-2 evtSOm"]/img')[0].get('src')
        art.append(twitterBG)
    except:
        pass

    j = 1
    Log("Artwork found: " + str(len(art)))
    for posterUrl in art:
        if not PAsearchSites.posterAlreadyExists(posterUrl,metadata):
            #Download image file for analysis
            try:
                img_file = urllib.urlopen(posterUrl)
                im = StringIO(img_file.read())
                resized_image = Image.open(im)
                width, height = resized_image.size
                #Add the image proxy items to the collection
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
                j = j + 1
            except:
                pass

    return metadata
