__author__ = 'chijun'

from common.model import BaseModel
from struct import NodeStructV1


class Model(BaseModel):
    STRUCT = NodeStructV1()

    def __init__(self, db_engine=None):
        super(Model, self).__init__(db_engine)

    def init(self, config):
        raise NotImplementedError()
