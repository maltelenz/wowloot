WhoOwsWhat Loot (wowloot)
=========================
Django project to figure out who ows what to whom.

Getting started
---------------

0. Install Django: https://docs.djangoproject.com/en/1.9/intro/install/

1. Copy settings-template.py to settings.py.
2. In settings.py, edit the following:
	* The path field in DATABASES to where you want to store your database file.
	* TEMPLATE_DIRS to where your templates are stored (they are in this repository under 'templates').
	* OPEN_EXCHANGE_APP_ID to the app id you get by signing up at https://openexchangerates.org/signup/free
3. In a shell:
```
$ cd wowloot
$ python manage.py migrate
$ python manage.py update_currency
$ python manage.py runserver
```

Dependencies
------------
### Server side
* Python
* Django (1.4)

### External
* http://openexchangerates.org/ (Documentation at http://openexchangerates.org/documentation/)

Usage Notes/Thanks
-----------
The error pages for this project (404, 500) use the beasts created by Matthew Inman from TheOatmeal.com.


License
-------
<a rel="license" href="http://creativecommons.org/licenses/by-nc/3.0/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by-nc/3.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/3.0/">Creative Commons Attribution-NonCommercial 3.0 Unported License</a>.

