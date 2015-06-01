__author__ = 'chijun'

try:
    from nodeobj.v1.dev import ContentParser
    from nodeobj.v1.dev.plugin.base import ExtensionNode
except:
    from dev import ContentParser
    from dev.plugin.base import ExtensionNode


__all__ = ['Package']


class Package(ContentParser):
    NODE_CLASS = ExtensionNode
    FORMAT = [{'node': 'pack_name',
               'regex': ['^([-_a-z0-9A-Z.]{1,}).*'],
               'subs': [
                    {'node': 'ver',
                     'regex': ['^.*=([.0-9]+).*'],
                    },
                    {'node': 'commit',
                     'regex': ['^[^#].*#(.*)'],
                    },
              ]}
    ]

    def scan(self):
        return self.fp.read()

    def readfp(self, fp):
        self.filename = fp.name
        self.fp = fp
        return self.run()

    def read(self, filename):
        self.filename = filename
        self.fp = open(filename, 'r')
        return self.run()
