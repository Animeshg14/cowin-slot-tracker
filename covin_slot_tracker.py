import os,argparse
import sys,time
import datetime
import requests,json
def getDate():
    """
    Function to get the current date

    Returns
    -------
    date : String
        Current date in DD-MM-YYYY format

    """
    current_time = datetime.datetime.now()
    day = current_time.day
    month = current_time.month
    year = current_time.year
    date = "{dd}-{mm}-{yyyy}".format(dd=day,mm=month,yyyy=year)
    return date

def pingCOWIN(date,district_id):
    """
    Function to ping the COWIN API to get the latest district wise details

    Parameters
    ----------
    date : String
    district_id : int
    
    Returns
    -------
    json

    """
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date}".format(district_id = district_id, date = date)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36' }
    response = requests.get(url,headers=headers)
    if(response.ok):
        return json.loads(response.text)
    else:
        if('application/json' in response.headers['Content-Type']):
            print("Unexpected response from cowin: "+response.text)
        else:
            print("Unexpected response from cowin")
        return {}

def checkAvailability(payload,age):
    """
    Function to check availability in the hospitals from the json response from the public API

    Parameters
    ----------
    payload : JSON

    Returns
    -------
    available_centers_str : String
        Available hospitals
    total_available_centers : Integer
        Counter for available hospitals

    """
    available_centers = set()
    unavailable_centers = set()
    available_centers_str = False
    total_available_centers  = 0
    
    if('centers' in payload.keys()):
       length = len(payload['centers'])       
       if(length>1):
            for i in range(0,length):
                sessions_len = len(payload['centers'][i]['sessions'])
                for j in range(0,sessions_len):
                    if(payload['centers'][i]['sessions'][j]['available_capacity']>0 and payload['centers'][i]['sessions'][j]['min_age_limit'] <= age):
                        available_centers.add(payload['centers'][i]['name'])
            available_centers_str =  ", ".join(available_centers)
            total_available_centers  = len(available_centers)
       elif(length ==0):
            print("Please check the District ID passed. No Center found!")

    return available_centers_str,total_available_centers


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--district", required=True,
    help="Add district code of your location",type=int)

    parser.add_argument("-a", "--age", 
    help="Add your age for retriving the vaccine slots of your agegroup, If not specified, Default of 45 is considered",
    type=int,default=45)
    
    args = parser.parse_args()
    
    '''
    We are accepting two arguments from command line.
    district Integer Required
    Age Integer Optional(Default of 45 is taken if age is not passed)
    While deploying in heroku, Configure Procfile accordingly for CL Args.

    my_secret parameter will contain the IFTTT token to be configured as environment variable.
    While deploying in Heroku, configure your personal IFTTT token as "IFTTT_TOKEN" in Settings -> Config Vars

    '''

    D_ID = args.district
    age=args.age
    my_secret=""
    my_secret = os.environ.get('IFTTT_TOKEN')
    if(not my_secret):
        raise Error("Error while loading the IFTTT token, Kindly configure 'IFTTT_TOKEN' as your environment variable")
    counter=0
    while(True):
        if(counter==0):
            headers = {'Content-Type': 'application/json',}
            data = {"value1": "Cowin Slot Retriver Started!"}
            print(data['value1'])
            data = json.dumps(data)
            response = requests.post('https://maker.ifttt.com/trigger/notify/with/key/{k}'.format(k=my_secret), headers=headers, data=data)
            counter+=1
        date = getDate()
        data1 = pingCOWIN(date,D_ID)
        counter+=1
        print("API Calls: "+str(counter-1))
        available, total_centers  = checkAvailability(data1,age)
        if (available):
            headers = {'Content-Type': 'application/json',}
            msg_body="Slots Available at {total} places. {available}".format(total = total_centers,available = available)
            data = {"value1": msg_body}
            print(data['value1'])
            data = json.dumps(data)
            response = requests.post('https://maker.ifttt.com/trigger/notify/with/key/{k}'.format(k=my_secret), headers=headers, data=data)
        time.sleep(300)
