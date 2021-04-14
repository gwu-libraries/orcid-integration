# orcid-integration
ORCID middleware to enable our researchers to designate GW as a trusted partner

1. Set up Python 3 virtual environment.
2. `pip install -r requirements.txt`
3. In `test_server.py`, populate the Client ID and Client Secret fields in the `app.config` definitions.
4. From the command line, `export FLASK_APP=test_server.py`
5. `flask run --host=0.0.0.0` (to listen on all public IP addresses)
