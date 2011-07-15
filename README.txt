Introduction
============

This package contains a few scripts that allow you to export a genericsetup
profile into somewhere on the filesystem, working around your VCS meta
directories if present *looks at .svn*.

Installing exportsite
---------------------

Place something along these lines in your buildout.cfg

    parts += export
      .  .  .
    [export]
    recipe = zc.recipe.egg
    eggs = collective.gsscripts
    arguments =
        default_user='${instance:user}',
        default_host='localhost:${instance:http-address}',
        default_dest='parts/omelette/shuttlethread/farmyard/profiles/testfixture/',
        default_step='content_quinta',

This will create a bin/exportsite script that by default logs into the local
instance and exports all the content into the testfixture directory.
     
Installing importsite
---------------------

TODO: This doesn't actually work yet but documentation is always good, right?

    [instance]
    eggs += collective.gsscripts


