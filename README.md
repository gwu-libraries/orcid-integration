# orcid-integration
ORCID middleware to enable our researchers to designate GW as a trusted partner

## Setup 

1. Create your secure key and certificate for SAML encryption/decryption: `openssl req -new -x509 -days 3652 -nodes -out sp.crt -keyout sp.key`
   - These files should go into an `orcidflask/saml/certs` directory.
2. In the `orcidflask/saml` directory, create a `settings.json` file to provide the metadata for your app and your identity provider, as well as the certificate from your identify provider. You can follow the example on the [python3-saml repository](https://github.com/onelogin/python3-saml) or in `example-settings.json`.
3. Copy the example Flask configuration file and edit it to provide sensitive keys, including the SERVER_KEY, ORCID client ID and ORCID client secret. The `SERVER_KEY` should be the key used to encrypt the Flask session objects, as described [here](https://flask.palletsprojects.com/en/2.2.x/config/).
 `cp example.config.py config.py`
4. Copy `example.docker-compose.yml` to `docker-compose.yml` and `example.env` to `.env`. 
5. Add the hostname of your server to the `VIRTUAL_HOST` environment variable in `.env`.
  - If using SSL, see the additional instructions below for configuring the Nginx Docker container.
  - If not using SSL, comment out the volume mapping in the `docker-compose.yml` file under the `nginx-proxy` service. 
6. Bring up the Docker container(s): `docker-compose up -d`. This will install all necessary dependencies and launch the Flask app with gunicorn on port `8080`, and it will start an Nginx server to proxy port `8080` to `80`/`443`.
  - For development, comment out the first three lines under the `volumes` section of the `flask-app` service and uncomment the line `.:/opt/orcid-integration`. This will use the local copy of the Python code.
6. When the Flask app starts up, it will check for the presence of a database encryption key file (as specified in `example.env`). If the file is not present, it will create a new database encryption key. **Be careful with this key.** Once the data has been encrypted using it, the key is necessary to decrypt the data again. Loss of the key means loss of the data.
7. The postgres container will store data outside of the container, in the `./data` directory.
    - When first run, postgres will set the permissions on this directory to a system user.
    - To avoid having the reset permissions on `./data` every time you start up the container, **after starting the container the first time**, modify the `db` service in `docker-compose.yml` to include the following line (where `UID` and `GID` are the system ID's of the user and group to which you want to assign ownership of the `./data` directory):
     ```
     user: "UID:GID"
     ```
    - To setup the database, run the migrations: 
        ```
        docker exec -it orcid-integration-flask-app-1 /bin/bash
        flask db upgrade
        ```
8. If you need to provide an XML file to your SAML IdP, with the `flask-app` container running, do the following:
    ```
    docker exec -it orcid-integration-flask-app-1 /bin/bash
    python generate_saml_metadata.py
    ```
    The SAML metadata file should be written to the `orcidflask/saml` directory (bind-mounted outside the container).

### SSL with Nginx proxy

    1. Create SSL key and cert (either self-signed or using a certificate authority)
    2. Follow the name conventions in the [nginx-proxy documentation](https://github.com/nginx-proxy/nginx-proxy/tree/main/docs#ssl-support), ensuring that the key and certificate files are placed in the same directory, which should be mapped to the `/etc/nginx/certs` directory in the `docker-compose.yml` file.

### Serializing the database

To quickly serialize the database as a JSON file, you can run the following commands (if outside the container):
    ```
    docker exec -it orcid-integration-flask-app-1 flask serialize-db /tmp/token-dump.json

    docker cp orcid-integration-flask-app-1:/tmp/token-dump.json ./
    ```