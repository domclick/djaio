import json
from aiohttp import web
from aiohttp_jinja2 import get_env


class Webpack(object):

    def __init__(self, app):
        self.app = app
        env = get_env(app)

        if env is None:
            text = ("Template engine is not initialized, "
                    "call aiohttp_jinja2.setup(...) first"
                    "")
            # in order to see meaningful exception message both: on console
            # output and rendered page we add same message to *reason* and
            # *text* arguments.
            raise web.HTTPInternalServerError(reason=text, text=text)

        self._set_asset_paths(app)

        # We only want to refresh the webpack stats in development mode,
        # not everyone sets this setting, so let's assume it's production.
        if app.settings.DEBUG:
            app.on_response_prepare.append(self._refresh_webpack_stats)

        env.globals['asset_url_for'] = self.asset_url_for

    def _set_asset_paths(self, app):
        """
        Read in the manifest json file which acts as a manifest for assets.
        This allows us to get the asset path as well as hashed names.

        :param app: aiohttp application
        :return: None
        """
        webpack_stats = app.settings.WEBPACK_MANIFEST_PATH

        try:
            with open(webpack_stats, 'r') as stats_json:
                stats = json.load(stats_json)
                if app.settings.WEBPACK_ASSETS_URL:
                    self.assets_url = app.settings.WEBPACK_ASSETS_URL
                else:
                    self.assets_url = stats['publicPath']

                self.assets = stats['assets']
        except IOError:
            raise RuntimeError(
                "'WEBPACK_MANIFEST_PATH' is required to be set and "
                "it must point to a valid json file.")

    async def _refresh_webpack_stats(self, *args):
        """
        Refresh the webpack stats so we get the latest version. It's a good
        idea to only use this in development mode.

        :return: None
        """
        self._set_asset_paths(self.app)

    def asset_url_for(self, asset):
        """
        Lookup the hashed asset path of a file name unless it starts with
        something that resembles a web address, then take it as is.

        :param asset: A logical path to an asset
        :type asset: str
        :return: Asset path or None if not found
        """
        if '//' in asset:
            return asset

        for key in self.assets:
            if key == asset:
                return '{0}{1}'.format(self.assets_url, self.assets[key])

        return None


def setup(app):
    app.webpack = Webpack(app)
