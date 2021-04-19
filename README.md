# orcid-integration
ORCID middleware to enable our researchers to designate GW as a trusted partner

1. Set up Python 3 virtual environment.
2. `pip install -r requirements.txt`
3. Copy the example configuration file and edit it to provide sensitive keys, including the SERVER_KEY, ORCID client ID and ORCID client secret. \
 `cp example.config.py config.py`
4. From the command line: \
 `export FLASK_APP=orcidflask` \
 `export ORCIDFLASK_SETTINGS=/path/to/config.py`
5. `flask run --host=0.0.0.0` (to listen on all public IP addresses) \
To specify a port: `flask run --host=0.0.0.0 --port=8080`
