# orcid-integration
ORCID middleware to enable our researchers to designate GW as a trusted partner

1. Set up Python 3 virtual environment.
2. To use python3-saml, it's necessary to install some dependencies. On Ubuntu, do the following:
    - `sudo apt-get install libxml2-dev libxmlsec1-dev libxmlsec1-openssl`
    - To get the latest version of LibXML2, I also had to the following:
    ```
    sudo apt-get install build-essential
    sudo apt-get install python3-dev
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
   - Alternately, to test with SSO, you'll need to list on port 443. To use gunicorn and nginx, do the following:
        1. Create SSL key and cert (either self-signed or using a certificate authority)
        2. Install gunicorn: `pip install gunicorn`
        3. Install nginx: `sudo apt-get install nginx`
        4. Remove the defaul SSL configuration: 
         ```cd /etc/nginx/sites-enabled`
            sudo rm default
            ```
        5. Create a new nginx configuration to proxy to the Flask as follows:
            ```
            server {
                listen 80;
                listen [::]:80;
                server_name gworcid-dev.wrlc.org;
                return 302 https://$server_name$request_uri;
             }
            server {
                listen 443 ssl;
                listen [::]:443 ssl;
                ssl_certificate /etc/ssl/certs/server.crt;
                ssl_certificate_key /etc/ssl/private/server.key;
                location / {
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header HOST $http_host;
                    proxy_pass http://127.0.0.1:8080;
                    proxy_redirect off;
                 }
            }```
        6. From the command line, run `gunicorn -b 127.0.0.1:8080 orcidflask:app`

