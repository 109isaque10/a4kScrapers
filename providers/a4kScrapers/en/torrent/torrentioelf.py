# -*- coding: utf-8 -*-

from providerModules.a4kScrapers import core

class sources(core.DefaultSources):
    def __init__(self, *args, **kwargs):
        super(sources, self).__init__(__name__, *args, single_query=True, **kwargs)
        self._filter = core.Filter(fn=self._filter_fn, type='single')

    def _filter_fn(self, title, clean_title):
        if self.is_movie_query():
            return False

        if self.scraper.filter_single_episode.fn(title, clean_title):
            self._filter.type = self.scraper.filter_single_episode.type
            return True

        if self.scraper.filter_show_pack.fn(title, clean_title):
            self._filter.type = self.scraper.filter_show_pack.type
            return True

        if self.scraper.filter_season_pack.fn(title, clean_title):
            self._filter.type = self.scraper.filter_season_pack.type
            return True

        return False

    def _get_scraper(self, title):
        return super(sources, self)._get_scraper(title, custom_filter=self._filter)

    def _search_request(self, url, query):
        query = self._imdb
        if not self.is_movie_query():
            query += '&season=' + self.scraper.season_x

        params = '&apikey=36uoqvh24k5gc0ljvk8y7hagngnkeql4' 

        request_url = url.base + '/' + core.quote_plus(params) + (url.search % core.quote_plus(query))
        response = self._request.get(request_url)

        if response.status_code != 200:
            return []

        try:
            results = bs(response.text, 'html5lib')
            rows = results('item')
        except Exception as e:
            self._request.exc_msg = 'Failed to parse json: %s' % response.text
            return []

        if not rows:
            return []
        else:
            return rows

    def _soup_filter(self, response):
        return response

    def _info(self, el, url, torrent):
        if 'infoHash' in el:
            torrent['hash'] = el['infoHash']
        if 'link' in el:
            torrent['url'] = el['url']

        torrent['size'] = core.source_utils.de_string_size(self.genericScraper.parse_size(el['title']))
        torrent['seeds'] = self.genericScraper.parse_seeds(el['title'])
        if '\n' in torrent['release_title']:
            #torrent['release_title'] = torrent['release_title'].split('\n👤', 1)[0]
            torrent['release_title'] = torrent['release_title'].split('\n💾', 1)[0]
        if '\n' in torrent['release_title']:
            torrent['release_title'] = torrent['release_title'].split('\n', 1)[1]

        return torrent

    def movie(self, title, year, imdb=None, **kwargs):
        self._imdb = imdb
        return super(sources, self).movie(title, year, imdb, auto_query=False)

    def episode(self, simple_info, all_info, **kwargs):
        self._imdb = all_info.get('info', {}).get('tvshow.imdb_id', None)
        if self._imdb is None:
            self._imdb = all_info.get('showInfo', {}).get('ids', {}).get('imdb', None)
        return super(sources, self).episode(simple_info, all_info)
