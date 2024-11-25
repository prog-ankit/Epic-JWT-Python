from token_manager import get_access_token 
import requests 
import time
from datetime import datetime, timedelta
import os  
from dotenv import load_dotenv  
import json 
# Load environment variables from the .env file
load_dotenv()


def bulk_data_request():
    try:
        bulk_data_request_url = None  # Initialize to avoid UnboundLocalError
        
        # Retrieve access token
        access_token = get_access_token() 
        if not access_token:
            print(error_response('Error: Access Token not found.'))
            return
        
        
        base_url = os.getenv('BASE_URI')
        bulk_group_id = os.getenv('GROUP_ID')
        initial_sleep_time = 10
       
        # Initiate bulk data request
        bulk_data_request_url = initiate_bulk_data_request(base_url, bulk_group_id, access_token)
        if not bulk_data_request_url:
            print(error_response('Error: Bulk data kickoff request failed.'))
            return   
        
        # Wait for the bulk data to be ready
        bulk_data_response = check_bulk_data_status(bulk_data_request_url, access_token, initial_sleep_time)
        if not bulk_data_response or bulk_data_response.status_code != 200:
            print(error_response('Error: Bulk data request failed.'))
            return
        
        # Process encounters and retrieve patient data
        output = bulk_data_response.json().get('output', [])
        encounter_urls = [item['url'] for item in output if item['type'] == 'Encounter']
        print("Processing Encounters...")
        messages = process_encounters(encounter_urls, access_token, base_url)

        # Display messages or return if no activity is found
        if not messages:
            print('No activity in last 24 hours.')
            print(success_response('Done'))
            return

        print()
        print('-----------------------------------------------------------------------------------------------------------------')
        print('Activity in last 24 hours:')
        for message in messages:
            print(message)
        print()
    except Exception as e:
        print(f"Failed to retrieve: {e}")
    finally:
        # Ensure that bulk data request is deleted even in case of an early return or error
        if bulk_data_request_url:
            if not delete_bulk_data_request(bulk_data_request_url, access_token):
                return error_response('Error: Bulk data request deletion failed.')
            print(success_response('Done'))
            return
       


def initiate_bulk_data_request(base_url, bulk_group_id, access_token):
    """Initiates the bulk data request and returns the request URL if successful."""
    bulk_data_kickoff_url = f'{base_url}R4/Group/{bulk_group_id}/$export?_type=Encounter'
    print('Initiating bulk data request:', bulk_data_kickoff_url)
    
    response = requests.get(
        bulk_data_kickoff_url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/fhir+json',
            'Prefer': 'respond-async'
        }
    )

    if response.status_code != 202:
        print('Error: Bulk data kickoff request failed with status:', response.status_code)
        return None

    return response.headers.get('Content-Location')

def check_bulk_data_status(request_url, access_token, initial_sleep_time):
    """Checks the status of the bulk data request, retrying until it's complete."""
    print('Checking bulk data request URL:', request_url)
    time.sleep(initial_sleep_time)
    for _ in range(3):
        response = requests.get(request_url, headers={'Authorization': f'Bearer {access_token}'})
        print('Bulk data request status:', response.status_code)

        if response.status_code == 200:
            return response
        elif response.status_code == 202:
            time.sleep(10)
        elif response.status_code >= 400:
            return None

    return None

def process_encounters(encounter_urls, access_token, base_url):
    """Processes encounter data, fetches patient information, and returns formatted messages."""
    current_time = datetime.now()
    last_24_hours = current_time - timedelta(days=1)
    messages = []
    
    for url in encounter_urls:
        response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
        if response.status_code == 200:
            for line in response.text.splitlines():
                encounter = json.loads(line)
                if is_valid_encounter(encounter, last_24_hours):
                    message = build_encounter_message(encounter, base_url, access_token)
                    if message:
                        messages.append(message)

    return messages

def is_valid_encounter(encounter, last_24_hours):
    """Validates if the encounter activity happen within the last 24 hours."""
    period_end_str = encounter.get('period', {}).get('end')
    if not period_end_str:
        return False

    period_end = parse_datetime(period_end_str)
    return period_end and period_end < last_24_hours

def parse_datetime(datetime_str):
    """Parses a datetime string into a datetime object."""
    try:
        if 'T' in datetime_str:
            return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
        return datetime.strptime(datetime_str, '%Y-%m-%d')
    except ValueError:
        return None

def build_encounter_message(encounter, base_url, access_token):
    """Builds a message for an encounter by retrieving related patient information."""
    patient_id = encounter.get('subject', {}).get('reference')
    if not patient_id:
        return None

    patient_url = f'{base_url}R4/{patient_id}'
    try:
        patient_response = requests.get(
            patient_url,
            headers={'Authorization': f'Bearer {access_token}', 'Accept': 'application/fhir+json'},
            timeout=30
        )
        if patient_response.status_code == 200:
            patient = patient_response.json()
            return format_encounter_message(encounter, patient)
    except requests.exceptions.ConnectionError as e:
        print(f'Error: Connection error occurred while fetching patient data: {e}')
    return None

def format_encounter_message(encounter, patient):
    """Formats the encounter and patient details into a readable message."""
    return (
        '-----------------------------------------------------------------------------------------------------------------\n'
        f'Encounter ID: {encounter["id"]}\n'
        f'Status: {encounter["status"]}\n'
        f'Class: {encounter["class"]["code"]} - {encounter["class"]["display"]}\n'
        f'Period Start: {encounter["period"]["start"]}, End: {encounter["period"]["end"]}\n'
        f'Patient ID: {patient.get("id")}\n'
        f'Name: {patient.get("name", [{}])[0].get("text")}\n'
        f'DOB: {patient.get("birthDate")}\n'
        f'Gender: {patient.get("gender")}\n'
        '-----------------------------------------------------------------------------------------------------------------'
    )

def delete_bulk_data_request(request_url, access_token):
    """Deletes the bulk data request."""
    print('Deleting bulk data request:', request_url)
    response = requests.delete(
        request_url,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/fhir+json',
            'Prefer': 'respond-async'
        }
    )
    return response.status_code in (200, 202)

def error_response(message):
    """Returns a formatted error response."""
    return {
        'statusCode': 400,
        'body': message
    }

def success_response(message):
    """Returns a formatted success response."""
    return {
        'statusCode': 200,
        'body': message
    }
      

if __name__=="__main__":
    bulk_data_request()