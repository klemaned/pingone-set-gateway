# About

## Use Case
After migrating to PingOne Cloud from Ping Federate + PingID, the imported Active Directory users from PingID cannot authenticate as there is no way to associate them to the PingOne Cloud LDAP Gateway. You must set the Gateway ID, User Type ID, and Correlation Attributes via the API to manually associate the user accounts with the LDAP Gateway.

## What does it do?
`pingone-set-gateway.py` will:
1. Collect the user accounts from a provided PingOne Cloud environment.
2. Compare the PingOne user accounts to a CSV of user accounts and their attributes pulled from Active Directory.
3. If a match is found, set the users Gateway, User Type, and Correlation Attributes. The Correlation Attributes are gathered from the CSV.

# Prerequisites

## PingOne configuration
This assumes you've already created your PingOne Cloud environment and established an integration to your existing PingID environment.
## Gateway
You will need to create an LDAP Gateway and User Type (Lookup) to identify the values to set for the gateway and user_type values to set in the script.
## Authentication Token
Link to Ping Identity's documention: https://docs.pingidentity.com/r/en-us/pingone/pingonemfa_creating_worker_application_access_token

Summary of Steps:
1. Create a new Application with the "Worker" Application Type.
2. Under the Application Roles assign the "Identity Data Admin" role.
3. On the Application's Configuration tab, at the bottom of the page, click the "Get Access Token" button to retrieve your temporary access token. Note that Access Tokens expire after 1 hour.
## Active Directory Users CSV
The scripts depends on a CSV of Active Directory user attributes to set the PingOne user Correlation Attributes. To create a CSV with the properties used in this script, execute the following powershell command from a Domain Controller or other domain joined system with the Active Directory Powershell module installed.
`get-aduser -filter * -Properties * | select objectGUID, objectSid, DistinguishedName, sAMAccountName, mail, UserPrincipalName | Export-Csv -Path 'ad_users.csv'`

## Disclaimer
This software is provided "as is" and without warranty of any kind. Use at your own risk.

