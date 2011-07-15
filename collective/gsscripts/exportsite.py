#!/usr/bin/env python
"""Usage: %prog [-o http://host:port] [-u user[:pass]] [-d destination/]"""
usage = __doc__

import getpass
import os
import urllib
import tarfile
import tempfile
import optparse
import re

"""Option parsing for commandline mode"""
def main(default_user=None, default_host=None, default_dest=None, default_step='content_quinta'):
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        "-u", "--user", metavar="admin:admin",
        help="Username / password to log into site with",
        dest="user", default=default_user
    )
    parser.add_option(
        "-o", "--host", metavar="http://localhost:8080",
        help="HTTP(S) host to contact",
        dest="host", default=default_host
    )
    parser.add_option(
        "-d", "--dest", metavar="parts/omelette/my/product/profiles/testfixture/",
        help="Destination to dump export into",
        dest="dest", default=default_dest
    )
    parser.add_option(
        "-s", "--step", metavar="content_quinta, typeinfo",
        help="Step to export",
        dest="step", default=default_step
    )
    (options, args) = parser.parse_args()
    
    # Ensure we've got something for each option
    if not(options.user): parser.error('User needs to be specified in either buildout or commandline')
    if not(options.host): parser.error('Host needs to be specified in either buildout or commandline')
    if not(options.dest): parser.error('Destination needs to be specified in either buildout or commandline')
    
    # Fetch password interactively
    if options.user and options.user.find(':') < 0:
        passwd = getpass.getpass("Password for %s: " % options.host)
        options.user += ':' + passwd
    
    # Combine credentials and hostname into URL
    if not(re.match('https?://',options.host,re.IGNORECASE)):
        url = 'http://' + options.user + '@' + options.host
    else:
        url = re.sub(r'^([hH][tT][tT][pP][sS]?://)',r'\1'+options.user+'@', options.host)
    
    export_step(url, options.dest, options.step)

def export_step(url, base, step):
    # Request .tar.gz of content
    response = urllib.urlopen(
        re.sub('/+$','',url)+'/Plone/portal_setup',
        urllib.urlencode({
            'ids:default:tokens':'',
            'ids:list': step,
            'manage_exportSelectedSteps:method':' Export selected steps ',
        })
    )
    
    # Read response into a tempfile, open as tarfile
    merge_tar(response, base)

def merge_tar(f, base):
    # Read into a temporary file, then return as a tarfile object
    tfile = tempfile.TemporaryFile(suffix='.tar.gz')
    lines = '0'
    while len(lines) > 0:
        lines = f.read(1024)
        tfile.write(lines)
    tfile.seek(0)
    tar = tarfile.open(fileobj=tfile,mode="r:gz")

    # Search filesystem for existing files
    existing_files = set()
    for root, dirs, files in os.walk(base,topdown=False):
        if is_metadir(root): continue
        relpath = os.path.relpath(root,base)
        for dir in (os.path.normpath(os.path.join(relpath,d)) for d in dirs if not(is_metadir(d))):
            try:
                tarinfo = tar.getmember(dir)
                existing_files.add(dir)
            except KeyError:
                abs_dir = os.path.join(base,dir)
                if (root != base) and (len(os.listdir(abs_dir)) == 0): # Only remove if not at base and empty
                    print "[rmdir ] ",dir
                    os.rmdir(abs_dir)
        for file in (os.path.normpath(os.path.join(relpath,f)) for f in files):
            try:
                tar.getmember(file)
                existing_files.add(file)
                print "[write ] ",file
                tar.extract(file,path=base)
            except KeyError:
                if root != base: # Don't remove unknown files at base
                    print "[delete] ",file
                    os.remove(os.path.join(base,file))
    
    # add any new files
    for tarinfo in tar:
        if tarinfo.name in existing_files: continue
        if tarinfo.isdir():
            print "[mkdir ] ",tarinfo.name
            os.mkdir(os.path.join(base,tarinfo.name))
        else:
            print "[create] ",tarinfo.name
            tar.extract(tarinfo.name,path=base)

def is_metadir(dir):
    # Return true iff .svn is anywhere in path
    (h,t) = os.path.split(dir)
    if t == '.svn': return True
    if not(h) or h == os.path.sep: return False
    return is_metadir(h)

if __name__ == "__main__":
    main()
