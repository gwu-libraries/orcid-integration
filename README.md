# orcid-integration
ORCID middleware to enable our researchers to designate GW as a trusted partner

1. Set up Python 3 virtual environment.
2. To use python3-saml, it's necessary to install some dependencies. On Ubuntu, do the following:
    - `apt-get install libxml2-dev libxmlsec1-dev libxmlsec1-openssl`
    - To get the latest version of LibXML2, I also had to the following:
    ```
    apt-get install build-essential
    apt-get install python3-dev
    wget http://xmlsoft.org/sources/libxml2-2.9.1.tar.gz
    tar -xvf libxml2-2.9.1.tar.gz
    cd libxml2-2.9.1
    ./configure && make && make install
    ```
3. `pip install -r requirements.txt`
4. Copy the example configuration file and edit it to provide sensitive keys, including the SERVER_KEY, ORCID client ID and ORCID client secret. \
 `cp example.config.py config.py`
5. From the command line: \
 `export FLASK_APP=orcidflask` \
 `export ORCIDFLASK_SETTINGS=/path/to/config.py`
6. `flask run --host=0.0.0.0` (to listen on all public IP addresses) \
To specify a port: `flask run --host=0.0.0.0 --port=8080`
