from setuptools import setup

setup(
    name = "collective.gsscripts",
    version = "0.1",
    install_requires = ['zc.recipe.egg'],
    entry_points = {
        'console_scripts' : [
            'exportsite = collective.gsscripts.exportsite:main',
        ],
        'plone.recipe.zope2instance.ctl' : [
            'createsite = collective.gsscripts.createsite:do_createsite'
        ],
    },
)
