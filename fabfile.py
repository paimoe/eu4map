"""
# Uh deploy plz
# python deploy.py 

increment version
ssh transfer the folder (exluding certain things that don't need to be)
to /srv/eu4map/<version>, symlink /srv/<proj>/beta to that new version
should already be linked up in nginx
when i've verified it live (unit tests run on computer) then symlink /srv/<proj>/live to the new version, and symlink /srv/<proj>/revert to the old version? so a revert is just going back to that basically, ro store the data in a text file 
"""

import os, shutil

from fabric.api import run, env, abort, local, cd
from fabric.operations import put
from fabric.contrib.project import rsync_project as rsync

env.hosts = ['linode']
env.use_ssh_config = True

path = os.path.join

def deploy():

    map_path = '/srv/www/eu4/map/app'
    dist_dir = path(os.getcwd(), 'vapp/')

    curr = path(map_path, 'current')
    prev = path(map_path, 'previous')

    # Make sure we have it built
    if not os.path.exists(dist_dir) or not os.path.exists(os.path.join(dist_dir, 'index.html')):
        abort('Build directory does not exist')

    # Move old version to /previous
    run('cp -r {0} {1}'.format(path(curr, '*'), prev))

    # scp build dir to /current

    rsync(local_dir=dist_dir, remote_dir=curr, exclude=[])
    # Add versions/symlinks later

    # Restart in supervisor/nginx? no since just static stuff