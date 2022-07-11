# Run the application (as long as is named app.py) with:
# $ flask run 

import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime


app = Flask(__name__)


#################################### READ HOPU DATA

# 1. Iniciar sesion en el APIRest de Hopu
#    Obtener access token y refress token

def API_get_token():
    url     = "https://fiware.hopu.eu/keycloak/auth/realms/fiware-server/protocol/openid-connect/token" 
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data    = "username=julgonzalez&password=vZnAWE7FexwgEqwT&grant_type=password&client_id=fiware-login"
    response = requests.post(url, data = data, headers = headers).json()

    global access_token, refresh_token

    access_token  = response["access_token"]
    refresh_token = response["refresh_token"]


def API_get_device_status(access_token):

    url     = "https://fiware.hopu.eu/orion/v2/entities?limit=1000&attrs=*,dateModified&options=count,keyValues" 
    headers = {"fiware-service": "Device", "fiware-servicepath": "/ctcon", "Authorization": "Bearer "+access_token}
    response = requests.get(url, headers = headers).json()[0]

    global operationalStatus

    operationalStatus = response["operationalStatus"]


def API_get_calidad_aire(access_token):

    url     = "https://fiware.hopu.eu/orion/v2/entities?limit=1000&attrs=*,dateModified&options=keyValues" 
    headers = {"fiware-service": "AirQuality", "fiware-servicepath": "/ctcon", "Authorization": "Bearer "+access_token}
    response = requests.get(url, headers = headers).json()[0]

    global CO2,PM10,PM25,Temperatura,Humedad    

    CO2         = response["CO2"]
    PM10        = response["PM10"]
    PM25        = response["PM25"]
    Temperatura = response["temperature"]
    Humedad     = response["humidity"]



def API_get_presencia(access_token):

    url     = "https://fiware.hopu.eu/orion/v2/entities?limit=1000&attrs=*,dateModified&options=count,keyValues" 
    headers = {"fiware-service": "PeopleCounting", "fiware-servicepath": "/ctcon", "Authorization": "Bearer "+access_token}
    response = requests.get(url, headers = headers).json()[0]

    global PersonasIn,PersonasOut,Personas

    PersonasIn  = response["numberOfIncoming"]
    PersonasOut = response["numberOfOutgoing"]
    Personas    = PersonasIn - PersonasOut



####################################

def get_datetime():
    # datetime object containing current date and time
    # dd/mm/YY H:M:S
    global dt
    dt = datetime.now().strftime("%d/%m/%Y,%H:%M:%S")

####################################


def init_data():
    f = open("data.csv", "w")
    f.write("Fecha,Hora,PersonasIn,PersonasOut,Personas,Temperatura,Humedad,CO2,PM10,PM25\n")
    f.close()

def save_data():
    f = open('data.csv', 'a')
    f.write(dt+","+
            str(PersonasIn)+","+
            str(PersonasOut)+","+
            str(Personas)+","+
            str(Temperatura)+","+
            str(Humedad)+","+
            str(CO2)+","+
            str(PM10)+","+
            str(PM25)+"\n")
    f.close()

def print_data():
    print("   PersonasIn  = ", PersonasIn)
    print("   PersonasOut = ", PersonasOut)
    print("   Personas    = ", Personas)
    print("   Temperatura = ", Temperatura)
    print("   Humedad     = ", Humedad)
    print("   CO2         = ", CO2)
    print("   PM10        = ", PM10)
    print("   PM25        = ", PM25)


####################################

def pipeline():

    get_datetime()
    print("pipeline at " + dt)

    API_get_token()
    API_get_device_status(access_token)
    API_get_calidad_aire(access_token)    
    API_get_presencia(access_token)
    print_data()
    save_data()



@app.route('/')
def route():
    return 'flask'



if __name__ == '__main__':

    init_data()
    
    scheduler = BackgroundScheduler(timezone='Europe/Madrid') # Default timezone is "utc"
    #scheduler.add_job(pipeline, 'interval', seconds=6)
    scheduler.add_job(pipeline, 'cron', day_of_week='mon-fri', hour='7-20', minute='*/5')
    #scheduler.add_job(pipeline, 'cron', day_of_week='1-5', hour='7-20', minute='1,31')
    #scheduler.add_job(func=pipeline, trigger=CronTrigger.from_crontab("0 16 * * *"))
    scheduler.start()

    app.run(debug=True, use_reloader=False)

