Application
===========

Bootstrap
---------

Djaio wraps ``aiohttp`` app with some useful things. Here we will create our own Djaio app.
First, let's create a management script in the root of our working directory::

    $ mkdir my-djaio-app
    $ cd my-djaio-app
    $ touch manage.py

Place following lines into the newly created ``manage.py``::

    #!/usr/bin/env python3
    from djaio import Djaio

    djaio = Djaio()

    if __name__ == '__main__':
        djaio.run()

Save file and make it executable::

    $ chmod +x manage.py

Let's run it::

    $ ./manage.py
    Settings module not found. Using the default one.
    ============================================================
    Usage: manage.py <command> <options>
    Available commands:
     * help - shows this message
     * runserver host:port - runs web server
    ============================================================

Management file is the common entrypoint for our application. It supports custom CLI commands that will be
described in further chapters. For now our app has neither routing nor handlers, so server won't respond
HTTP requests. Let's create a real application. Our project structure will be like this::

    my-djaio-app /
        app /
            api /
                __init__.py
                views.py
                urls.py
            __init__.py
            settings.py
        manage.py

We need to customize Djaio initialization. ``Djaio()`` constructor receives optional argument ``custom_init``
which must be callable. After creating ``aiohttp`` app, it is passed to ``custom_init`` as an argument.
``custom_init`` callable must return updated ``app`` object. Here is a good place to initialize our
custom libraries and plugins. For example let's configure logging:

app/__init__.py::

    from djaio.core import logs


    def init_app(app):
        logs.setup(app)
        return app

Update manage.py::

    import os
    from djaio import Djaio
    from app import init_app

    djaio = Djaio(custom_init=init_app)

    if __name__ == '__main__':
        djaio.run()

Now our app uses ``logging``.

Settings
--------

Djaio apps support declarative settings. Settings is a simple Python module with
constants defined. By default Djaio is looking for settings in ``app.settings`` module.
You can specify another location via environment variable ``SETTINGS``. Example::

    export SETTINGS='app.settings.local' ./manage.py <command>

Constants specified in project settings module override default ones.
Add the following lines to ``app/settings.py``::

    DEBUG = True
    INSTALLED_APPS = ['app.api']

Here we set debug mode on and add ``app/api`` module as one of installed apps, like in Django.
Djaio will try to locate ``urls`` module and add routes to aiohttp app.

