# Hace la llamada a todas las APIs de Hopu para obtener los datos de calidad de aire y de presencia 






function server_log {
     echo `date +"%D %T"` $1
}



#####################################################################

# 1. Iniciar sesion en el APIRest de Hopu
#    Obtener access token y refress token

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


#####################################################################

# 2. Obtener si el dispositivo esta operativo
#    operationalStatus == "DISCONNECTED" -> MAL
#    operationalStatus == "CONNECTED"    -> BIEN

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

if [[ "$status" == "DISCONNECTED" ]]; then
    server_log "[ERROR] El dispositivo NO responde"
    exit 1
else
    server_log "[INFO]  El dispositivo se encuentra operativo"
fi

#####################################################################

# 3. Obtener datos de la calidad del aire:
#    PM2.5, PM10, CO2, humedad y temperatura

function get_calidad_aire {
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


function get_presencia {

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

function pipeline {
     get_calidad_aire
     get_presencia
     print_data
}

pipeline





### PUT IT IN A SERVER

#function server_response {
#     echo -e 'HTTP/1.1 200 OK\r\n'
#     pipeline
#}
#ncat -lk -p 8080 --exec $(server_response) # --listen --keep-open

