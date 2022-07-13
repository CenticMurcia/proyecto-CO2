# Run the application (as long as is named app.py) with:
# $ flask run 

import requests
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
import os
import numpy as np

app = Flask(__name__)


#################################### READ HOPU DATA

def get_datetime():
    # datetime object containing current date and time
    # dd/mm/YY H:M:S
    global dt
    dt = datetime.now().strftime("%d/%m/%Y,%H:%M:%S")


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

def get_CO2_msg(pred_CO2_20mins):

    start_msg = "PREDICCIÓN DE CO2 EN NIVEL "
    advice_1  = " (IDA 1). NINGUNA ACCIÓN REQUERIDA."
    advice_2  = " (IDA 2). SE RECOMIENDA VENTILAR LA OFICINA EN LOS PRÓXIMOS 15 MINUTOS"
    advice_3  = " (IDA 3). SE DEBE VENTILAR LA OFICINA EN ESTE MOMENTO"

    if   pred_CO2_20mins < 500:                             return start_msg + "OPTIMO"        + advice_1
    elif pred_CO2_20mins >= 500 and pred_CO2_20mins < 900:  return start_msg + "BUENO"         + advice_1
    elif pred_CO2_20mins >= 900 and pred_CO2_20mins < 1200: return start_msg + "ACEPTABLE"     + advice_2
    elif pred_CO2_20mins >= 1200:                           return start_msg + "DESACONSEJADO" + advice_3

def get_PM10_msg(pred_PM10_20mins):

    start_msg = "PREDICCIÓN DE PARTÍCULAS EN SUSPENSIÓN INFERIORES A 10 MICRAS EN NIVEL "
    advice_1  = ". NINGUNA ACCIÓN REQUERIDA."
    advice_2  = ". CESEN CUALQUIER POSIBLE ACTIVIDAD GENERADORA DE POLVO EN LOS PRÓXIMOS 15 MINUTOS. REVISEN EL SISTEMA DE CLIMATIZACIÓN Y VENTILACIÓN EN LAS PRÓXIMAS 48 HORAS"
    advice_3  = ". CESEN CUALQUIER POSIBLE ACTIVIDAD GENERADORA DE POLVO EN ESTE MOMENTO. REVISEN EL SISTEMA DE CLIMATIZACIÓN Y VENTILACIÓN EN LAS PRÓXIMAS 24 HORAS"

    if   pred_PM10_20mins < 20:                            return start_msg + "OPTIMO"        + advice_1
    elif pred_PM10_20mins >= 20 and pred_PM10_20mins < 40: return start_msg + "BUENO"         + advice_1
    elif pred_PM10_20mins >= 40 and pred_PM10_20mins < 60: return start_msg + "ACEPTABLE"     + advice_2
    elif pred_PM10_20mins >= 60:                           return start_msg + "DESACONSEJADO" + advice_3


def get_PM25_msg(pred_PM25_20mins):

    start_msg = "PREDICCIÓN DE PARTÍCULAS EN SUSPENSIÓN INFERIORES A 2,5 MICRAS EN NIVEL "
    advice_1  = ". NINGUNA ACCIÓN REQUERIDA."
    advice_2  = ". CESEN CUALQUIER POSIBLE ACTIVIDAD GENERADORA DE POLVO EN LOS PRÓXIMOS 15 MINUTOS. REVISEN EL SISTEMA DE CLIMATIZACIÓN Y VENTILACIÓN EN LAS PRÓXIMAS 48 HORAS"
    advice_3  = ". CESEN CUALQUIER POSIBLE ACTIVIDAD GENERADORA DE POLVO EN ESTE MOMENTO. REVISEN EL SISTEMA DE CLIMATIZACIÓN Y VENTILACIÓN EN LAS PRÓXIMAS 24 HORAS"

    if   pred_PM25_20mins < 20:                            return start_msg + "OPTIMO"        + advice_1
    elif pred_PM25_20mins >= 20 and pred_PM25_20mins < 40: return start_msg + "BUENO"         + advice_1
    elif pred_PM25_20mins >= 40 and pred_PM25_20mins < 60: return start_msg + "ACEPTABLE"     + advice_2
    elif pred_PM25_20mins >= 60:                           return start_msg + "DESACONSEJADO" + advice_3



def get_ml_predictions():

    global CO2_list, PM10_list, PM25_list

    input_data_df = pd.read_csv("data.csv")

    if len(input_data_df) >= 4:

        #### ENOUGH DATA -> DO PREDICTION
        print("doing ml prediction")

        # get tail(4) that means lag15, lag10, lag5, actual 
        in_dat = input_data_df.tail(4)

        temp_hist = in_dat["Temperatura"].values # [temp_lag15, temp_lag10, temp_lag5, temp_actual] 
        hume_hist = in_dat["Humedad"].values
        pm25_hist = in_dat["PM25"].values
        pm10_hist = in_dat["PM10"].values
        CO2_hist  = in_dat["CO2"].values
        pers_hist = in_dat["Personas"].values

        # Prepare flat numpy matrix for the sklearn prediction
        test_x = np.concatenate((temp_hist,
                                 hume_hist,
                                 pm25_hist,
                                 pm10_hist,
                                 CO2_hist,
                                 pers_hist)).reshape(1,-1)

        # DO sklearn prediction
        pred_np = np.array([[  1.5137,   1.8456,   1.887 ,   2.5185,   2.5037,   2.8493,
                               2.9192,   3.412 , 760.1504, 766.1264, 779.5188, 755.173 ]])[0]

        PM25_list = list(pm25_hist) + list(pred_np[0:4])
        PM10_list = list(pm10_hist) + list(pred_np[4:8])
        CO2_list  = list(CO2_hist)  + list(pred_np[8:12])

    else:
        #### NO ENOUGH DATA -> ERROR MSG
        print("NO ENOUGH DATA")
        PM25_list = [-1]*8
        PM10_list = [-1]*8
        CO2_list  = [-1]*8



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
    get_ml_predictions()



@app.route('/')
def web_endpoint():
    data={
        "x_labels":   ["-15 mins", "-10 mins", "-5 mins", "Actual", "+5 mins", "+10 mins", "+15 mins", "+20 mins"],
        "CO2":        CO2_list, #[120, 153, 213, 230, 240, 220, 180, 120],
        "CO2_msg":    get_CO2_msg(CO2_list[-1]),
        "PM10":       PM10_list, #[8, 10, 20, 26, 27, 22, 13, 11],
        "PM10_msg":   get_PM10_msg(PM10_list[-1]),
        "PM25":       PM25_list, #[6, 8, 18, 23, 24, 18, 10, 8],
        "PM25_msg":   get_PM25_msg(PM25_list[-1])
    }
    return render_template('frontend.html', **data)


if __name__ == '__main__':

    init_data()
    
    #scheduler = BackgroundScheduler(timezone='Europe/Madrid') # Default timezone is "utc"
    #scheduler.add_job(pipeline, 'cron', day_of_week='mon-fri', hour='7-20', minute='*/5')
    #scheduler.start()

    port = os.getenv('PORT') # Port is given by Heroku as env variable
    print("Port:", port)

    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)

