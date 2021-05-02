import os
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
    district_id : String
    
    Returns
    -------
    json

    """
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date}".format(district_id = district_id, date = date)
    response = requests.get(url)
    return json.loads(response.text)

def checkAvailability(payload):
    """
    Function to check availability in the hospitals from the json response from the public API

    Parameters
    ----------
    payload : JSON

    Returns
    -------
    available_centers_str : String
        Available hospitals
    unavailable_centers_str : String
        Unavailable hospitals

    """
    available_centers = set()
    unavailable_centers = set()
    available_centers_str = False
    unavailable_centers_str = False
    
    if('centers' in payload.keys()):
       length = len(payload['centers'])
       if(length>1):
            for i in range(0,length):
                sessions_len = len(payload['centers'][i]['sessions'])
                for j in range(0,sessions_len):
                    if(payload['centers'][i]['sessions'][j]['available_capacity']>0 and payload['centers'][i]['sessions'][j]['min_age_limit'] == 18):
                        available_centers.add(payload['centers'][i]['name'])
                    else:
                        unavailable_centers.add(payload['centers'][i]['name'])
            available_centers_str =  ", ".join(available_centers)
            unavailable_centers_str = ", ".join(unavailable_centers)
    
    return available_centers_str,unavailable_centers_str


if __name__=="__main__":
    D_ID = 230
    my_secret = os.environ.get('IFTTT_TOKEN')
    counter=0
    while(True):
        if(counter==0):
            headers = {'Content-Type': 'application/json',}
            data = {"value1": "Cowin Slot Retriver Started!"}
            data = json.dumps(data)
            print(data)
            response = requests.post('https://maker.ifttt.com/trigger/notify/with/key/{k}'.format(k=my_secret), headers=headers, data=data)
            counter+=1
            print("Counter now! "+str(counter))
        date = getDate()
        data1 = pingCOWIN(date,D_ID)
        counter+=1
        print("API Calls: "+str(counter-1))
        available, unavailable = checkAvailability(data1)
        if (len(available)>0):
            headers = {'Content-Type': 'application/json',}
            data = {"value1": "Slot Available: "+available}
            data = json.dumps(data)
            print(data)
            response = requests.post('https://maker.ifttt.com/trigger/notify/with/key/{k}'.format(k=my_secret), headers=headers, data=data)
        time.sleep(300)
