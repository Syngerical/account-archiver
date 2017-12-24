import json
import re
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    # checks preconditions if we can actually delete the account from es database
    if(check_params(event) == False):
        message = {"message":"Error: Account cannot be found"}
        return json.dumps(message)
    # deletes account/profile from the database
    return delete_profile(event)

# holds fields that must be present in event parameters
requiredFields = ["address", "password"]

# checks preconditions for deletion
def check_params(event):
    # gets elastic search object
    es = get_ES()
    # checks that all required fields from validFields are present
    for field in requiredFields:
        if (not field in event or event[field] == ""):
            return False
    # checks that the address is a legitimate address
    if(not is_address(event["address"])):
        return False
    # checks if password is correct
    if(not correct_password(event, es)):
        return False
    # passed all parameter checks, return true
    return True

# determines if given address follows valid address format
def is_address(address):
    return re.search("\w+@\w+\.\w+", address)

# deletes the actual account/profile
def delete_profile(event):
    # gets elastic search object
    es = get_ES()
    # deletes profile
    es.delete(index="accounts", doc_type="account", id=event.get("address"))
    # message to return
    message = {"message": "Successfully deleted profile"}
    return json.dumps(message)

# checks if corresponding password is correct
def correct_password(event, es):
    try:
        # retrieve profile using the address as id
        profile = es.get(index="accounts", doc_type="account", id=event.get("address"))
        # extract password from profile
        pw = profile.get("_source").get("password")
        # checks if paswword from parameter matches password from es database
        return event.get("password") == pw
    # throw exception if profile doesn't exist
    except Exception:
        return False

# returns elastic search object allowing for access to database
def get_ES():
    AWS_ACCESS_KEY = 'your_aws_access_key'
    AWS_SECRET_KEY = 'your_aws_secret_key'
    region = 'your_region'
    service = 'es'
    
    awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, service)
    # endpoint for elastic search domain
    host = 'your_elastic_search_domain'
    
    # creates elastic search object
    es = Elasticsearch(
                       hosts = [{'host': host, 'port': 443}],
                       http_auth = awsauth,
                       use_ssl = True,
                       verify_certs = True,
                       connection_class = RequestsHttpConnection
                       )
    return es
