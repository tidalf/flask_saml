============
Installation
============

Beyond installing the library (e.g. ``pip install flask_saml``) you need to
have ``xmlsec1`` installed, e.g. for Ubuntu:

.. code-block:: bash

    apt-get install xmlsec1

Quickstart
==========


.. code-block:: python

    import flask
    import flask_saml

    app = flask.Flask(__name__)

    app.config.update({
        'SECRET_KEY': 'soverysecret',
        'SAML_METADATA_URL': 'https://mymetadata.xml',
    })
    flask_saml.FlaskSAML(app)


Let's go step by step. The ``SECRET_KEY`` is required by the default session
storage (see :ref:`session_replacement` if you would like to use a different
mechanism to manage sessions). ``SAML_METADATA_URL`` is a URL that contains the
SAML metadata which configures the whole app.

.. warning::

    The metadata URL should be a HTTPS URL as an untrusted source for metadata
    will allow an attacker to log in as any user they like.

The extension also sets up the following routes:

* ``/saml/logout/``: Log out from the application. This is where users
  go if they click on a "Logout" button.
* ``/saml/sso/``: Log in through SAML.
* ``/saml/acs/``: After ``/saml/sso/`` has sent you to your IdP it sends you
  back to this path. Also your IdP might provide direct login without needing
  the ``/saml/sso/`` route.

In general you don't need to worry about this too much. Sending users to login
and logout is as simple as calling ``flask.url_for('login')`` and
``flask.url_for('logout')`` using Flasks :func:`flask.url_for` method.

.. note::

    To send the user back to a specific URL after a login, provide the ``next``
    parameter:

    .. code-block:: python

        flask.url_for('login', next='http://localhost:8080/foobar')

    Be advised that only things that belong to the correct domain and port
    will be accepted. Also, there is currently no support for a redirect
    after a logout.

Now that we have the basics covered, let's go over some finer details in case
you wish to tweak some of the bits. This might already cover everything you
need but in case you want to tweak the configuration check out
:ref:`advanced_config`.
