.. currentmodule:: flask_saml

.. _advanced_config:

======================
Advanced Configuration
======================

.. _session_replacement:

Change User Storage
===================

The default implementation will just store the user in a session.
Alternatively, you can use whatever method your prefer. To realise this, the
extension provides two functions you can implement. You can either
implement all or none of them since they work hand in hand.

1. The login signal: Once a user successfully authenticated, the extension
   sends the user data over via the :data:`saml_authenticated` signal.
2. The logout signal: When a user logs out, this signal must make sure all
   data relating to that users session are cleared. The signal
   :data:`saml_log_out` is sent.


Here's what the default implementation does:

.. code-block:: python

    def _session_login(sender, subject, attributes, auth):
        flask.session['saml'] = {
            'subject': subject,
            'attributes': attributes,
        }


    def _session_logout(sender):
        flask.session.clear()

Assuming the same configuration as above, we can create the extension like
this:

.. code-block:: python

    app.config['SAML_USE_SESSIONS'] = False
    ext = flask_saml.FlaskSAML(app)

    flask_saml.saml_authenticated.connect(_session_login, app)
    flask_saml.saml_log_out.connect(_session_logout, app)

As you can see, the ``_session_login`` function receives a ``subject`` and
``attributes`` for the user. In addition an ``auth`` object is provided. In
most cases you will only need the ``subject`` which is the unique identifier
for the user (for example an e-mail) and the attributes which contains all the
SAML attributes. These were both received from the ``auth`` object which can be
used for more advanced operations.

.. _error_handling:

Error Handling
==============

Ocassionally, errors will happen during login. If you don't do anything they
will go into the void and they are not very useful there. So let's hook into
the :class:`saml_error` signal! Any time an error happens, this function gets
the exception thrown by the `PySAML2`_ library. Here is what
a simple Flask app might do with it:

.. code-block:: python

    @flask_saml.saml_error.connect_via(app)
    def on_saml_error(sender, exception):
        flask.flash(exception.args[0], 'error')

.. _PySAML2: https://github.com/rohe/pysaml2

This uses Flask's flashing mechanism but what you do with them is really up
to you. We just send them your way and don't worry about it too much.

Changing the Route Prefix
=========================

Maybe you think ``/saml`` is a stupid prefix (because ``/teddybear`` make more
sense in your opinion) or you have a collision. So change the prefix:

.. code-block:: python

    app.config['SAML_PREFIX'] = '/teddybear'
    flask_saml.FlaskSAML(app)

Change the Default Redirect
===========================

By default the user is redirected to ``/``. If you would rather have a
different landing page, then that's totally possible:

.. code-block:: python

    app.config['SAML_DEFAULT_REDIRECT'] = '/dashboard'

So now on both logout and login, this is your default. Remember, for login you
can always provide the ``next`` parameter to specify where the user should go
after a successful login.


API
===

Extension
---------

.. autoclass:: FlaskSAML
    :members:

Signals
-------

.. data:: saml_authenticated

    Signal sent when the user has successfully authenticated. Receives three
    parameters: ``subject``, ``attributes`` and ``auth``. ``auth`` is the
    actual ``saml.response.AuthnResponse`` from which both ``subject`` and
    ``attributes`` were extracted.

    Can be used to override the default session implementation as described in
    :ref:`session_replacement`.

.. data:: saml_log_out

    Signal sent when the user has logged out. Delete all authentication
    references, such as clearing the session to ensure the user has no further
    access to the application. No parameters.

    Used together with :data:`saml_authenticated` to override default session
    implementation.

.. data:: saml_error

    Signal sent when an error ocurred. Receives instance of exception thrown
    when trying to log in user. See :ref:`error_handling` for more details.
