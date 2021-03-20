# -*- coding: utf-8 -*-
# https://github.com/Kodi-vStream/venom-xbmc-addons
#
from resources.lib.config import GestionCookie
from resources.hosters.hoster import iHoster
from resources.lib.comaddon import dialog, VSlog, addon
from resources.lib.handler.premiumHandler import cPremiumHandler
from resources.lib.parser import cParser
from resources.lib.util import QuoteSafe
import json, re

class cHoster(iHoster):

    def __init__(self):
        self.__sDisplayName = 'Uptobox'
        self.__sFileName = self.__sDisplayName
        self.oPremiumHandler = None

    def getDisplayName(self):
        return self.__sDisplayName

    def setDisplayName(self, sDisplayName):
        self.__sDisplayName = sDisplayName + ' [COLOR violet]' + self.__sDisplayName + '[/COLOR]'

    def setFileName(self, sFileName):
        self.__sFileName = sFileName

    def getFileName(self):
        return self.__sFileName

    def getPluginIdentifier(self):
        return 'uptobox'

    def isDownloadable(self):
        return True

    def getPattern(self):
        return ''

    def setUrl(self, sUrl):
        self.__sUrl = str(sUrl)
        self.__sUrl = self.__sUrl.replace('iframe/', '')
        self.__sUrl = self.__sUrl.replace('http:', 'https:')

    def checkSubtitle(self, sHtmlContent):
        oParser = cParser()

        # On ne charge les sous titres uniquement si vostfr se trouve dans le titre.
        # if not re.search("<h1 class='file-title'>[^<>]+(?:TRUEFRENCH|FRENCH)[^<>]*</h1>", sHtmlContent, re.IGNORECASE):
        if "<track type='vtt'" in sHtmlContent:

            sPattern = '<track type=[\'"].+?[\'"] kind=[\'"]subtitles[\'"] src=[\'"]([^\'"]+).vtt[\'"] srclang=[\'"].+?[\'"] label=[\'"]([^\'"]+)[\'"]>'
            aResult = oParser.parse(sHtmlContent, sPattern)

            if (aResult[0] == True):
                Files = []
                for aEntry in aResult[1]:
                    url = aEntry[0]
                    label = aEntry[1]
                    url = url + '.srt'

                    if not url.startswith('http'):
                        url = 'http:' + url
                    if 'Forc' not in label:
                        Files.append(url)
                return Files

        return False

    def checkUrl(self, sUrl):
        return True

    def getUrl(self):
        return self.__sUrl

    def getMediaLink(self):
        self.oPremiumHandler = cPremiumHandler(self.getPluginIdentifier())
        if (self.oPremiumHandler.isPremiumModeAvailable()):
            ADDON = addon()

            try:
                mDefault = int(ADDON.getSetting("hoster_uptobox_mode_default"))
            except AttributeError:
                mDefault = 0

            if mDefault == 0:
                ret = dialog().VSselect(['Passer en Streaming (via Uptostream)', 'Rester en direct (via Uptobox)'], 'Choissisez votre mode de fonctionnement')
            else:
                # 0 is ask me, so 1 is uptostream and so on...
                ret = mDefault - 1

            # mode stream
            if ret == 0:
                return self.__getMediaLinkForGuest()
            # mode DL
            if ret == 1:
                return self.__getMediaLinkByPremiumUser()
            
            return False

        else:
            VSlog('UPTOBOX - no premium')
            return self.__getMediaLinkForGuest()

    def __getMediaLinkForGuest(self):
        cookies = GestionCookie().Readcookie("uptobox")
        import requests, re

        s = requests.Session()
        s.headers.update({"Cookie": cookies})

        r = s.get('https://uptobox.com/api/streaming?file_code=' + self.__sUrl.split('/')[3]).json()

        r1 = s.get(r["data"]["user_url"]).text
        tok = re.search('token.+?;.+?;(.+?)&', r1).group(1)

        r1 = s.post("https://uptobox.com/api/user/pin/validate?token=" + tok,json={"pin":r["data"]["pin"]}).json()
        s.headers.update({"Referer": "https://uptobox.com/pin?pin=" + r["data"]["pin"]})

        r = s.get(r["data"]["check_url"]).json()["data"]["streamLinks"]

        sPattern = "'(.+?)': {(.+?)}"

        oParser = cParser()
        aResult = oParser.parse(r, sPattern)

        from resources.lib.comaddon import dialog

        url = []
        qua = []
        api_call = False

        for aEntry in aResult[1]:
            QUAL = aEntry[0]
            d = re.findall("'(.+?)': '(.+?)'",aEntry[1])
            for aEntry1 in d:
                VSlog(aEntry1)
                url.append(aEntry1[1])
                qua.append(QUAL  + ' (' + aEntry1[0] + ')')

        # Affichage du tableau
        api_call = dialog().VSselectqual(qua, url)

        if (api_call):
             return True, api_call

        return False, False

    def __getMediaLinkByPremiumUser(self):

        if not self.oPremiumHandler.Authentificate():
            return self.__getMediaLinkForGuest()

        else:
            sHtmlContent = self.oPremiumHandler.GetHtml(self.__sUrl)
            # compte gratuit ou erreur auth
            if 'you can wait' in sHtmlContent or 'time-remaining' in sHtmlContent:
                VSlog('no premium')
                return self.__getMediaLinkForGuest()
            else:
                SubTitle = self.checkSubtitle(sHtmlContent)
                api_call = self.GetMedialinkDL(sHtmlContent)
                if api_call:
                    if SubTitle:
                        return True, api_call, SubTitle
                    else:
                        return True, api_call

                return False, False

    def GetMedialinkDL(self, sHtmlContent):

        oParser = cParser()

        sPattern = '<a href *=[\'"](?!http:\/\/uptostream.+)([^<>]+?)[\'"] *class=\'big-button-green-flat mt-4 mb-4\''
        aResult = oParser.parse(sHtmlContent, sPattern)

        if (aResult[0]):
            return QuoteSafe(aResult[1][0])

        return False

