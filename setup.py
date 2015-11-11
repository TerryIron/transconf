__author__ = 'chijun'

from setuptools import setup
from transconf.__init__ import __version__

version = '.'.join(map(str, __version__))

setup(
    name="TransConf",
    version=version,
    description="A framework based on Twisted, AMQP, SqlAlChemy etc",
    long_description=__doc__,
    author="Chi Jun",
    packages=[
        'transconf',
        'transconf.tests',
        'transconf.common',
        'transconf.server',
        'transconf.server.twisted',
        'transconf.server.twisted.models',
        'transconf.msg',
        'transconf.msg.rabbit',
        'transconf.backend',
        'transconf.cmd',
    ],
    include_package_data=True,
    install_requires=[
        'twisted>=14.0',
        'pika>=0.9.14',
        'SQLAlchemy>=0.7.8,!=0.9.5,<=0.9.99',
        'PasteDeploy>=1.5.2',
        'PasteScript>=1.7.5',
        'Mako>=0.5.0',
        'Tempita>=0.5.1',
    ],

    extras_require={
        'genshi': ['Genshi>=0.6'],
        'jinja2': ['Jinja2'],
    },
    entry_points="""
        [paste.paster_command]
        controller = transconf.commands:ControllerCommand
        restcontroller = transconf.commands:RestControllerCommand
        routes = transconf.commands:RoutesCommand
        shell = transconf.commands:ShellCommand

        [paste.paster_create_template]
        transconf = transconf.installer:TransconfTemplate
        transconf_minimal = transconf.installer:MinimalTransconfTemplate

        [paste.filter_factory]
        debugger = transconf.middleware:debugger_filter_factory

        [paste.filter_app_factory]
        debugger = transconf.middleware:debugger_filter_app_factory
    """
)
