Views and Methods
=================

Djaio supports an idea that typical API can implement both REST and RPC paradigms.
For instance, some generic "Get object details" action can be represented as REST::

    /api/v1/object/<id>/

And there can be an RPC handler::

    import xmlrpclib

    proxy = xmlrpclib.ServerProxy("http://localhost:8000/rpc")
    proxy.getObjectDetails(<id>)

...that actually does the same - it returns some object's detail information. So RESTful handlers are
just wrappers for CRUDL methods. Djaio provides basic method and view classes for rapid API development.

.. WARNING::
   RPC interface is not implemented yet.


Methods
-------

Djaio's base method is an object that is able to receive input parameters, execute some action and return result.
Input parameters must be described with `Schematics model <http://schematics.readthedocs.io/>`_. Schematics
is installed automatically as Djaio's dependency.
*Input model* validation is executed during initialization. If model data is not valid, HTTP 400 error
is raised. If input is valid, action is executed and result is returned. Result is described with
*output model*.

Let' create some greeting method. It will receive name and return greeting. First we have to create `input model`.
Create ``app/api/models.py`` and add following lines there::

    from schematics import Model
    from schematics import types


    class GreetingInput(Model):
        name = types.StringType(default='')


    class GreetingOutput(Model):
        greeting = types.StringType(default='')

And ``app/api/methods.py``::

    from djaio.core.methods import BaseMethod


    class GreetingMethod(BaseMethod):

        async def execute(self):
            _name = self.params['name']
            return [{'greeting': 'Hello, {}!'.format(_name)}]

That's enough. Note that all we need is to implement ``execute()`` method. Validated input params are
available as ``self.params`` dict.


Views
-----

Djaio has few helper view classes and ``djaio.core.views.JsonView`` is one of them. Let's create ``app/api/views.py`` and
add some code there::

    from djaio.core.views import JsonView
    from .methods import GreetingMethod
    from .models import GreetingInput, GreetingOutput


    class GreetingView(JsonView):
        get_method = GreetingMethod(input_model=GreetingInput, output_model=GreetingOutput)

Pretty declarative, huh? We are almost done.

URLConf
-------

URLs in Djaio is a small wrap over ``aiohttp`` routes. They can be autodiscovered on application
bootstrap. Djaio searches ``urls`` module in every of ``INSTALLED_APPS`` modules.
Create ``app/api/urls.py`` with the following contents::

    from djaio.core.urlconf import url
    from app.api.views import GreetingView

    url('GET', '/api/greeting', GreetingView, name='greeting')

Ok, now we are ready to launch::

    $ ./manage.py runserver 0.0.0.0:8080
    ======== Running on http://0.0.0.0:8080/ ========
    (Press CTRL+C to quit)

Navigate your favourite browser to http://localhost:8080/api/greeting/?name=John and see::

    {
        "success": true,
        "result": [
            {
                "greeting": "Hello, John!"
            }
        ]
    }

