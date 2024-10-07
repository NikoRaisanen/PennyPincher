import os
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.api import plaid_api
import plaid
from dotenv import load_dotenv


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

if __name__ == "__main__":
    load_dotenv()
    client_id = os.getenv("PLAID_CLIENT_ID")
    plaid_secret = os.getenv("PLAID_SECRET")
    link_token = get_link_token()