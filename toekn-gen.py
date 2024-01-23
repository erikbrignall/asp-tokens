import requests
import pandas as pd
from datetime import datetime
import json
import streamlit as st
import hmac

st.header('Alexa Smart Properties Campaign tools')

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


############################
# FETCH UP TO DATE API TOKEN 
url = "https://api.amazon.com/auth/o2/token"

rtoken = st.secrets["rtoken"]
client_id = st.secrets["client_id"]
client_secret =  st.secrets["client_secret"]


body = {
        "refresh_token": f"{rtoken}",
        "client_id":f"{client_id}",
        "client_secret":f"{client_secret}",
        "grant_type":"refresh_token"
        }

#st.write(body)

try:
    response = requests.post(url, json=body)

    # Checking if the request was successful
    if response.status_code == 200:
        #st.write("Request successful!")
        #print(response.text)
        #st.write("token is:")
        data = json.loads(response.text)
        lwa_token = data['access_token']
        #st.write(lwa_token)
    else:
        st.write("Request failed with status code:", response.status_code)
        st.stop()
except:
    st.write("well that didn't work hmmm")
    st.stop()


########################
# PAGE BODY - LIST CURRENT CAMPAIGNS IN TABLE
st.header('Current campaigns')

# GET ALL CAMPAIGNS
url = "https://api.eu.amazonalexa.com/v1/proactive/campaigns"

headers = {
    "Host": "api.eu.amazonalexa.com",
    "Accept": "application/json",
    "Authorization": f"Bearer {lwa_token}"
}

#Making the GET request
response = requests.get(url, headers=headers)

# Checking if the request was successful
if response.status_code == 200:
    st.write("Here are the latest campaigns")
else:
    st.write("Campaign list Request failed with status code:", response.status_code)

parsed_json = json.loads(response.text)

## CREATE A FUNCTION TO CREATE A TABLE OF ALL CORE FUNCTION INFORMATION
# List to store flattened data
flattened_data = []


# Iterate through the JSON to extract relevant data
for item in parsed_json['results']:
    campaign_id = item['campaignId']
    for variant in item['suggestion']['variants']:
        # There might be multiple content values in each variant
        for content_value in variant['content']['values']:
            locale = content_value['locale']
            body = content_value['datasources']['displayText']['body']
            title = content_value['datasources']['displayText']['title']
            img = content_value['datasources']['background']['backgroundImageSource']
            
            # Append the extracted data to the list
            flattened_data.append({
                'campaignId': campaign_id,
                'locale': locale,
                'body': body,
                'title': title,
                'img': img
            })

# Create DataFrame of campaign data
dfCampaigns = pd.DataFrame(flattened_data)

# Display the DataFrame
st.dataframe(dfCampaigns)

######################
# DELETE A CAMPAIGN
def delete_campaign(cid):
    # Here you would add your code to delete the campaign
    url = "https://api.eu.amazonalexa.com/v1/proactive/campaigns/" + cid
    st.write(url)
    headers = {
        "Host": "api.eu.amazonalexa.com",
        "Accept": "application/json",
        "Authorization": f"Bearer {lwa_token}"
    }
    
    #Making the GET request
    response = requests.delete(url, headers=headers)
    
    # Checking if the request was successful
    if response.status_code == 202:
        st.success(f"Campaign with ID {cid} has been deleted.")
    else:
        st.write("Request failed with status code:", response.status_code)
        
st.header('Delete a campaign')
campaign_id = st.text_input("Enter the ID of the campaign to delete:")
if campaign_id:
    delete_campaign(campaign_id)

########################
# ADD A CAMPAIGN

# PAGE HEADINGS AND FILE UPLOAD FOR LOADING CAMPAIGNS
#st.write('Please upload the unit ids')
#st.text('Note: this should be formatted as follows:)