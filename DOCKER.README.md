## Deployment

### Principles

 * Execute the application directly via the container. For the time being, we are not using a container management layer.
 * Specify /dev/shm as Gunicorn's worker-tmp-dir for performance reasons. For details, see: https://pythonspeed.com/articles/gunicorn-in-docker/
 * Execute via a socket file for deployment simplicity. This may not be performant on non-linux systems.
 * Run multiple gunicorn workers in deployment

### Prep

 * create the directory `mnt` in the project root
 * create a .env file in the project root

**collect static files**

Note: `STATIC_TMPDIR` in the env variables is actually the STATIC_ROOT, and should be set to:

```
STATIC_TMPDIR=mnt/static/cityhallmonitor/
```

That is, static files should be placed into a project-specific directory in order to facilitate proxying to multiple applications.

```
$ sudo docker run -it --env-file=.env -v /home/apps/sites/cityhallmonitor/mnt:/usr/src/app/mnt cityhallmonitor ./manage.py collectstatic
```

### Running the application

Execute gunicorn via a daemonized container (do this from the systemctl config file):

```
$ sudo docker run -d --env-file=.env -v /home/apps/sites/cityhallmonitor/mnt:/usr/src/app/mnt --name cityhallmonitor cityhallmonitor gunicorn --workers 3 --worker-tmp-dir /dev/shm --bind unix:/usr/src/app/mnt/cityhallmonitor.sock core.wsgi:application
```

To stop the container:

```
$ sudo docker stop cityhallmonitor
```

### Troubleshooting

Replace -d with -it to execute in interactive mode and to see application logs:

```
$ sudo docker run -it --env-file=.env -v /home/apps/sites/cityhallmonitor/mnt:/usr/src/app/mnt cityhallmonitor gunicorn --worker-tmp-dir /dev/shm --bind unix:/usr/src/app/mnt/cityhallmonitor.sock core.wsgi:application
```

Alternatively, execute a bash shell and run gunicorn from inside the container:

```
$ sudo docker run -it --env-file=.env -v /home/apps/sites/cityhallmonitor/mnt:/usr/src/app/mnt cityhallmonitor sh

# gunicorn --worker-tmp-dir /dev/shm --bind unix:/usr/src/app/mnt/cityhallmonitor.sock core.wsgi:application
```

To run gunicorn on a port and bypass Nginx:

```
$ sudo docker run -it --env-file=.env -p 8000:8000 cityhallmonitor gunicorn -b :8000 core.wsgi:application
```
