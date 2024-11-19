import os
import plaid
import reader
from flask import Flask, jsonify, request
from flask_cors import CORS
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
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

@app.route('/api/create_link_token', methods=['GET'])
def create_link_token():
    try:
        link_token = get_link_token('niko-account-id')
        return jsonify({"link_token": link_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_public_token():
    try:
        public_token = request.json.get('public_token')
        print('request.json: ', request.json)
        x_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(x_request)
        print('response: ', response)
        access_token = response.get('access_token')
        item_id = response.get('item_id')

        return jsonify({"access_token": access_token, "item_id": item_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
