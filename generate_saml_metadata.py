import os
from onelogin.saml2.settings import OneLogin_Saml2_Settings

saml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orcidflask/saml')

def get_metadata():
    settings = OneLogin_Saml2_Settings(custom_base_path=saml_path)
    metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(metadata)
    if len(errors) == 0:
        return metadata
    else:
        print(errors)

def save_metadata():
    metadata = get_metadata()
    if metadata:
        with open(saml_path + '/orcid-integration-metadata.xml', 'wb') as f:
            f.write(metadata)

if __name__ == '__main__':
    save_metadata()