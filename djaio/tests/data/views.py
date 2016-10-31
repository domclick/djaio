from aiohttp import web
from djaio.core.methods import BaseMethod
from djaio.core.views import RemoteContextMixin, JsonView

from djaio.tests.data.methods import (TstGetMethod, TstPostMethod, TstPutMethod, TstDeleteMethod, TstGetMethodBasic,
                                    TstGetDetailMethod)
from djaio.tests.data.models import TstInput, TstOutput, TstPostInput, TstInputDetail


class TstDefaultView(RemoteContextMixin, web.View):

    get_method = BaseMethod(description='return the application test result')

    async def get(self):
        result = web.Response(
            body=str.encode('You shall not pass!'),
            content_type='text/plain'
        )
        return result


class TstInputViewBasic(JsonView):
    get_method = TstGetMethodBasic(input_model=TstInput, description="""Returns test data""")

class TstInputView(JsonView):
    get_method = TstGetMethod(output_model=TstOutput,
                                             description="""Returns test data""")

    post_method = TstPostMethod(input_model=TstPostInput, output_model=TstOutput,
                            description="""Creates test data""")


class TstInputDetailView(JsonView):
    get_method = TstGetDetailMethod(input_model=TstInputDetail, output_model=TstOutput,
                                             description="""Returns test data""")

    put_method = TstPutMethod(input_model=TstInput, output_model=TstOutput,
                               description="""Updates test data""")

    delete_method = TstDeleteMethod(input_model=TstInputDetail, description="""Deletes test data""")
