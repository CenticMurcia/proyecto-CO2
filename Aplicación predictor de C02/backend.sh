

########################################### Overall schema
# 
# __CTCON CLIENT__       ___________CENTIC APP_____________       ______HOPU________
# |              |      |                                  |     |                  |
# | Tablet with  |<-----| frontend <- Internal  <- backend |<----| air quality API  |
# | web browser  |      |  script     data.json    script  |     | person count API |                   
# |______________|      |__________________________________|     |__________________|
# 


########################################### BACKEND SCRIPT
#             
#   backend.sh  -----------> data.json
# 
# Initial setup:
#   1. Get access token from the HOPU API endpoint
#   2. Get if the sensor device is available
#
# Pipeline:              
#   1. Read air quality data from HOPU API endpoint
#   2. Read person count data from HOPU API endpoint
#   3. Run the Machine learning model to forecast the future
#   4. Overwrite results on the data.json file
#
# This pipeline is run every 5 mins
# (this can be done with an infinite while loop with sleep 5*60)
# (or also can be done be setting a crontab job every 5 minutes)


########################################### FRONTEND SCRIPT
#
#   frontend.sh <-------- frontend.html <-------- data.json
#
#   Web server using netcat in a while loop
#   to display the content of frontend.html
#   
#   frontend.html is a template which reads the data from data.json
#
#   The frontend.html refresh iteself in the browser
#   every 60 seconds because it has in the <head> section:
#
#     <meta http-equiv="refresh" content="60">




function server_log {
     echo `date +"%D %T"` $1
}



#####################################################################

# 1. Iniciar sesion en el APIRest de Hopu
#    Obtener access token y refress token

function API_get_token {

     response=$(curl -s \
          -X POST \
          -H "Content-Type: application/x-www-form-urlencoded" \
          -d "username=julgonzalez&password=vZnAWE7FexwgEqwT&grant_type=password&client_id=fiware-login" \
          https://fiware.hopu.eu/keycloak/auth/realms/fiware-server/protocol/openid-connect/token )

     # This returns a dictionary like:
     #
     #{
     #	"access_token":"adsfadfadfadf",
     #    "expires_in":600,
     #    "refresh_expires_in":1800,
     #    "refresh_token":"adsfadfadfadf",
     #    "token_type":"bearer",
     #    "not-before-policy":0,
     #    "session_state":"7915c53a-1c1c-42c3-a952-f01432d79b87",
     #    "scope":"profile fiware-scope email"
     #}

     access_token=$(jq -r '.access_token' <<< "$response")
     refresh_token=$(jq -r '.refresh_token' <<< "$response")
}


#####################################################################

# 2. Obtener si el dispositivo esta operativo
#    operationalStatus == "DISCONNECTED" -> MAL
#    operationalStatus == "CONNECTED"    -> BIEN

function API_get_device_status {

     response=$(curl -s \
          -X GET \
          -H "fiware-service: Device" \
          -H "fiware-servicepath: /ctcon" \
          -H "Authorization: Bearer $access_token" \
          "https://fiware.hopu.eu/orion/v2/entities?limit=1000&attrs=*,dateModified&options=count,keyValues")

     # Esto develeve algo parecido a esto:
     #
     #[
     #  {
     #    "id": "urn:ngsi:Device:HOPac67b2cd450a",
     #    "type": "Device",
     #    "dataProvider": "www.hopu.eu",
     #    "location": {
     #      "type": "Point",
     #      "coordinates": [
     #        -1.2238365,
     #        38.0896306
     #      ]
     #    },
     #    "name": "Urdecom AQ2",
     #    "operationalStatus": "CONNECTED" ó "DISCONNECTED"
     #    "source": "www.hopu.eu",
     #    "dateModified": "2022-05-31T11:53:04.00Z"
     #  }
     #]

     status=$(jq -r '.[0].operationalStatus' <<< "$response")
}


#####################################################################

# 3. Obtener datos de la calidad del aire:
#    PM2.5, PM10, CO2, humedad y temperatura

function API_get_calidad_aire {
     response=$(curl -s \
          -X GET \
          -H "fiware-service: AirQuality" \
          -H "fiware-servicepath: /ctcon" \
          -H "Authorization: Bearer $access_token" \
          "https://fiware.hopu.eu/orion/v2/entities?limit=1000&attrs=*,dateModified&options=keyValues")

     #[
     #  {
     #    "id": "urn:ngsi:AirQualityObserved:HOPac67b2cd450a",
     #    "type": "AirQualityObserved",
     #    "CO2": 1081.6625976,
     #    "PM10": 2,
     #    "PM25": 1,
     #    "TimeInstant": "2022-05-31T11:56:17.00Z",
     #    "dataProvider": "www.hopu.eu",
     #    "humidity": 40.1556434,
     #    "location": {
     #      "type": "Point",
     #      "coordinates": [
     #        -1.2238365,
     #        38.0896306
     #      ]
     #    },
     #    "name": "Urdecom AQ2",
     #    "operationalStatus": "CONNECTED",
     #    "particulates": [
     #      "PM10",
     #      "PM25"
     #    ],
     #    "pollutants": [
     #      "CO2"
     #    ],
     #    "source": "www.hopu.eu",
     #    "temperature": 23.7022209,
     #    "dateModified": "2022-05-31T11:56:17.00Z"
     #  }
     #]

     CO2=$(        jq -r '.[0].CO2' <<< "$response")
     PM10=$(       jq -r '.[0].PM10' <<< "$response")
     PM25=$(       jq -r '.[0].PM25' <<< "$response")
     temperature=$(jq -r '.[0].temperature' <<< "$response")
     humidity=$(   jq -r '.[0].humidity' <<< "$response")
}







#####################################################################

# 4. Obtener datos del sensor de presencia:

function API_get_presencia {

     response=$(curl -s \
          -X GET \
          -H "fiware-service: PeopleCounting" \
          -H "fiware-servicepath: /ctcon" \
          -H "Authorization: Bearer $access_token" \
          "https://fiware.hopu.eu/orion/v2/entities?limit=1000&attrs=*,dateModified&options=count,keyValues")

     #[
     #  {
     #    "id": "TBEEb827eb7f2d37:Access",
     #    "type": "Access",
     #    "TimeInstant": "2022-05-31T11:57:22.00Z",
     #    "location": {
     #      "type": "Point",
     #      "coordinates": [
     #        -1.2240365,
     #        38.0894306
     #      ]
     #    },
     #    "name": "Terabee People Counting",
     #    "numberOfIncoming": 45,
     #    "numberOfOutgoing": 32,
     #    "resources": [
     #      "numberOfIncoming",
     #      "numberOfOutgoing"
     #    ],
     #    "dateModified": "2022-05-31T11:57:22.00Z"
     #  }
     #]

     Incoming=$(jq -r '.[0].numberOfIncoming' <<< "$response")
     Outgoing=$(jq -r '.[0].numberOfOutgoing' <<< "$response")
     Personas=$((Incoming-Outgoing))
}


function print_data {
     echo "DATOS CALIDAD DEL AIRE:"
     echo "  Temperatura: $temperature"
     echo "  Humedad:     $humidity"
     echo "  C02:         $CO2"
     echo "  PM10:        $PM10"
     echo "  PM25:        $PM25"
     echo ""
     echo "DATOS CONTEO PERSONAS:"
     echo "  Han entrado:      $Incoming"
     echo "  Han salido:       $Outgoing"
     echo "  entrado - salido: $Personas"
     echo ""
}


function step_save {
     C02_lag2=C02_lag1
     PM10_lag2=PM10_lag1
     PM25_lag2=PM25_lag1

     C02_lag1=C02
     PM10_lag1=PM10
     PM25_lag1=PM25
}



# Cada nueva fila se escribe a los 5 minutos
# Por tanto...
#    288 filas -> 1 dia
#    288 * 365 * 5 = 525600 filas -> 5 años
function save_historic_sensor_data {
     {
          echo "Fecha Tiempo PersonasIn PersonasOut Personas Temperatura Humedad C02 PM10 PM25" # Print the header 
          tail +2 data | tail -525599 # Remove first line (header) | and the keep the last 525600 rows of data
          echo "$(date +"%D %T") $Incoming $Outgoing $Personas $temperature $humidity $CO2 $PM10 $PM25" # Add the new last row
     } | column -t | sponge data
}


while read -r $Incoming $Outgoing $Personas $temperature $humidity $CO2 $PM10 $PM25
do
    echo "$a" "$b"
done < data | tail -3

function write_json {

     # var CO2_real  = [153, 213, 230];
     # var PM10_real = [10, 20, 26];
     # var PM25_real = [8, 18, 23];
     echo "var CO2_real  = $(tail -3 data | awk '{print $8}'  | jq -s -c '.');" >> data.js
     echo "var PM10_real = $(tail -3 data | awk '{print $9}'  | jq -s -c '.');" >> data.js
     echo "var PM25_real = $(tail -3 data | awk '{print $10}' | jq -s -c '.');" >> data.js

     echo "var CO2_pred  = [240, 220, 180, 120];" >> data.js
     echo "var PM10_pred = [27,   22,  13,  11];" >> data.js
     echo "var PM25_pred = [24,   18,  10,   8];" >> data.js
}



################################################# MAIN

API_get_token
API_get_device_status

if [[ "$status" == "DISCONNECTED" ]]; then
    server_log "[ERROR] El dispositivo está desconectado."
    exit 1
else
    server_log "[INFO]  El dispositivo se encuentra operativo."
fi

rm -f data # Remove data file
touch data # Create empty data file


while true
do
     API_get_calidad_aire
     API_get_presencia
     save_historic_sensor_data

     rm -f data.js

     lines_of_data=$(wc -l < data)
     if (( $lines_of_data > 3)); then
          echo "Haciendo predicciones..."
          #compute_ml_predictions
          write_json
     else
          echo "No hay suficientes datos para hacer predicciones"
     fi
     
     #print_data
     sleep 5
done



