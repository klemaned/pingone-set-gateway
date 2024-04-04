import requests
import csv
import json

# PingOne API Reference:
# https://apidocs.pingidentity.com/pingone/platform/v1/api/

# This script utilizes the User Identity Management APIs
# https://apidocs.pingidentity.com/pingone/platform/v1/api/#users


env = "<Environment ID>" # Pingone Environment ID. Found in "Settings > Environment Properties" of the PingOne Environment
gateway = "<Gateway ID>" # Pingone Gateway ID. This is NOT the Credential ID. You can find the Gateway ID and in the API section of the Gateway configuraiton.
user_type = "<User Type ID>" # Pingone Gateway User Type ID. The ID can be be found in the 
csv_users_file = "./ad_users.csv" # File path for CSV containing all Active Directory users and their user link correlation attributes 
token = "<token>" # Pingone Worker App Access Token
verbose = True # True = Verbose script output

def print_msg(msg_type,msg):
    # Keep output uniform
    if msg_type == "verbose" and verbose == True:
        msg_head = "[v]"
    elif msg_type == "info":
        msg_head = "[i]"
    elif msg_type == "error":
        msg_head = "[!]"
    elif msg_type == "success":
        msg_head = "[+]"
    else:
        return
    print(f"{msg_head}: {msg}")

def collect_users():
    # https://apidocs.pingidentity.com/pingone/platform/v1/api/#get-read-user-or-users
    # You can provide a filter to the URL to limit the user scope https://apidocs.pingidentity.com/pingone/platform/v1/api/#limiting-and-filtering-data

    url = f"https://api.pingone.com/v1/environments/{env}/users"
    headers = {"Authorization": f"Bearer {token}"}
    pingone_users=[]
    print_msg("info","Collecting Users from Pingone")
    while url:
        print_msg("verbose",f"Making request to {url}")
        status = None # Reset status
        response = requests.get(url, headers=headers) # Issue GET request to PingOne API to collect users
        status=response.status_code
        print_msg("verbose",f"Status code is {status}")
        if status == 200: # Append users to pingone_users if API request was successful
            response_json = response.json()
            try:
                url = response_json["_links"]["next"]["href"] # If _links.next.href is provided in the response, set url to _links.next.href to support results pagination.
            except:
                print_msg("verbose","End of results. Next URL not present.")
                url = None # If _links.next.href is not provided in the response, then that is the end of the user results. Set url to None to break from loop.
            for user in response_json["_embedded"]["users"]: # Iterate through each user provided in the results. Create a dictionary for each user that includes "id" and "username" and append it to the pingone_users list
                user_dict = {
                    "id"      : user["id"],
                    "username": user["username"]
                }
                pingone_users.append(user_dict)
            print_msg("verbose",f"All Users count is {len(pingone_users)}")

        else: # If API request was NOT successfull, terminate the script as there is not need to proceed without a list of users
            print_msg("error",f"{status} {response.text}")
            quit()
    print_msg("verbose",f"{len(pingone_users)} user IDs collected from Pingone")
    return pingone_users

def match_users(pingone_users):
    print_msg("info",f"Looking up users in {csv_users_file} and setting their gateway and correlation attributes if they match.")
    for pingone_user in pingone_users: # Loop through the users in the pingone_users List
        with open(csv_users_file, newline="") as csvfile: # Open File containing list of 
            csv_users = csv.DictReader(csvfile) # Read file as a CSV. Loads CSV as a Dictionary
            for csv_user in csv_users: # Loop through the users in the CSV File 
                # Check if the pingone_user username matches the sAMAccountName or UserPrincipalName of the CSV User 
                if csv_user["sAMAccountName"].lower() == pingone_user["username"].lower() or csv_user["UserPrincipalName"].lower() == pingone_user["username"].lower():
                    set_user_properties(pingone_user, csv_user) # Pass user details to set_user_properties() if a match is found
                    break

def set_user_properties(pingone_user, csv_user):
    # https://apidocs.pingidentity.com/pingone/platform/v1/api/#put-update-password-set

    url = f"https://api.pingone.com/v1/environments/{env}/users/{pingone_user['id']}/password" # Set specific user API url. Using the Set Password API as it can be used to update the gateway id and correlationAttributes.
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.pingidentity.password.setGateway+json"
    }
    print_msg("verbose",f"Making request to update {pingone_user['username']} ({pingone_user['id']})")
    print_msg("verbose",f"User URL set to {url}")

    # Construct user update Dictionary
    user_update_data = {
        "id": gateway,
        "userType": {
            "id": user_type
        },
        "correlationAttributes": { # Set the Active Directory attributes that can be used to link PingOne users to Active Directory users.
            "objectGUID" : csv_user['objectGUID'],
            "objectsid" : csv_user['objectSid'],
            "dn" : csv_user['DistinguishedName'],
            "sAMAccountName" : csv_user['sAMAccountName']
        }
    }
    json_data = json.dumps(user_update_data, indent=4) # Convert Dictionary to JSON format.

    ########## Comment out the remaining lines of this function to execute as a dry run. ##########
    response = requests.request("PUT",url, headers=headers, data=json_data) # Send PUT request to update user data
    print_msg("verbose",f"User update response code is {response.status_code}")
    if not response.status_code == 200: # Print the error message if the http response code is not 200 (Success)
        print(response.text.encode('utf8'))

# Collect usernames and ids from a PingOne environment
pingone_users=collect_users()
# Compare users to a csv pulled from Active Directory and update the corresponding PingOne account if found.
match_users(pingone_users)
