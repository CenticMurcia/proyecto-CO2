package calidadAire.rest;


import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

public class Registro {
	private Path pathLog;
	private Path carpetadeLogs = Paths.get("./logs");
	private String diaHora ;
	private String nomFichero;
	private ZoneId zoneMadrid = ZoneId.of("Europe/Madrid");
	private DateTimeFormatter formatoFechaHora = DateTimeFormatter.ofPattern("dd-MM-YYYY HH:mm:ss");
	private DateTimeFormatter formatoFecha = DateTimeFormatter.ofPattern("dd-MM-YYYY");
	
	
	public Registro(String nombreReg) throws IOException {
		if(Files.exists(carpetadeLogs)) {
			iniciarArchivo(nombreReg);
		}else {
			Files.createDirectory(carpetadeLogs);
			iniciarArchivo(nombreReg);
		}
	}
	
	public void grabarReg(String txt) throws IOException {
		diaHora = LocalDateTime.now(zoneMadrid).format(formatoFechaHora) + " ";
		Files.writeString(pathLog, diaHora + txt + "\n" , StandardOpenOption.APPEND);
	}
	
	private void iniciarArchivo (String nombreReg) throws IOException {
		nomFichero = nombreReg + "_" + LocalDateTime.now(zoneMadrid).format(formatoFecha) + ".txt";
		diaHora = LocalDateTime.now(zoneMadrid).format(formatoFechaHora) + " ";
		pathLog = Paths.get(carpetadeLogs.toString(),nomFichero);
		
		if(Files.exists(pathLog)) {
			//Files.writeString(pathLog, diaHora + "Se inicia el registro: " + nombreReg + "\n" , StandardOpenOption.APPEND);
		}else {
			Files.writeString(pathLog, diaHora + "Se inicia el registro: " + nombreReg + "\n" , StandardOpenOption.CREATE);
		}
	}
	
	
}
