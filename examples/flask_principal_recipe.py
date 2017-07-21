import flask
import flask_principal
import flask_saml

app = flask.Flask(__name__)
principals = flask_principal.Principal(app)
app.config.update({
    'SECRET_KEY': 'soverysecret',
    'SAML_METADATA_URL': 'https://metadata-url',
})
saml = flask_saml.FlaskSAML(app)

# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = flask_principal.Permission(flask_principal.RoleNeed('admin'))

#
# Connect SAML & Principal
#

@flask_saml.saml_authenticated.connect_via(app)
def on_saml_authenticated(sender, subject, attributes, auth):
    # We have a logged in user, inform Flask-Principal
    flask_principal.identity_changed.send(
        flask.current_app._get_current_object(),
        identity=get_identity(),
    )


@flask_saml.saml_log_out.connect_via(app)
def on_saml_logout(sender):
    # Let Flask-Principal know the user is gone
    flask_principal.identity_changed.send(
        flask.current_app._get_current_object(),
        identity=get_identity(),
    )


# This provides the users' identity in the application
@principals.identity_loader
def get_identity():
    if 'saml' in flask.session:
        return flask_principal.Identity(flask.session['saml']['subject'])
    else:
        return flask_principal.AnonymousIdentity()


@flask_principal.identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # If authenticated, you're an admin - yay!
    if not isinstance(identity, flask_principal.AnonymousIdentity):
        identity.provides.add(flask_principal.RoleNeed('admin'))


# protect a view with a principal for that need
@app.route('/admin')
@admin_permission.require()
def do_admin_index():
    return flask.Response('Only if you are an admin')

# this time protect with a context manager
@app.route('/articles')
def do_articles():
    with admin_permission.require():
        return flask.Response('Only if you are admin')


@app.errorhandler(flask_principal.PermissionDenied)
def handle_permission_denied(error):
    deny = 'Permission Denied', 403
    redirect = flask.redirect(flask.url_for('login', next=flask.request.url))
    if isinstance(flask.g.identity, flask_principal.AnonymousIdentity):
        return redirect
    else:
        return deny


if __name__ == '__main__':
    app.run(port=8000, debug=True)
