package calidadAire.rest;

import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;





/**
 * Comunica con el servidor APIRest de Hopu, recoge los datos de calidad del aire y de presencia y los guarda en un .csv para su posterior procesamiento 
 * con algoritmos de MachineLearning con Python
 */
/**
 * @author jgonzalez
 *
 */
public class App
{
	private String fechaRegAnterior = ""; 
	private String error = "No"; 
	private Runnable runnable;
	private ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
	private ScheduledFuture<?> beeperHandle;
	
    public App()
    {
    	runnable = new Runnable() {
			@Override
			public void run() {
				try {
		    		RestHopu restHopu = new RestHopu(); 
		    		LinkedHashMap<String,String> mapDatosAirePresencia = restHopu.cicloLlamadas();	// Llamo a las APIs para recoger los datos en el Map
		    		
		    		if(!mapDatosAirePresencia.get("timeInstant").equals(fechaRegAnterior)) {
		    			FicheroCSV fichero = new FicheroCSV("calidadAireURDECON", "fecha;pm25;pm10;co2;humedad;temperatura;t_terabee;presencia;");	// Inicio el CSV y le paso el Map para grabar los registros obtenidos 
		    			fichero.grabarReg(mapDatosAirePresencia);
		    			fechaRegAnterior = mapDatosAirePresencia.get("timeInstant");
		    			fichero = null;
		    			// Grabo el mismo fichero para tener continuidad
		    			fichero = new FicheroCSV("calidadAireURDECON_SIEMPRE_PRESENCIA", "fecha;pm25;pm10;co2;humedad;temperatura;t_terabee;presencia;");	// Inicio el CSV y le paso el Map para grabar los registros obtenidos 
		    			fichero.grabarReg(mapDatosAirePresencia);
		    			fechaRegAnterior = mapDatosAirePresencia.get("timeInstant");
		    			fichero = null;
		    		} else {	// Sigo con un fichero distinto para no perder los datos de presencia 
		    			
		    			FicheroCSV fichero = new FicheroCSV("calidadAireURDECON_SIEMPRE_PRESENCIA", "fecha;pm25;pm10;co2;humedad;temperatura;t_terabee;presencia;");	// Inicio el CSV y le paso el Map para grabar los registros obtenidos 
		    			fichero.grabarReg(mapDatosAirePresencia);
		    			//fechaRegAnterior = mapDatosAirePresencia.get("timeInstant");
		    			fichero = null;
		    		}
		    		
		    		mapDatosAirePresencia.clear();
		    		restHopu = null;
		    		mapDatosAirePresencia= null;
		    		System.gc();
					System.gc();
		    		error = "No";
		    	} catch (IOException e) {
		    		try {
		    			error = "No se pudo iniciar la conex.";
		    			Registro reg = new Registro("logCritico");
		    			reg.grabarReg("No se pudo iniciar la conexión con el servidor. Excepcion: " + e.toString());
		    			reg = null;
		    		} catch (IOException e1) {
		    			// Dar alerta visual, eror general y de lectura del disco 
		    		}
		    	}
			}//END RUN
		};
    }
    
    
    /** Ejecuta el Scheduled 
     * @return String del estado Iniciado/Detenido
     */
    public String iniciarCaptacion() {
    	try {
    		// Lanzo la llamada al REST cada 30 segudos
    		beeperHandle = scheduler.scheduleAtFixedRate(runnable, 1, 30, TimeUnit.SECONDS);
    		return estadoHilo();
    	}catch (Exception exp) {
    		return estadoHilo();
    	}
		
    }
    
    /** Ejecuta el Scheduled 
     * @return String del estado Iniciado/Detenido
     */
    public String detenerCaptacion() {
    	try {
    		if (beeperHandle != null) {
    			beeperHandle.cancel(true);
    			beeperHandle = null;
    		}
    		return estadoHilo();    		
    	}catch (Exception exp) {
    		return estadoHilo();
    	}
    }
    
    private String estadoHilo() {
    	if (beeperHandle != null) {
    		if (!beeperHandle.isCancelled()) {
    			return "Iniciado";
    		}else {
    			return "Detenido";
    		}    		
    	}else {
    		return "";
    	}
    }
    
    //Getters
    
	public String getFechaRegAnterior() {
		return fechaRegAnterior;
	}
	
	public String getError() {
		return error;
	}

    

}
