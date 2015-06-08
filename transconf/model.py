__author__ = 'chijun'

from common.model import BaseModel

class Model(BaseModel):
    def init(self, config):
        raise NotImplementedError()
