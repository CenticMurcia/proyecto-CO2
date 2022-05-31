package calidadAire.rest;

import java.io.IOException;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.time.LocalDateTime;

import org.json.JSONObject;

import com.squareup.okhttp.MediaType;
import com.squareup.okhttp.OkHttpClient;
import com.squareup.okhttp.Request;
import com.squareup.okhttp.RequestBody;
import com.squareup.okhttp.Response;

/**
 * @author jgonzalez
 *
 */
/**
 * @author jgonzalez
 *
 */
public class RestHopu {
	private OkHttpClient client;
	private MediaType mediaType = MediaType.parse("application/x-www-form-urlencoded");
	private RequestBody body = RequestBody.create(mediaType, "username=julgonzalez&password=vZnAWE7FexwgEqwT&grant_type=password&client_id=fiware-login");
	private String tocken;
	private JSONObject json;
	private LinkedHashMap<String,String> mapDatosAirePresencia; 
	private Registro reg;
	private Request request;
	
	/** Inicia la sesion con el APIRest de Hopu
	 * @throws IOException
	 */
	public RestHopu() throws IOException{
		
		client = new OkHttpClient();
		reg = new Registro("logRestHopu");
		Request request = new Request.Builder()
				.url("https://fiware.hopu.eu/keycloak/auth/realms/fiware-server/protocol/openid-connect/token")
				.method("POST", body)
				.addHeader("Content-Type", "application/x-www-form-urlencoded")
				.build();
		
		Response response = client.newCall(request).execute();	
		if (!response.isSuccessful()) {
			tocken = "";
			throw new IOException("Error No se pudo obtener el tocken " + response.message().toString() + " Code:" + response.code());
		}else {
			JSONObject json = new JSONObject(response.body().string());
			tocken = json.get("access_token").toString();
		}
	}
	
	/**	Hace la llamada a todas las APIs de Hopu para obtener los datos de calidad de aire y de presencia 
	 * @return un map con los valores obtenidos de los sensores 
	 * @throws IOException
	 */
	public LinkedHashMap<String,String> cicloLlamadas() throws IOException {
		
		mapDatosAirePresencia = new LinkedHashMap<String,String>();
		
		//** Obtengo Si el dispositivo esta operativo
			Response respuestaOK = getEstado();	
			json = formateaRespuesta(respuestaOK.body().string());
			
			if (respuestaOK.isSuccessful()) {	// 200...300
				if(json.get("operationalStatus").toString().equals("DISCONNECTED")) {
					reg.grabarReg("FALLO El dispositivo NO responde -> operationalStatus:" + json.get("operationalStatus").toString() );						
				}else {
					reg.grabarReg("El dispositivo responde -> operationalStatus: " + json.get("operationalStatus").toString() );
				}
			}else {
				grabarFallo(respuestaOK,json);
			}
			respuestaOK = null;
			json = null;
			
		//** Obtengo la calidad del aire PM2.5, PM10, CO2, humedad y temperatura
			Response respuestaCaldiadAire = getAirQuality();	
			json = formateaRespuesta(respuestaCaldiadAire.body().string());
			
			if (respuestaCaldiadAire.isSuccessful()) { // 200...300
				/*2021-09-30T11:27:39.00Z*/
				
				DateTimeFormatter formatoFechaHoraCSV = DateTimeFormatter.ofPattern("dd-MM-YYYY HH:mm:ss");
				String fechaJson = json.getString("TimeInstant");
				fechaJson = fechaJson.substring(0,fechaJson.length()-4);
				LocalDateTime.now(ZoneId.of("Europe/Madrid"));
				LocalDateTime fechaDelRegistro = LocalDateTime.parse(fechaJson);
				if ( (fechaDelRegistro.getMonthValue() > 3 && fechaDelRegistro.getMonthValue() < 10)  
						|| (fechaDelRegistro.getMonthValue() >= 3  && fechaDelRegistro.getDayOfMonth() >= 28 && fechaDelRegistro.getHour() >= 2) 
						|| (fechaDelRegistro.getMonthValue() <= 10  && fechaDelRegistro.getDayOfMonth() <= 31  && fechaDelRegistro.getHour() < 3)  ) {
					fechaDelRegistro = fechaDelRegistro.plusHours(2);		// Verano 
				} else {
					fechaDelRegistro = fechaDelRegistro.plusHours(1);		// Invierno
				}
				mapDatosAirePresencia.put("timeInstant",fechaDelRegistro.format(formatoFechaHoraCSV));
				mapDatosAirePresencia.put("pm25", String.valueOf( json.getFloat("PM25")) );
				mapDatosAirePresencia.put("pm10", String.valueOf( json.getFloat("PM10")) );
				mapDatosAirePresencia.put("co2",  String.valueOf( json.getFloat("CO2")) );
				mapDatosAirePresencia.put("humedad", String.valueOf( json.getFloat("humidity")) );
				mapDatosAirePresencia.put("temperatura", String.valueOf( json.getFloat("temperature")) );
				
			}else {
				grabarFallo(respuestaCaldiadAire,json);
			}
		
			respuestaCaldiadAire = null;
			json = null;
			
		//** Obtengo la lectura del sensor de presencia
			Response respuestaPresencia = getPresencia();	
			json = formateaRespuesta(respuestaPresencia.body().string());
			
			if (respuestaPresencia.isSuccessful()) { // 200...300
				float indoor = json.getFloat("numberOfIncoming") - json.getFloat("numberOfOutgoing");
				// Me quedo tambien con el timeStamp del aforamiento para guardarlo aunque no tenga los datos del aire
				DateTimeFormatter formatoFechaHoraCSV = DateTimeFormatter.ofPattern("dd-MM-YYYY HH:mm:ss");
				String fechaJson = json.getString("TimeInstant");
				fechaJson = fechaJson.substring(0,fechaJson.length()-4);
				LocalDateTime.now(ZoneId.of("Europe/Madrid"));
				LocalDateTime fechaDelRegistro = LocalDateTime.parse(fechaJson);
				if ( (fechaDelRegistro.getMonthValue() > 3 && fechaDelRegistro.getMonthValue() < 10)  
						|| (fechaDelRegistro.getMonthValue() >= 3  && fechaDelRegistro.getDayOfMonth() >= 28 && fechaDelRegistro.getHour() >= 2) 
						|| (fechaDelRegistro.getMonthValue() <= 10  && fechaDelRegistro.getDayOfMonth() <= 31  && fechaDelRegistro.getHour() < 3)  ) {
					fechaDelRegistro = fechaDelRegistro.plusHours(2);		// Verano 
				} else {
					fechaDelRegistro = fechaDelRegistro.plusHours(1);		// Invierno
				}
				mapDatosAirePresencia.put("timeInstantTeraBee",fechaDelRegistro.format(formatoFechaHoraCSV));
				mapDatosAirePresencia.put("presencia", String.valueOf( indoor)) ;
			}else {
				grabarFallo(respuestaPresencia,json);
			}
			respuestaPresencia = null;
			json = null;
		reg.grabarReg("Se graban todos los datos correctamente");	
		reg = null;
		request = null;
		return mapDatosAirePresencia;
	}	//END cicloLlamadas()


	//** Funciones: LLamadas GET
	
	/** Llama al API de Hopu para comprobar que el dispositivo esté OK
	 * @return Devuelve el Response de la llama al API
	 * @throws IOException
	 */
	public Response getEstado() throws IOException {
		
		request = new Request.Builder()
		  .url("https://fiware.hopu.eu/orion/v2/entities?limit=1000&attrs=*,dateModified&options=count,keyValues")
		  .method("GET", null)
		  .addHeader("fiware-service", "Device")
		  .addHeader("fiware-servicepath", "/ctcon")
		  .addHeader("Authorization", "Bearer "+ tocken +"")
		  .build();
		return client.newCall(request).execute();
	}

	
	/** Llama al API de Hopu para obtener la calidad del aire: PM2.5, PM10, CO2, humedad y temperatura
	 * @return Devuelve el Response de la llama al API
	 * @throws IOException
	 */
	public Response getAirQuality() throws IOException {
		
		request = new Request.Builder()
		  .url("https://fiware.hopu.eu/orion/v2/entities?limit=1000&attrs=*,dateModified&options=keyValues")
		  .method("GET", null)
		  .addHeader("fiware-service", "AirQuality")
		  .addHeader("fiware-servicepath", "/ctcon")
		  .addHeader("Authorization", "Bearer "+ tocken +"")
		  .build();
		return client.newCall(request).execute();
	}
	
	
	/** Llama al API de Hopu para obtener las lecturas del sensor de presencia
	 * @return Devuelve el Response de la llama al API
	 * @throws IOException
	 */
	public Response getPresencia() throws IOException {
		
		request = new Request.Builder()
		  .url("https://fiware.hopu.eu/orion/v2/entities?limit=1000&attrs=*,dateModified&options=count,keyValues")
		  .method("GET", null)
		  .addHeader("fiware-service", "PeopleCounting")
		  .addHeader("fiware-servicepath", "/ctcon")
		  .addHeader("Authorization", "Bearer "+ tocken +"")
		  .build();
		return client.newCall(request).execute();
	}
	
	//** Funciones: utilidades
	
	/**
	 * @param resp Body de la respuesta
	 * @return el mismo String preparado para JSON, {}
	 */
	public JSONObject formateaRespuesta (String resp) {
    	if( resp.startsWith("[")) {
    		resp = resp.substring(1,resp.length()-1);					
		}
    	return new JSONObject(resp);
    }
	
	public void grabarFallo (Response response, JSONObject json) throws IOException {
    	Registro regError = new Registro("logError");
    	regError.grabarReg("FALLO al ejecutar la llamada al REST "+ response.header("fiware-service") +" -> CODE: " + response.code() +" error: "+ json.get("error") + " descripcion: " + json.get("description"));
    	regError = null;
	}
	
	
	
}
