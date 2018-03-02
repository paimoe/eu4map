import os

from fabric.api import run, env, abort
from fabric.operations import put
from fabric.contrib.project import rsync_project as rsync

env.hosts = ['linode']
env.use_ssh_config = True

path = os.path.join

def deploy():

    map_path = '/srv/www/eu4/map/app'
    dist_dir = path(os.getcwd(), 'app', 'dist/')

    curr = path(map_path, 'current')
    prev = path(map_path, 'previous')

    # Make sure we have it built
    if not os.path.exists(dist_dir) or not os.path.exists(os.path.join(dist_dir, 'index.html')):
        abort('Build directory does not exist')

    # Move old version to /previous
    run('cp -r {0} {1}'.format(path(curr, '*'), prev))

    # scp build dir to /current
    build_dir = os.path.join(os.getcwd(), 'app', 'dist')
    assert os.path.exists(build_dir)

    rsync(local_dir=dist_dir, remote_dir=curr, exclude=[])
    # Add versions/symlinks later

    # Restart in supervisor/nginx? no since just static stuff