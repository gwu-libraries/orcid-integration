from flask import request, Blueprint, jsonify
from orcidflask.db.models import Token, APIKey
import re

auth_pattern = re.compile(r'Apikey ([A-Za-z0-9\-]{36})')

api = Blueprint('api', __name__,  url_prefix='/api')

def is_valid(api_key):
    return APIKey.check_api_key(api_key)

@api.route('/get-token')
def get_token():
    '''GET request should include Authorization: Apikey header (with a valid API key) and an orcid URL parameter with the ORCiD of the user whose token is to be retrieved.'''
    api_key = auth_pattern.match(request.headers.get('Authorization', ''))
    if not api_key:
        return {'message': 'Please provide a valid API key in the Authorization header of your request.'}, 403
    api_key = api_key.group(1)
    if not is_valid(api_key):
        return {'message': 'API key has not been registered. Please have the application administrator create an API key for you.'}, 403
    orcid = request.args.get('orcid')
    if not orcid:
        return {'message': 'Please provide a valid ORCiD as a URL parameter, e.g., "?orcid=0000-0000-0000-0000"'}, 422
    access_token = Token.query.filter_by(orcid=orcid).order_by(Token.timestamp.desc()).first()
    if not access_token:
        return jsonify({'error': f'Entry not found for ORCiD {orcid}. Has the user registered with the GW ORCiD integration app?'})
    return jsonify({'orcid': orcid,
                    'access_token': access_token.to_dict()['access_token']})
    



