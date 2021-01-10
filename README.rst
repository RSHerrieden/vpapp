=====
vpapp
=====

Vpapp is a django app to parse replacement-plans from the Realschule Herrieden
and provide them in a format so that the corresponding Android-App can use them.

Quick start
-----------

1. Add "vpapp" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        'vpapp',
        ...
    ]

2. Configure XML Endpoint in your settings:

   VPAPP_RSH_URL='http://localhost:9000/data_{:%Y-%m-%d}.xml'

3. Include the polls URLconf in your project urls.py like this::

    path('', include('vpapp.urls')),

4. Run ``python manage.py migrate`` to create the polls models.

5. 4un ``python manage.py scrape`` to collect the next replacement-plans.

6. Visit http://127.0.0.1:8000/ to view the webapp with the replacements
