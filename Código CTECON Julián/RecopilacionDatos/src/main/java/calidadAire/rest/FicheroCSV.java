package calidadAire.rest;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.LinkedHashMap;

public class FicheroCSV {

	public Path path;
	private String nomFichero;

	
	
	/** Crea el CSV con la siguiente cabecera: fecha;pm2.5;pm10;co2;humedad;temperatura;presencia
	 * @param nombreCSV Nombre para el CSV
	 * @throws IOException
	 */
	public FicheroCSV(String nombreCSV, String cabecera) throws IOException{
		nomFichero = nombreCSV + ".csv";
		path = Paths.get(nomFichero);
		if(!Files.exists(path)) {
			Files.writeString(path, cabecera +" \n" , StandardOpenOption.CREATE);
		}
	}
	
	/**
	 * @param reg Graba una nueva línea en el CSV
	 * @throws IOException
	 */
	public void grabarReg(LinkedHashMap<String,String> reg) throws IOException,IllegalArgumentException {

		reg.forEach((key,value) -> {
			try {
				Files.writeString(path,   value.toString() + ";"  , StandardOpenOption.APPEND);
			} catch (IOException e) {
				throw new IllegalArgumentException("Fallo al escribir los pares key, value en el CSV");
			}
		});
		Files.writeString(path,  "\n" , StandardOpenOption.APPEND);
	}
	
}
