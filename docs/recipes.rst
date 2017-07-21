=======
Recipes
=======

Integration with Flask Principal
================================

`Flask Principal`_ allows you do manage your user authentication information
and permissions. Flask SAML nicely by combining its own signal-based approach
with that of Flask Principal. This recipe shows a basic implementation of that.

.. note::

    Don't forget to update the metadata URL to your SAML provider or this code
    won't work. You might also need to update the ``port`` parameter depending
    on your SAML IdP configuration.

.. _Flask Principal: https://pythonhosted.org/Flask-Principal/

.. literalinclude:: ../examples/flask_principal_recipe.py
