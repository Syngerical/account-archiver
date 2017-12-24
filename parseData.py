import re
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# does actual indexing of a specific account to the elastic search database
def indexAccount(email_address, email_username, email_domain, password, es):
    document = {
        "address": email_address,
        "username": email_username,
        "domain": email_domain,
        "password": password
    }
    es.index(index="accounts", doc_type="account", id=email_address, body=document)

# extracts every line from the given file
def extractLines():
    # reads in file
    file = open("stuff.txt")
    # stores info as list of lines of strings
    lines = file.readlines()
    file.close()
    return lines

# goes through the information in the file and parses out usernames/passwords/emails
def parseData(lines, es):
    # regex pattern for emails
    emailPattern = "\w+@\w+\.\w+"
    # regex pattern for passwords
    passPattern = "Password:"
    # determines if email was valid, so we would need to check for password too
    checkPass = False
    # holds position in lines during while loop
    index = 0
    
    # continues looping as long as there are more lines from the file
    while index < len(lines) - 1:
        # strip extra white space
        line = lines[index].strip()
        # splits line into individual words and iterate through each word
        words = line.split(" ")
        for word in words:
            # if the word is an email, have to check for password now
            if(re.search(emailPattern, word)):
                checkPass = True
                break
    
        # increment index for while loop
        index += 1
        
        # see if need to check for the password too
        if(checkPass):
            # holds the next line and strips of extra white space
            line2 = lines[index].strip()
            # appends to the metadata lists at corresponding positions if this line has a password
            # re.I makes the regex case insensitive
            if(re.search(passPattern, line2, re.I)):
                # pieces together the account information and calls indexAccount to add to database
                password = (line2[line2.index(":") + 1:])
                address = (word)
                username = (word[0:word.index("@")])
                domain = (word[word.index("@") + 1:])
                indexAccount(address, username, domain, password, es)
                # can skip next line now
                index += 1
            # reset checkPass
            checkPass = False

def main():
    # creates elastic search object
    AWS_ACCESS_KEY = 'your_aws_access_key'
    AWS_SECRET_KEY = 'your_aws_secret_key'
    region = 'your_region'
    service = 'es'
    
    awsauth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, region, service)
    
    host = 'your_elastic_search_domain'
    
    es = Elasticsearch(
                       hosts = [{'host': host, 'port': 443}],
                       http_auth = awsauth,
                       use_ssl = True,
                       verify_certs = True,
                       connection_class = RequestsHttpConnection
                       )
    
    # holds the lines of data extracted from the file
    lines = extractLines()
    # parses the data in lines and indexes the data if it is valid
    parseData(lines, es)

if __name__ == '__main__':
    main()
