from flask import Flask
import globus_sdk
import json

app = Flask(__name__)

endpointIDList = {"list": [{"name": "Tutorial Endpoint 1", "id": "ddb59aef-6d04-11e5-ba46-22000b92c6ec"},
                           {"name": "Zach's Laptop", "id": "636505f6-d784-11e7-96f1-22000a8cbd7d"}]}
CLIENT_ID = '8b721ec9-e8f7-472c-a8ac-d6b80afa7229'

client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
client.oauth2_start_flow(refresh_tokens=True)

authorize_url = client.oauth2_get_authorize_url()
print('Please go to this URL and login: {0}'.format(authorize_url))

get_input = getattr(__builtins__, 'raw_input', input)
auth_code = get_input(
    'Please enter the code you get after login here: ').strip()
token_response = client.oauth2_exchange_code_for_tokens(auth_code)

globus_auth_data = token_response.by_resource_server['auth.globus.org']
globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']

REFRESH_TOKEN = globus_transfer_data['refresh_token']
expires = globus_transfer_data['expires_at_seconds']
AUTH_TOKEN = globus_auth_data['access_token']
TRANSFER_TOKEN = globus_transfer_data['access_token']
print(CLIENT_ID)

authorizer = globus_sdk.RefreshTokenAuthorizer(REFRESH_TOKEN, client, access_token=AUTH_TOKEN, expires_at=expires)
tc = globus_sdk.TransferClient(authorizer=authorizer)

print("My Endpoints:")
for ep in tc.endpoint_search(filter_scope="my-endpoints"):
    print("[{}] {}".format(ep["id"], ep["display_name"]))

endChoice = tc.endpoint_search(filter_scope="my-endpoints")
staticEnd = tc.get("/endpoint_search", params=dict(filter_fulltext="Globus Tutorial Endpoint 1", limit=1))


@app.route('/')
def authInitial():
    myEnd = tc.get("/endpoint_search", params=dict(filter_fulltext=endChoice, limit=1, filter_scope="my-endpoints"))
    string = ""
    if len(myEnd["DATA"]):
        string = string + str(myEnd["DATA"][0]["id"])
    return string


@app.route('/files')
def files():
    myEnd = tc.get("/endpoint_search", params=dict(filter_fulltext=endChoice, limit=1, filter_scope="my-endpoints"))
    out = []
    for file in tc.operation_ls(myEnd["DATA"][0]["id"]):
        for item in file:
            if item == "name":
                fileDict = {"name": str(file[item]), "size": str(file["size"])}
                out.append(fileDict)
    output = {"files": out}
    return json.dumps(output)


@app.route('/endpoints')
def endpointList():
    return json.dumps(endpointIDList)


@app.route('/transfer/<otherEndpoint>/<filename>')
def transfer(otherEndpoint, filename):

    source_endpoint_id = "636505f6-d784-11e7-96f1-22000a8cbd7d"
    source_path = str(filename)

    dest_endpoint_id = str(otherEndpoint)
    dest_path = "/~/" + source_path
    label = "tutorial transfer"

    tdata = globus_sdk.TransferData(tc, source_endpoint_id, dest_endpoint_id, label=label)

    tdata.add_item(source_path, dest_path)

    tc.endpoint_autoactivate(source_endpoint_id)
    tc.endpoint_autoactivate(dest_endpoint_id)

    submit_result = tc.submit_transfer(tdata)
    print("Task ID:", submit_result["task_id"])
    myEnd = tc.get("/endpoint_search", params=dict(filter_fulltext=endChoice, limit=1, filter_scope="my-endpoints"))
    tutorial = tc.get_endpoint("ddb59aef-6d04-11e5-ba46-22000b92c6ec")
    data = globus_sdk.TransferData(tc, myEnd, tutorial)
    return json.dumps("Task Submitted")


@app.route("/test")
def test():
    return "test page test page test page"


@app.route("/owner")
def owner():
    myEnd = tc.get("/endpoint_search", params=dict(filter_fulltext=endChoice, limit=1, filter_scope="my-endpoints"))
    return myEnd["DATA"][0]["owner_string"]

if __name__ == '__main__':
    app.run()
    app.config["DEBUG"] = True
