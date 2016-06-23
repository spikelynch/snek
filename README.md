s n e k
=======

a lightweight Python frontend to Fedora Commons 4

## Getting started

Install:

* fcrepo4
* django

Then do the following --

    git clone git@codeine.research.uts.edu.au:eresearch/snek.git
    cd snek
    python manage.py migrate
    python manage.py createsuperuser

Create a file snek/settings_local.py with config for your Fedora server
and username/password: it should look like this

    FCREPO = {
        'uri': 'http://localhost:8080/fcrepo/',
        'users': {
            'user': {
                'user': 'YOUR_ADMIN_USER',
                'password': 'YOUR_PASSWORD'
                }
            }
        }

Now

    python manage.py runserver

Browse to http://localhost:8000/ and log in with the superuser account. You should get a page pointed at the root container of the Fedora server.



    
