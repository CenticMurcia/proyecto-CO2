#Columnas del fichero CSV
VAROBJETIVO = 'co2' # Variable a predecir
VAREXOGENA = 'presencia' # Variable Exogena para el modelo 
VARHUMEDAD = 'humedad'
VARTEMPERATURA = 'temperatura'
VARPM25 = 'pm25'
VARPM10 = 'pm10'
FORMATOCSV = '%d-%m-%Y %H:%M:%S'

#Columnas del fichero de Grafana 
#VAROBJETIVO = 'CO2' # Variable a predecir
#VAREXOGENA = 'presencia' # Variable Exogena para el modelo 
#VARHUMEDAD = 'Humidity'
#VARTEMPERATURA = 'Temperature'
#VARPM25 = 'PM25'
#VARPM10 = 'PM10'
#FORMATOCSV = '%Y-%m-%d %H:%M:%S'


#Otros
FICHERO_CSV = 'calidadAireURDECON.csv' # Nombre del fichero csv donde se guardan los registros 
#FICHERO_CSV = 'OrigenGrafana.csv' # Nombre del fichero csv donde se guardan los registros 
#FICHERO_CSV = 'calidadAireURDECON_SIEMPRE_PRESENCIA.csv' # Nombre del fichero csv donde se guardan los registros 

CARPETA_OUTPUT = 'output' # guarda la carpeta donde se guardan todos los archivos de la aplicacion 
ALTO_GRAFICO = 9
ANCHO_GRAFICO = 16