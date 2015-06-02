__author__ = 'chijun'

import commands

from . import ContentParser
from . import ExtensionNode

__all__ = ['ConfigParser']


class ConfigParser(ContentParser):
    """Simple config parser, only support with-value and note-line"""
    NODE_CLASS = ExtensionNode
    FORMAT = [{'node': 'section',
               'regex': ['\[(.*)\]'],
               'subs': [
                   {'node': 'option',
                    'regex': ['([^:=\s]+).*='],
                    'subs': [
                       {'node': 'value',
                        'regex': ['[^=\s]+.*=(.*)',
                                  '^([^#][^=]+)$'],
                        }
                    ]
                    },
                   {'node': 'opt_commit',
                    'regex': ['(#.*)'],
                    },
               ]
               },
              {'node': 'sect_commit',
               'regex': ['(#.*)'],
               }]

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

    def write(self, config):
        lines = []
        if isinstance(config.sect_commit, list):
            for note in config.sect_commit:
                lines.append(note + '\n')
            lines.append('\n\n')
        if isinstance(config.section, dict):
            for sect, content in config.section.items():
                lines.append('[' + sect + ']' + '\n')
                if isinstance(content.option, dict):
                    for opt, val in content.option.items():
                        lines.append('{0} = {1}\n'.format(opt, val.value[0]))
                if isinstance(content.opt_commit, list):
                    for nt in content.opt_commit:
                        lines.append(nt + '\n')
                lines.append('\n\n')
        with open(self.filename, 'w') as f:
            f.writelines(lines)
