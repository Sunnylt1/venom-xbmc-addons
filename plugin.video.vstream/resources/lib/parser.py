# -*- coding: utf-8 -*-
# vStream https://github.com/Kodi-vStream/venom-xbmc-addons
from operator import itemgetter
import re

class cParser:

    def sorted_nicely(self, l, key):
        """ Sort the given iterable in the way that humans expect."""
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda item: [ convert(c) for c in re.split('([0-9]+)', key(item)) ]
        return sorted(l, key = alphanum_key)

    def parseSingleResult(self, sHtmlContent, sPattern):
        aMatches = re.compile(sPattern).findall(sHtmlContent)
        if (len(aMatches) == 1):
            aMatches[0] = self.__replaceSpecialCharacters(aMatches[0])
            return True, aMatches[0]
        return False, aMatches

    def __replaceSpecialCharacters(self, sString):
        """ /!\ pas les mêmes tirets, tiret moyen et cadratin."""
        return sString.replace('\r', '').replace('\n', '').replace('\t', '').replace('\\/', '/').replace('&amp;', '&')\
                      .replace('&#039;', "'").replace('&#8211;', '-').replace('&#8212;', '-').replace('&eacute;', 'é')\
                      .replace('&acirc;', 'â').replace('&ecirc;', 'ê').replace('&icirc;', 'î').replace('&ocirc;', 'ô')\
                      .replace('&hellip;', '...').replace('&quot;', '"').replace('&gt;', '>').replace('&egrave;', 'è')\
                      .replace('&ccedil;', 'ç').replace('&laquo;', '<<').replace('&raquo;', '>>').replace('\xc9', 'E')\
                      .replace('&ndash;', '-').replace('&ugrave;', 'ù').replace('&agrave;', 'à').replace('&lt;', '<')\
                      .replace('&rsquo;', "'").replace('&lsquo;', '\'').replace('&nbsp;', '').replace('&#8217;', "'")\
                      .replace('&#8230;', '...').replace('&#8242;', "'").replace('&#884;', '\'').replace('&#39;', '\'')\
                      .replace('&#038;', '&').replace('&iuml;', 'ï').replace('&#8220;', '"').replace('&#8221;', '"')\
                      .replace('–', '-').replace('—', '-')

    def parse(self, sHtmlContent, sPattern, iMinFoundValue=1):
        sHtmlContent = self.__replaceSpecialCharacters(str(sHtmlContent))
        aMatches = re.compile(sPattern, re.IGNORECASE).findall(sHtmlContent)

        #Source non compatible avec le tri :
        #- Celle qui utilise oGui.
        #- Celle qui se base sur l'ordre des tuple pour ajouter du texte (voir hds_fm).
        #- French-Stream lol a cause des valeurs random sur le site comme "ABCDE".
        try:
            if "episode" in str(aMatches) and not aMatches[0][1] == "" and not "ABCDE" in str(aMatches):
                if aMatches[1][0] and not "/" in str(aMatches[1][0]):
                    aMatches = self.sorted_nicely(aMatches, itemgetter(0))
                elif aMatches[1][1] and not "/" in str(aMatches[1][1]):
                    aMatches = self.sorted_nicely(aMatches, itemgetter(1))
                else:
                    aMatches = self.sorted_nicely(aMatches, itemgetter(2))                 
        except Exception as e:
            pass

        if (len(aMatches) >= iMinFoundValue):
            return True, aMatches
        return False, aMatches

    def replace(self, sPattern, sReplaceString, sValue):
        return re.sub(sPattern, sReplaceString, sValue)

    def escape(self, sValue):
        return re.escape(sValue)

    def getNumberFromString(self, sValue):
        sPattern = '\d+'
        aMatches = re.findall(sPattern, sValue)
        if (len(aMatches) > 0):
            return aMatches[0]
        return 0

    def titleParse(self, sHtmlContent, sPattern):
        sHtmlContent = self.__replaceSpecialCharacters(str(sHtmlContent))
        aMatches = re.compile(sPattern, re.IGNORECASE)
        try:
            [m.groupdict() for m in aMatches.finditer(sHtmlContent)]
            return m.groupdict()
        except:
            return {'title': sHtmlContent}

    def abParse(self, sHtmlContent, start, end=None, startoffset=0):
        # usage oParser.abParse(sHtmlContent, 'start', 'end')
        # startoffset (int) décale le début pour ne pas prendre en compte start dans le résultat final si besoin
        # la fin est recherchée forcement après le début
        # la recherche de fin n'est pas obligatoire
        # usage2 oParser.abParse(sHtmlContent, 'start', 'end', 6)
        # ex youtube.py
        
        startIdx = sHtmlContent.find(start)
        if startIdx == -1:  # rien trouvé, retourner le texte complet
            return sHtmlContent
        
        if end:
            endIdx = sHtmlContent[startoffset + startIdx:].find(end)
            if endIdx > 0:
                return sHtmlContent[startoffset + startIdx: startoffset + startIdx + endIdx]
        return sHtmlContent[startoffset + startIdx:]
