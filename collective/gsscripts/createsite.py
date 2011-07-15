import os

import Zope2

from Products.CMFPlone.factory import addPloneSite

def do_createsite(self, arg):
    cmdline = self.get_startup_cmd(
        self.options.python,
        'from collective.gsscripts.createsite import stage2; stage2(r\'%s\')' % arg,
    )
    os.system(cmdline)

def stage2(arg):
    opts = arg.split()
    profiles = [opts[0]] if len(opts) > 0 else [];
    site_id = opts[1] if len(opts) > 1 else 'Plonb';
    
    app = Zope2.app()
    addPloneSite(app, site_id,
        extension_ids=profiles,
        setup_content=False,
    )
    import ipdb ; ipdb.set_trace()
