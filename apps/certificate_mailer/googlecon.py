from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, _RedirectWSGIApp, _WSGIRequestHandler
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import webbrowser
import wsgiref.simple_server
import wsgiref.util

# If modifying these scopes, delete the file token.picklefrom 
import os
from apps.certificate_mailer.utils import mkdir
from apps import socket_io_events as ioe

basedir = os.path.abspath(os.path.dirname(__file__))

class InstalledAppFlowExtend(InstalledAppFlow):
    _OOB_REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

    _DEFAULT_AUTH_PROMPT_MESSAGE = (
        "Please visit this URL to authorize this application: {url}"
    )
    """str: The message to display when prompting the user for
    authorization."""
    _DEFAULT_AUTH_CODE_MESSAGE = "Enter the authorization code: "
    """str: The message to display when prompting the user for the
    authorization code. Used only by the console strategy."""

    _DEFAULT_WEB_SUCCESS_MESSAGE = (
        "The authentication flow has completed. You may close this window."
    )
    def run_local_server(
        self,
        host="localhost",
        bind_addr=None,
        port=8080,
        authorization_prompt_message=_DEFAULT_AUTH_PROMPT_MESSAGE,
        success_message=_DEFAULT_WEB_SUCCESS_MESSAGE,
        open_browser=False,
        redirect_uri_trailing_slash=True,
        timeout_seconds=None,
        new_tab_sio=True,
        **kwargs
    ):
        """Run the flow using the server strategy.

        The server strategy instructs the user to open the authorization URL in
        their browser and will attempt to automatically open the URL for them.
        It will start a local web server to listen for the authorization
        response. Once authorization is complete the authorization server will
        redirect the user's browser to the local web server. The web server
        will get the authorization code from the response and shutdown. The
        code is then exchanged for a token.

        Args:
            host (str): The hostname for the local redirect server. This will
                be served over http, not https.
            bind_addr (str): Optionally provide an ip address for the redirect
                server to listen on when it is not the same as host
                (e.g. in a container). Default value is None,
                which means that the redirect server will listen
                on the ip address specified in the host parameter.
            port (int): The port for the local redirect server.
            authorization_prompt_message (str | None): The message to display to tell
                the user to navigate to the authorization URL. If None or empty,
                don't display anything.
            success_message (str): The message to display in the web browser
                the authorization flow is complete.
            open_browser (bool): Whether or not to open the authorization URL
                in the user's browser.
            redirect_uri_trailing_slash (bool): whether or not to add trailing
                slash when constructing the redirect_uri. Default value is True.
            timeout_seconds (int): It will raise an error after the timeout timing
                if there are no credentials response. The value is in seconds.
                When set to None there is no timeout.
                Default value is None.
            kwargs: Additional keyword arguments passed through to
                :meth:`authorization_url`.

        Returns:
            google.oauth2.credentials.Credentials: The OAuth 2.0 credentials
                for the user.
        """
        wsgi_app = _RedirectWSGIApp(success_message)
        # Fail fast if the address is occupied
        wsgiref.simple_server.WSGIServer.allow_reuse_address = False
        local_server = wsgiref.simple_server.make_server(
            bind_addr or host, port, wsgi_app, handler_class=_WSGIRequestHandler
        )

        redirect_uri_format = (
            "http://{}:{}/" if redirect_uri_trailing_slash else "http://{}:{}"
        )
        self.redirect_uri = redirect_uri_format.format(host, local_server.server_port)
        auth_url, _ = self.authorization_url(**kwargs)

        if open_browser:
            webbrowser.open(auth_url, new=1, autoraise=True)

        if new_tab_sio:
            ioe.open_uri(auth_url)

        if authorization_prompt_message:
            print(authorization_prompt_message.format(url=auth_url))

        local_server.timeout = timeout_seconds
        local_server.handle_request()

        # Note: using https here because oauthlib is very picky that
        # OAuth 2.0 should only occur over https.
        authorization_response = wsgi_app.last_request_uri.replace("http", "https")
        self.fetch_token(authorization_response=authorization_response)

        # This closes the socket
        local_server.server_close()

        return self.credentials



class Service():
    def __init__(self):
        self.gCreds = None

    def get_creds(self, tokenFileName):
        #.readonly
        SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/spreadsheets']
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_path = os.path.join(basedir, f'tokens/{tokenFileName}.json')
        if os.path.exists(token_path) and tokenFileName != '':
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            #if creds and creds.expired and creds.refresh_token:
            #    creds.refresh(Request())
            #else:
            flow = InstalledAppFlowExtend.from_client_secrets_file(os.path.join(basedir,'kernel/app_credential.json'), SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)
            # Save the credentials for the next run
            mkdir(os.path.join(basedir,"tokens/"))
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        self.gCreds = creds

    def gmail(self):
        try:
            return build(serviceName='gmail', version='v1', credentials=self.gCreds, static_discovery=False)
        except Exception as e:
            print("Error in {0}".format("oauth_login.gmail_service"))
            raise e
        

    def sheets(self):
        try:
            return build(serviceName='sheets', version='v4', credentials=self.gCreds, static_discovery=False)
        except Exception as e:
            print("Error in {0}".format("oauth_login.sheets_service"))
            raise e
        
