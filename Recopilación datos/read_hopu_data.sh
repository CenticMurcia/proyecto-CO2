

touch data.csv


### 1) GET TOKEN

curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "username=julgonzalez&password=vZnAWE7FexwgEqwT&grant_type=password&client_id=fiware-login" https://fiware.hopu.eu/keycloak/auth/realms/fiware-server/protocol/openid-connect/token

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



### 2) LOOP FOR GETTING DATA AND REFRESH TOKEN

loop {


	
}