import pandas as pd
from CONSTANTES import VAROBJETIVO, FORMATOCSV

class FicheroCSV:
    ''' Lee el fichero de registro de calidad del aire, con las columnas que se indiquen en el constructor y en nombre del archivo.'''
    ''' El nombre del fichero se define en las constantes, también las columnas con el nombre VAROBJETIVO y VAREXOGENA'''
    
    df = pd.DataFrame()

    def __init__(self, nombreArch, columnas):
        self.df = pd.read_csv(nombreArch, sep = ";", index_col=0, squeeze=True)
        self.preparaFichero(etiquetas=columnas)

    def preparaFichero(self, etiquetas):
        """Private, deja las columnas que le pasan por el constructor, elimina duplicados y hace el indexDateTime con '%d-%m-%Y %H:%M:%S'"""
        self.df = self.df[etiquetas] # Dejo unicamente las que me pasan por el construcctor
        self.df = self.df.drop_duplicates(subset=[VAROBJETIVO], keep="last")  # Elimino los duplicados lo dejo con 'co2' porque es el dato que se repite en el CSV. No pongo la variable constante del co2
        self.df = self.df.set_index(pd.to_datetime(self.df.index, format=FORMATOCSV)) # Transformo el index en DateTime
        #pd.to_datetime(df['fecha'], format='%d-%m-%Y %H:%M:%S').replace()