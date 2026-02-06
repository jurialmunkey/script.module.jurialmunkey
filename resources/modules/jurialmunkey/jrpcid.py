# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from xbmcgui import ListItem
from jurialmunkey.jsnrpc import get_jsonrpc
from jurialmunkey.litems import ContainerDirectory, INFOLABEL_MAP
from jurialmunkey.ftools import cached_property
from infotagger.listitem import ListItemInfoTag


JSON_RPC_LOOKUPS = {
    'addonid': {
        'method': "Addons.GetAddonDetails",
        'properties': [
            "name", "version", "summary", "description", "path", "author", "thumbnail", "disclaimer", "fanart",
            "dependencies", "broken", "extrainfo", "rating", "enabled", "installed", "deprecated"],
        'key': "addon",
    },
    'setid': {
        'method': "VideoLibrary.GetMovieSetDetails",
        'properties': [
            "title", "plot", "playcount",
            "fanart", "thumbnail", "art"],
        'key': "setdetails",
    },
    'movieid': {
        'method': "VideoLibrary.GetMovieDetails",
        'properties': [
            "file", "title", "plot", "playcount", "year", "trailer", "tagline", "originaltitle", "mpaa", "runtime", "set", "setid", "lastplayed", "premiered", "dateadded", "userrating", "rating", "votes", "top250",
            "genre", "director", "writer", "studio", "cast", "country",
            "fanart", "thumbnail", "art", "ratings", "uniqueid", "streamdetails"],
        'key': "moviedetails",
    },
    'tvshowid': {
        'method': "VideoLibrary.GetTVShowDetails",
        'properties': [
            "file", "title", "plot", "playcount", "year", "lastplayed", "premiered", "originaltitle", "watchedepisodes", "dateadded", "userrating", "rating", "votes", "mpaa", "season", "episode",
            "genre", "studio", "cast",
            "fanart", "thumbnail", "art", "ratings", "uniqueid"],
        'key': "tvshowdetails",
    },
    'seasonid': {
        'method': "VideoLibrary.GetSeasonDetails",
        'properties': [
            "title", "showtitle", "playcount", "watchedepisodes", "season", "episode",
            "tvshowid",
            "fanart", "thumbnail", "art"],
        'key': "seasondetails",
    },
    'episodeid': {
        'method': "VideoLibrary.GetEpisodeDetails",
        'properties': [
            "file", "showtitle", "title", "plot", "playcount", "firstaired", "runtime", "productioncode", "lastplayed", "dateadded", "season", "episode", "originaltitle", "userrating", "rating", "votes",
            "tvshowid", "seasonid",
            "writer", "director", "cast",
            "fanart", "thumbnail", "art", "ratings", "uniqueid", "streamdetails"],
        'key': "episodedetails",
    },
}


class ListItemMakerBase():

    library = None

    @cached_property
    def sublookups(self):
        return []

    @cached_property
    def listitem(self):
        return ListItem(label=self.label, label2=self.label2, path=self.path, offscreen=True)

    @cached_property
    def info_tag(self):
        return ListItemInfoTag(self.listitem, self.library)

    @cached_property
    def base_collector(self):
        return {}

    label2 = ''

    @cached_property
    def label(self):
        return self.meta.get('label') or ''

    @cached_property
    def artwork(self):
        artwork = self.meta.get('art') or {}
        artwork.setdefault('fanart', self.meta.get('fanart', ''))
        artwork.setdefault('thumb', self.meta.get('thumbnail', ''))
        return artwork

    @cached_property
    def path(self):
        return self.get_path()

    def get_path(self):
        return ''

    @staticmethod
    def format_key_value(k, v):
        if isinstance(v, float):
            return (
                (f'{k}', f'{v}', ),
                (f'{k}_integer', f'{int(v)}'),
                (f'{k}_percentage', f'{v / 10:.0%}'),  # Ratings stored out of 10
                (f'{k}_rounded', f'{v:.1f}'),
                (f'{k}_rounded_2dp', f'{v:.2f}'),
            )
        return ((k, f'{v}', ), )

    def iter_dict(self, d, prefix='', sub_lookups=False):
        ip = {}
        for k, v in d.items():

            if isinstance(v, dict):
                ip.update(self.iter_dict(v, prefix=f'{prefix}{k}.', sub_lookups=sub_lookups))
                continue

            if isinstance(v, list):
                ip[f'{prefix}{k}.count'] = f'{len(v)}'
                collector = {}

                for x, j in enumerate(v):
                    if isinstance(j, dict):
                        ip.update(self.iter_dict(j, prefix=f'{prefix}{k}.{x}.', sub_lookups=sub_lookups))
                        continue

                    for key, value in self.format_key_value(k, j):
                        ip[f'{prefix}{key}.{x}'] = f'{value}'
                        collector.setdefault(f'{prefix}{key}', set()).add(f'{value}')
                        self.base_collector.setdefault(f'{key}', set()).add(f'{value}')

                for key, value in collector.items():
                    ip[f'{key}.collection'] = ' / '.join(sorted(value))
                    ip[f'{key}.collection.count'] = f'{len(value)}'

                continue

            for key, value in self.format_key_value(k, v):
                ip[f'{prefix}{key}'] = f'{value}'
                self.base_collector.setdefault(f'{key}', set()).add(f'{value}')

            if not sub_lookups or k not in sub_lookups or k not in JSON_RPC_LOOKUPS:
                continue

            try:
                lookup = JSON_RPC_LOOKUPS[k]
                method = lookup['method']
                params = {k: int(v), "properties": lookup['properties']}
                response = get_jsonrpc(method, params)
                item = response['result'][lookup['key']] or {}
                ip.update(self.iter_dict(item, prefix=f'{prefix}item.'))
            except (KeyError, AttributeError):
                pass

        return ip

    @cached_property
    def infoproperties(self):
        return self.get_infoproperties()

    def get_infoproperties(self):
        infoproperties = {}
        infoproperties.update(self.iter_dict(self.meta, sub_lookups=self.sublookups))
        infoproperties['isfolder'] = 'true'

        for key, value in self.base_collector.items():
            infoproperties[f'{key}.collection'] = ' / '.join(sorted(value))
            infoproperties[f'{key}.collection.count'] = f'{len(value)}'

        return infoproperties

    @cached_property
    def infolabels(self):
        return self.get_infolabels()

    def get_infolabels(self):
        return {}

    def make_item(self):
        if not self.meta:
            return
        self.listitem.setProperties(self.infoproperties)
        self.listitem.setArt(self.artwork)
        return self.listitem


class ListItemMakerVideo(ListItemMakerBase):
    def get_infolabels(self):
        infolabels = {}
        infolabels.update({INFOLABEL_MAP[k]: v for k, v in self.meta.items() if v and k in INFOLABEL_MAP and v != -1})
        infolabels['dbid'] = self.dbid
        infolabels['mediatype'] = self.dbtype
        return infolabels

    def make_item(self):
        if not self.meta:
            return
        self.info_tag.set_info(self.infolabels)
        self.info_tag.set_unique_ids(self.meta.get('uniqueid') or {})
        self.info_tag.set_stream_details(self.meta.get('streamdetails') or {})
        self.info_tag.set_cast(self.meta.get('cast') or [])
        self.listitem.setProperties(self.infoproperties)
        self.listitem.setArt(self.artwork)
        return self.listitem


class ListItemMakerMovie(ListItemMakerVideo):
    dbtype = 'movie'

    def get_path(self):
        return f'videodb://movies/titles/{self.dbid}'


class ListItemMakerSet(ListItemMakerVideo):
    dbtype = 'set'

    def get_path(self):
        return f'videodb://movies/sets/{self.dbid}/'


class ListItemMakerTvshow(ListItemMakerVideo):
    dbtype = 'tvshow'

    @cached_property
    def totalepisodes(self):
        return int(self.infolabels.get('episode') or 0)

    @cached_property
    def totalseasons(self):
        return int(self.infolabels.get('season') or 0)

    def get_path(self):
        return f'videodb://tvshows/titles/{self.dbid}/'

    def get_infoproperties(self):
        infoproperties = super().get_infoproperties()
        infoproperties['totalepisodes'] = self.totalepisodes
        infoproperties['unwatchedepisodes'] = self.totalepisodes - int(infoproperties.get('watchedepisodes') or 0)
        infoproperties['totalseasons'] = self.totalseasons
        return infoproperties


class ListItemMakerSeason(ListItemMakerVideo):
    dbtype = 'season'

    @cached_property
    def totalepisodes(self):
        return int(self.infolabels.get('episode') or 0)

    @cached_property
    def season(self):
        return self.meta.get("season")

    @cached_property
    def tvshow_dbid(self):
        return self.meta.get("tvshowid")

    def get_path(self):
        return f'videodb://tvshows/titles/{self.tvshow_dbid}/{self.season}/'

    def get_infoproperties(self):
        infoproperties = super().get_infoproperties()
        infoproperties['totalepisodes'] = self.totalepisodes
        infoproperties['unwatchedepisodes'] = self.totalepisodes - int(infoproperties.get('watchedepisodes') or 0)
        return infoproperties


class ListItemMakerEpisode(ListItemMakerVideo):
    dbtype = 'episode'

    @cached_property
    def season(self):
        return self.meta.get("season")

    @cached_property
    def tvshow_dbid(self):
        return self.meta.get("tvshowid")

    def get_path(self):
        return f'videodb://tvshows/titles/{self.tvshow_dbid}/{self.season}/{self.dbid}'


def ListItemMaker(meta, dbid, dbtype, library=None, sublookups=None):
    routes = {
        'movie': ListItemMakerMovie,
        'set': ListItemMakerSet,
        'tvshow': ListItemMakerTvshow,
        'season': ListItemMakerSeason,
        'episode': ListItemMakerEpisode,
    }
    try:
        route = routes[dbtype]()
    except KeyError:
        route = ListItemMakerBase()
    route.meta = meta
    route.dbid = dbid
    route.library = library
    route.sublookups = sublookups
    route.dbtype = dbtype
    return route


class ListGetItemDetails(ContainerDirectory):
    jrpc_method = ""
    jrpc_properties = []
    jrpc_id = ""
    jrpc_idtype = int
    jrpc_key = ""
    jrpc_sublookups = []
    item_dbtype = None
    item_library = None
    container_content = ''

    def get_items(self, dbid, **kwargs):
        def _get_items():
            method = self.jrpc_method
            params = {
                self.jrpc_id: self.jrpc_idtype(dbid),
                "properties": self.jrpc_properties
            }
            response = get_jsonrpc(method, params) or {}
            item = response.get('result', {}).get(self.jrpc_key)

            return [ListItemMaker(item, dbid, self.item_dbtype, self.item_library, self.jrpc_sublookups).make_item()]

        items = [
            (li.getPath(), li, li.getProperty('isfolder').lower() == 'true', )
            for li in _get_items() if li] if dbid else []

        return items

    def get_directory(self, dbid, **kwargs):
        items = self.get_items(dbid, **kwargs)
        self.add_items(items, container_content=self.container_content)


class ListGetAddonDetails(ListGetItemDetails):
    jrpc_method = JSON_RPC_LOOKUPS['addonid']['method']
    jrpc_properties = JSON_RPC_LOOKUPS['addonid']['properties']
    jrpc_key = JSON_RPC_LOOKUPS['addonid']['key']
    jrpc_id = "addonid"
    jrpc_idtype = str

    def get_directory(self, dbid, convert_path=False, **kwargs):
        if convert_path:
            if not dbid.startswith('plugin://'):
                return
            import re
            result = re.search('plugin://(.*)/', dbid)
            return result.group(1) if result else None

        items = self.get_items(dbid, **kwargs)
        self.add_items(items)


class ListGetMovieSetDetails(ListGetItemDetails):
    jrpc_method = JSON_RPC_LOOKUPS['setid']['method']
    jrpc_properties = JSON_RPC_LOOKUPS['setid']['properties']
    jrpc_key = JSON_RPC_LOOKUPS['setid']['key']
    jrpc_id = "setid"
    jrpc_sublookups = ["movieid"]
    item_dbtype = "set"
    item_library = "video"
    container_content = 'sets'


class ListGetMovieDetails(ListGetItemDetails):
    jrpc_method = JSON_RPC_LOOKUPS['movieid']['method']
    jrpc_properties = JSON_RPC_LOOKUPS['movieid']['properties']
    jrpc_key = JSON_RPC_LOOKUPS['movieid']['key']
    jrpc_id = "movieid"
    item_dbtype = "movie"
    item_library = "video"
    container_content = 'movies'


class ListGetTVShowDetails(ListGetItemDetails):
    jrpc_method = JSON_RPC_LOOKUPS['tvshowid']['method']
    jrpc_properties = JSON_RPC_LOOKUPS['tvshowid']['properties']
    jrpc_key = JSON_RPC_LOOKUPS['tvshowid']['key']
    jrpc_id = "tvshowid"
    item_dbtype = "tvshow"
    item_library = "video"
    container_content = 'tvshows'


class ListGetSeasonDetails(ListGetItemDetails):
    jrpc_method = JSON_RPC_LOOKUPS['seasonid']['method']
    jrpc_properties = JSON_RPC_LOOKUPS['seasonid']['properties']
    jrpc_key = JSON_RPC_LOOKUPS['seasonid']['key']
    jrpc_sublookups = ["tvshowid"]
    jrpc_id = "seasonid"
    item_dbtype = "season"
    item_library = "video"
    container_content = 'seasons'


class ListGetEpisodeDetails(ListGetItemDetails):
    jrpc_method = JSON_RPC_LOOKUPS['episodeid']['method']
    jrpc_properties = JSON_RPC_LOOKUPS['episodeid']['properties']
    jrpc_key = JSON_RPC_LOOKUPS['episodeid']['key']
    jrpc_sublookups = ["seasonid", "tvshowid"]
    jrpc_id = "episodeid"
    item_dbtype = "episode"
    item_library = "video"
    container_content = 'episodes'
