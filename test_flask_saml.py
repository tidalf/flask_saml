import flask
import flask_saml
import mock
import pytest
import xml.etree.ElementTree
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse


DUMMY_CERT = """
MIIDtzCCAp+gAwIBAgIJANCwF7VjtRF9MA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwIBcNMTcwNzEzMjIyNjU1WhgPMjExNzA2MTkyMjI2NTVa
MEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJ
bnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAw
ggEKAoIBAQC7uw5K/OVEDs9E9p5HGkVXYi76zWLdGoYIFdVPIOkT4ls1wgyf/HdG
v1pk+FWiqVBIvPUmOgj6dRYVvk6NIftPuk3B/91fU8Qc9wENd8yc5ldA6p9FQs/x
Nj1n4i1Ybgf6OphOSYKWt5MJk3HrWryFbZ/RJ6/CfGj0CyVEuuPi6vyXo2fQ8f97
4snuLXYsGjiNKheNhqsFm917uaT1D5b05AWJdbPj5jskk7djVYLA9lm1jRpnpMaU
/anQMOmiUxfDNJmku0TpmHOah2m7+H+kGR1j3icWPKzgTPEtmjl4tjzuPdeNVaoQ
M4tU3OnBntCvP3nUqifyMHnEbbEiUDudAgMBAAGjgacwgaQwHQYDVR0OBBYEFJhI
NQPoRlWf5E56lZpWVmMZPIN7MHUGA1UdIwRuMGyAFJhINQPoRlWf5E56lZpWVmMZ
PIN7oUmkRzBFMQswCQYDVQQGEwJBVTETMBEGA1UECBMKU29tZS1TdGF0ZTEhMB8G
A1UEChMYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkggkA0LAXtWO1EX0wDAYDVR0T
BAUwAwEB/zANBgkqhkiG9w0BAQUFAAOCAQEAoxK3XYzXNftkLe3Q7BBBH+zrBYLR
JLu3GNdMAWTc4pZeqoTTtXUHylWcLFKnq+eocOFSGyft9G1/VFt+5WupkhXuPG4x
VCP2gp7Qc9j6POmKviXdMW659d1BHOPTkF0M00qW3mP+TGevdQtDwGLTDyB5FuJQ
INp7+OJXjs+Nkphx0W1IUnA3H1YqEv3zNIO0Scjd/5Ub+eQYXTXkzrhR+Zy0a3KH
fkBaCGAN/QXpPk/Dm7zfx3+SUG3g4FPdWyKo77F7Wc1FgkmInW4kMoKzhDkpV0Po
ve93k3XbM6fO1FuQ4m1JS080aGud8y/qtfzbBfeP5PSpskv6DMZkaZTxIg==
"""


def make_settings(**kwargs):
    kwargs.setdefault('app_id', 123)
    kwargs.setdefault('app_url', 'https://foo.bar')
    kwargs.setdefault('idp_cert', 'ABC')
    return flask_saml._get_settings(**kwargs)


def get_ext(app, *args, **kw):
    app.config.setdefault('SAML_METADATA_URL', '...')
    with open('metadata_sample.xml') as f:
        metadata = f.read()
    p = mock.patch(
        'flask_saml._get_metadata',
        return_value=metadata,
    )
    with p:
        ext = flask_saml.FlaskSAML(app, *args, **kw)
    return ext


def get_app():
    app = flask.Flask(__name__)
    app.config['SECRET_KEY'] = 'asd'
    return app


@pytest.fixture
def app():
    return get_app()


@pytest.fixture
def ext(app):
    return get_ext(app)


def test_get_return_to_no_next(webapp):
    with webapp.test_request_context('/'):
        assert flask_saml._get_return_to() == '/'


def test_get_return_to_no_external_domain(webapp):
    return_to = 'https://external.com'
    with webapp.test_request_context('/?next={}'.format(return_to)):
        assert flask_saml._get_return_to() == '/'


def test_get_return_to_internal_next(webapp):
    return_to = 'http://localhost/asd/'
    with webapp.test_request_context('/?next={}'.format(return_to)):
        assert flask_saml._get_return_to() == 'http://localhost/asd/'


def test_own_session_funcs(mocker):
    session = {}

    def login(sender, subject, attributes, auth):
        session['authed'] = True

    def logout(sender):
        session.clear()

    app = get_app()
    app.config['SAML_USE_SESSIONS'] = False
    ext = get_ext(app)
    flask_saml.saml_authenticated.connect(login, app)
    flask_saml.saml_log_out.connect(logout, app)

    with app.test_client() as client:
        data = {
            'SAMLResponse': '',
        }
        mocker.patch(
            'saml2.client.Saml2Client.parse_authn_request_response',
            autospec=True
        )
        mocker.patch(
            'saml2.response.AuthnResponse.get_identity', autospec=True,
            return_value={},
        )
        mocker.patch(
            'saml2.response.AuthnResponse.get_subject', autospec=True,
            return_value='foo@bar.com',
        )
        response = client.post('/saml/acs/', data=data)
        assert response.status_code == 302
        assert session['authed']


@pytest.fixture
def webapp(app, ext):
    return app


def test_login_flow(webapp, mocker):
    with webapp.test_client() as client:
        response = client.get('/saml/sso/')
        assert response.status_code == 302
        data = {
            'SAMLResponse': '',
            'RelayState': 'http://127.0.0.1:8000/'
        }
        parse_authn = mocker.patch(
            'saml2.client.Saml2Client.parse_authn_request_response',
            autospec=True,
        )
        response = parse_authn.return_value
        attributes = {
            'User.FirstName': ['A'],
            'User.LastName': ['B'],
            'User.email': ['foo@bar.com'],
            'memberOf': ['OU=a OU=b DC=com DC=foo CN=asd'],
        }
        response.get_identity.return_value = attributes
        response.get_subject.return_value.text = 'foo@bar.com'
        response = client.post('/saml/acs/', data=data)
        assert response.status_code == 302
        saml = flask.session['saml']
        assert saml['attributes'] == attributes
        assert saml['subject'] == 'foo@bar.com'

        response = client.get('/saml/logout/')
        assert response.status_code == 302
        assert 'saml' not in flask.session


def test_acs_response_None(webapp, mocker):
    errors = []

    @flask_saml.saml_error.connect_via(webapp)
    def on_saml_error(sender, exception):
        errors.append(exception.args[0])

    with webapp.test_client() as client:
        data = {
            'SAMLResponse': '',
            'RelayState': 'http://127.0.0.1:8000/'
        }
        mocker.patch(
            'saml2.client.Saml2Client.parse_authn_request_response',
            autospec=True,
            return_value=None,
        )
        response = client.post('/saml/acs/', data=data)
        assert response.status_code == 302
        assert 'saml' not in flask.session
        assert errors[0]


def test_login_redirect(webapp, mocker):
    with webapp.test_client() as client:
        return_to = 'http://localhost/return_here'
        response = client.get('/saml/sso/?next={}'.format(return_to))
        assert response.status_code == 302
        redirect = response.headers['Location']
        url = urlparse.urlparse(redirect)
        query = urlparse.parse_qs(url.query)
        [relay_state] = query['RelayState']
        assert relay_state == 'http://localhost/return_here'


def test_login_default_redirect(webapp, mocker):
    webapp.extensions['saml'][1]['default_redirect'] = '/defaultz'
    with webapp.test_client() as client:
        data = {
            'SAMLResponse': '',
        }
        parse_authn = mocker.patch(
            'saml2.client.Saml2Client.parse_authn_request_response',
            autospec=True,
        )
        response = parse_authn.return_value
        attributes = {}
        response.get_identity.return_value = attributes
        response.get_subject.return_value.text = 'foo@bar.com'
        response = client.post('/saml/acs/', data=data)
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/defaultz')


def test_error_signal_login(webapp, mocker):
    received_errors = []

    @flask_saml.saml_error.connect_via(webapp)
    def error(sender, exception):
        received_errors.append(exception.args[0])

    # Make sure login is never signalled
    @flask_saml.saml_authenticated.connect_via(webapp)
    def authenticated(sender, auth):
        raise ValueError('Auth signal should not have been sent')
    with webapp.test_client() as client:
        data = {
            'SAMLResponse': '',
        }
        parse_authn = mocker.patch(
            'saml2.client.Saml2Client.parse_authn_request_response',
            autospec=True,
            side_effect=KeyError('myerror1'),
        )
        response = client.post('/saml/acs/', data=data)
        assert response.status_code == 302
        assert received_errors == ['myerror1']


def test_metadata(webapp):

    with webapp.test_client() as client:
        response = client.get('/saml/metadata/')
        assert response.status_code == 200
        assert response.content_type == 'text/xml'
        data = response.get_data(as_text=True)
        assert xml.etree.ElementTree.fromstring(data)
