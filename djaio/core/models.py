# -*- coding: utf-8 -*-
from schematics import Model as SchematicsModel


class Model(SchematicsModel):

    # TODO: A good place to implement mapping to DB
    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)

