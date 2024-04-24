# orcid-integration
ORCID middleware to enable our researchers to designate GW as a trusted partner

## Setup 

1. Create your secure key and certificate for SAML encryption/decryption: `openssl req -new -x509 -days 3652 -nodes -out sp.crt -keyout sp.key`
   - These files should go into an `orcidflask/saml/certs` directory.
2. In the `orcidflask/saml` directory, create a `settings.json` file to provide the metadata for your app and your identity provider, as well as the certificate from your identify provider. You can follow the example on the [python3-saml repository](https://github.com/onelogin/python3-saml) or in `example-settings.json`.
3. Copy the example Flask configuration file and edit it to provide sensitive keys, including the SERVER_KEY, ORCID client ID and ORCID client secret. The `SERVER_KEY` should be the key used to encrypt the Flask session objects, as described [here](https://flask.palletsprojects.com/en/2.2.x/config/).
 `cp example.config.py config.py`
4. Copy `example.docker-compose.yml` to `docker-compose.yml` and `example.env` to `.env`. 
5. Bring up the Docker container(s): `docker-compose up -d`. This will install all necessary dependencies and launch the Flask app with gunicorn on port `8080`. For development, comment out the first three lines under the `volumes` section of the `flask-app` service and uncomment the line `.:/opt/orcid_integration`. This will use the local copy of the Python code.
6. When the Flask app starts up, it will check for the presence of a database encryption key file (as specified in `example.env`). If the file is not present, it will create a new database encryption key. **Be careful with this key.** Once the data has been encrypted using it, the key is necessary to decrypt the data again. Loss of the key means loss of the data.
7. The postgres container will store data outside of the container, in the `./data` directory.
    - When first run, postgres will set the permissions on this directory to a system user.
    - To avoid having the reset permissions on `./data` every time you start up the container, **after starting the container the first time**, modify the `db` service in `docker-compose.yml` to include the following line (where `UID` and `GID` are the system ID's of the user and group to which you want to assign ownership of the `./data` directory):
     ```
     user: "UID:GID"
     ```
8. If you need to provide an XML file to your SAML IdP, with the `flask-app` container running, do the following:
    ```
    docker exec -it orcid-integration-flask-app-1 /bin/bash
    python generate_saml_metadata.py
    ```
    The SAML metadata file should be written to the `orcidflask/saml` directory (bind-mounted outside the container).
9. For SSL, use gunicorn with nginx:
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
10. To quickly serialize the database as a JSON file, you can run the following command (if outside the container), providing the path to a file in a mounted volume:
    ```
    docker exec -it orcid-integration_flask-app_1 flask serialize-db ./data/token-dump.json
    ```