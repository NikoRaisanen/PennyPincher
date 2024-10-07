import os
import plaid
from flask import Flask, jsonify
from flask_cors import CORS
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.api import plaid_api
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
CORS(app)
client_id = os.getenv("PLAID_CLIENT_ID")
plaid_secret = os.getenv("PLAID_SECRET")

def get_link_token():
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
    user = 'niko'
    client_user_id = user

    request = LinkTokenCreateRequest(
        products=[Products('transactions')],
        client_name="Plaid Test App",
        country_codes=[CountryCode('US')],
        redirect_uri='https://localhost:3030',
        language='en',
        webhook='https://webhook.sample.com',
        user=LinkTokenCreateRequestUser(
            client_user_id=client_user_id
        )
    )
    response = client.link_token_create(request)
    return response['link_token']

@app.route('/api/create_link_token', methods=['GET'])
def create_link_token():
    try:
        link_token = get_link_token()
        return jsonify({"link_token": link_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
