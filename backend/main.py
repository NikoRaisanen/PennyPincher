import os
import plaid
import reader
from flask import Flask, jsonify, request
from flask_cors import CORS
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.api import plaid_api
from dotenv import load_dotenv

app = Flask(__name__)

# TODO: use logger instead of print statements
# TODO: get balance: https://plaid.com/docs/api/products/balance/
load_dotenv()
CORS(app)
client_id = os.getenv("PLAID_CLIENT_ID")
plaid_secret = os.getenv("PLAID_SECRET")
configuration = plaid.Configuration(
        host=plaid.Environment.Production,
        api_key={
            'clientId': client_id,
            'secret': plaid_secret,
            'plaidVersion': '2020-09-14'
        }
    )
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def get_link_token(user_id):
    request = LinkTokenCreateRequest(
        products=[Products('transactions')],
        client_name="Plaid Test App",
        country_codes=[CountryCode('US')],
        redirect_uri='https://localhost:3030',
        language='en',
        user=LinkTokenCreateRequestUser(
            client_user_id=user_id
        )
    )
    response = client.link_token_create(request)
    return response['link_token']

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    session = request.json.get('user_session')
    try:
        link_token = get_link_token(session)
        return jsonify({"link_token": link_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_public_token():
    try:
        session = request.json.get('user_session')
        public_token = request.json.get('public_token')
        print('request.json: ', request.json)
        x_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(x_request)
        response = response.to_dict()
        print('response: ', response)
        access_token = response.get('access_token')
        item_id = response.get('item_id')

        # TODO: validate that this works
        req = ItemGetRequest(access_token=access_token)
        item_get_res = client.item_get(req)
        institution_name = item_get_res['data']['item']['institution_name']
        print("Access token provisioned for institution: ", institution_name)

        # save access token for user
        db = reader.read_file()
        db[session].append({
            "access_token": access_token,
            "item_id": item_id,
            "inst_name": institution_name
        })
        reader.write_file(db)
        return jsonify({"access_token": access_token, "item_id": item_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/balance/get', methods=['POST'])
def get_balance():
    try:
        session = request.json.get('user_session')
        # get access token from db
        db = reader.read_file()
        user_info = db.get(session)
        access_token = user_info.get('access_token')
        req = AccountsBalanceGetRequest(access_token=access_token)
        response = client.accounts_balance_get(req)
        response = response.to_dict()
        print('response from balance/get: ', response)

        accounts = response.get('accounts')
        # what pieces of data should I return?
        return jsonify({"accounts": accounts}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/item', methods=['POST'])
def get_inst_by_id():
    try:
        session = request.json.get('user_session')
        db = reader.read_file()
        user_info = db.get(session)[0]
        access_token = user_info.get('access_token')
        req = ItemGetRequest(access_token=access_token)
        response = client.item_get(req)
        print("respnse: ", response)
        return jsonify({"data": response.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
