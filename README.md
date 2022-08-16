# orcid-integration
ORCID middleware to enable our researchers to designate GW as a trusted partner

## Setup 

1. Create your secure key and certificate for SAML encryption/decryption: `openssl req -new -x509 -days 3652 -nodes -out sp.crt -keyout sp.key`
   - These files should go into an `orcidflask/saml/certs` directory.
2. In the `orcidflask/saml` directory, create a `settings.json` file to provide the metadata for your app and your identity provider, as well as the certificate from your identify provider. You can follow the example on the [python3-saml repository](https://github.com/onelogin/python3-saml) or in `example-settings.json`.
3. Copy the example Flask configuration file and edit it to provide sensitive keys, including the SERVER_KEY, ORCID client ID and ORCID client secret. 
 `cp example.config.py config.py`
4. Ensure that the `data` directory and subcontents have permissions as `755`; `sudo chmod` if needed.
5. Bring up the Docker container(s): `docker-compose up -d`. This will install all necessary dependencies and launch the Flask app with gunicorn on port `8080`. For development, comment out the first three lines under the `volumes` section of the `flask-app` service and uncomment the line `.:/opt/orcid_integration`. This will use the local copy of the Python code.
6. For SSL, use gunicorn with nginx:
        1. Create SSL key and cert (either self-signed or using a certificate authority)
        2. Install nginx: `sudo apt-get install nginx`
        3. Remove the defaul SSL configuration: 
         `cd /etc/nginx/sites-enabled`
        `sudo rm default`
        4. Create a new nginx configuration to proxy to the Flask app as follows:
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
