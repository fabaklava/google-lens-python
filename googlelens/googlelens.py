import re
import json

from requests import Session
from bs4 import BeautifulSoup


class GoogleLens:
    def __init__(self):
        self.url = "https://lens.google.com"
        self.session = Session()
        self.session.headers.update(
            {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'}
        )

    def __parse_prerender_script(self, prerender_script):
        data = {
            "match": None,
            "similar": []
        }

        try:
            if prerender_script and prerender_script[0]:
                data["match"] = {
                    "title": prerender_script[0][1][8][12][0][0][0],
                    "thumbnail": prerender_script[0][1][8][12][0][2][0][0],
                    "pageURL": prerender_script[0][1][8][12][0][2][0][4]
                }
        except (IndexError, KeyError):
            pass

        if data["match"] is not None:
            try:
                visual_matches = prerender_script[1][1][8][8][0][12]
            except (IndexError, KeyError):
                return data
        else:
            try:
                visual_matches = prerender_script[0][1][8][8][0][12]
            except (IndexError, KeyError):
                return data

        for match in visual_matches:
            try:
                title = match[3]
                thumbnail = match[0][0]
                pageURL = match[5]
                sourceWebsite = match[14]
                data["similar"].append({
                    "title": title,
                    "thumbnail": thumbnail,
                    "pageURL": pageURL,
                    "sourceWebsite": sourceWebsite
                })
            except (IndexError, KeyError):
                pass

        return data

    def search_by_file(self, file_path: str):
        multipart = {'encoded_image': (file_path, open(file_path, 'rb')), 'image_content': ''}
        response = self.session.post(self.url + "/upload", files=multipart, allow_redirects=False)
        search_url = BeautifulSoup(
            response.text,
            'html.parser').find('meta', {'http-equiv': 'refresh'}).get('content')
        search_url = re.sub("^.*URL='", '', search_url).replace("0; URL=", "")

        response = self.session.get(search_url)
        prerender_script = self.__get_prerender_script(response.text)

        return self.__parse_prerender_script(prerender_script)

    def search_by_url(self, url: str):
        response = self.session.get(self.url + "/uploadbyurl", params={"url": url}, allow_redirects=True)

        prerender_script = self.__get_prerender_script(response.text)

        return self.__parse_prerender_script(prerender_script)
