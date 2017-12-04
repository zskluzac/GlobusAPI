from flask import Flask
import globus_sdk

app = Flask(__name__)


@app.route('/')
def authInitial():
    CLIENT_ID = '8b721ec9-e8f7-472c-a8ac-d6b80afa7229'

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow()

    authorize_url = client.oauth2_get_authorize_url()
    print('Please go to this URL and login: {0}'.format(authorize_url))

    # this is to work on Python2 and Python3 -- you can just use raw_input() or
    # input() for your specific version
    get_input = getattr(__builtins__, 'raw_input', input)
    auth_code = get_input(
        'Please enter the code you get after login here: ').strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    globus_auth_data = token_response.by_resource_server['auth.globus.org']
    globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']

    # most specifically, you want these tokens as strings
    AUTH_TOKEN = globus_auth_data['access_token']
    TRANSFER_TOKEN = globus_transfer_data['access_token']
    print(CLIENT_ID)

    # a GlobusAuthorizer is an auxiliary object we use to wrap the token. In
    # more advanced scenarios, other types of GlobusAuthorizers give us
    # expressive power
    authorizer = globus_sdk.AccessTokenAuthorizer(TRANSFER_TOKEN)
    tc = globus_sdk.TransferClient(authorizer=authorizer)

    # high level interface; provides iterators for list responses
    print("My Endpoints:")
    for ep in tc.endpoint_search(filter_scope="my-endpoints"):
        print("[{}] {}".format(ep["id"], ep["display_name"]))

    endChoice = tc.endpoint_search(filter_scope="my-endpoints")
    staticEnd = tc.get("/endpoint_search", params=dict(filter_fulltext="Globus Tutorial Endpoint 1", limit=1))
    myEnd = tc.get("/endpoint_search", params=dict(filter_fulltext=endChoice, limit=1, filter_scope="my-endpoints"))

    print(myEnd, staticEnd)
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
