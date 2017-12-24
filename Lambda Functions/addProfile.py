import json
import re
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def lambda_handler(event, context):
    # checks preconditions if we can add based on parameters given
    if(check_params(event) == False):
        message = {"message": "Error: Invalid input"}
        return json.dumps(message)
    # adds account/profile to the database
    return add_profile(event)

# holds fields that must be present in event parameters
requiredFields = ["address", "password"]

# checks preconditions for adding an account/profile
def check_params(event):
    # checks that all required fields from validFields are present
    for field in requiredFields:
        if (not field in event or event[field] == ""):
            return False
    # checks that the address is a legitimate address
    if(not is_address(event["address"])):
        return False
    # passed all parameter checks, return true
    return True

# determines if address follows valid address format
def is_address(address):
    return re.search("\w+@\w+\.\w+", address)

# adds account/profile to ES database
def add_profile(event):
    # gets elastic search object
    es = get_ES()
    # gets query information
    doc_info = get_document_info(event)
    # body to be added
    document ={
        "address": doc_info["address"],
        "username": doc_info["username"],
        "domain": doc_info["domain"],
        "password": doc_info["password"]
    }
    
    # adds information to database
    es.index(index="accounts", doc_type="account", body=document, id = doc_info["address"])
    # message to return
    message = {"message": "Added successfully"}
    return json.dumps(message)

# returns relevant fields to be added to database based on user input
def get_document_info(event):
    # holds relevant fields
    doc_info = {}
    # adds required fields from parameters
    for key, value in event.items():
        if key in requiredFields:
            doc_info[key] = value
    # uses address to add domain and username to doc_info
    address = doc_info["address"]
    doc_info["domain"] = address[address.index("@") + 1:]
    doc_info["username"] = address[0:address.index("@")]
    return doc_info

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
