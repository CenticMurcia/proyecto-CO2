from logging import error
from os import system
from FicheroCSV import FicheroCSV 
from Modelos import Modelos
from CONSTANTES import VARHUMEDAD, VAROBJETIVO, VAREXOGENA, FICHERO_CSV, CARPETA_OUTPUT, ALTO_GRAFICO, ANCHO_GRAFICO, VARPM10, VARPM25, VARTEMPERATURA

import pandas as pd
import matplotlib.pylab as plt 
import time
import subprocess
plt.rcParams['figure.figsize'] = (ANCHO_GRAFICO, ALTO_GRAFICO)

# Para tenerlo igual que el Jupyter:
#registrosAireSimpleForecast.df = registrosAireSimpleForecast.df[:-steps]

class Menu:
    ''' Menu principal y de modelos de la aplicacion. Define los comportamientos de las opciones de menu, preparando datos, variables y llamando a las funciones en orden determinado según el modelo  '''

    steps = 12  # Numero de saltos para predecir y partir datos en Train /Test
    modeloSeleccionado = 0  # Utilizado para guardar la seleccion del menu y ejecutar un modelo u otro. 1: SimpleForecast, 2:Con variable Exogena, 3: MultiOutput con Exogena y Lasso
    modeloSimpleFK = None   # Guarda el modelo de Forecast simple 
    modeloExogFK = None     # Guarda el modelo de Forecast con variable Exogena 
    modeloMOExoFK = None    # Guarda el modelo de Forecast MultiOutut con variable Exogena 
    registrosAireExoForecast = None # Guarda el objeto FicheroCSV utilizado para los modelos con variable exogena 
    registrosAireSimpleForecast = None # Guarda el objeto FicheroCSV utilizado para los modelos simples (Solo co2)
    carpetaOutput = "output" # guarda la carpeta donde se guardan todos los archivos de la aplicacion 
    resultadoPrediccion = None

    def __init__(self):
        self.menuPrincipal()    # Inicia el menu 
    
    def mide_tiempo(funcion):
        '''Decorador para devolver el tiempo de ejecucion de la funcion'''
        def funcion_medida(*args, **kwargs):
            inicio = time.time()
            c = funcion(*args, **kwargs)
            print(f"Tiempo de ejecucion: {time.time() - inicio} s")
            return c
        return funcion_medida

    
    def pedirNumeroEntero(self, msn: str):
        ''' Pide un numero entero por terminal '''
        correcto=False
        num=0
        while(not correcto):
            try:
                num = int(input(msn))
                correcto=True
            except ValueError:
                print('Error, introduce un numero entero')
        
        return num

    def cuadrarTitulo(self, str, tituloModelo):
        '''Cuadra el titulo del menu del modelo con 62 de longitud total'''
        longTotal = len (str) + len (tituloModelo)
        tituloCompleto = str + tituloModelo + " "
        for i in range(longTotal, 60):
            tituloCompleto += "="
        return tituloCompleto + "|"

    # Menu principal de la aplicacion 
    def menuPrincipal(self ):

        salir = False
        while not salir:
            print ( self.iconoAplicacion)
            print ("\n1. Forecast con una sola variable: " + ("READY" if self.modeloSimpleFK != None  else "NOT READY") )
            print ("2. Forecast con una variable exogena: " + ("READY" if self.modeloExogFK != None  else "NOT READY") )
            print ("3. Forecast MultiOutput " + ("READY" if self.modeloMOExoFK != None  else "NOT READY") )
            print ("4. Ejecutar todos los modelos seguidos")
            print (f"5. Definir steps (saltos): {self.steps}")
            print ("7. Grafico completo")  
            print ("8. Instalar librerias necesarias")
            print ("9. Salir")
            print ("Elige una opcion")
        
            opcion = self.pedirNumeroEntero("Introduce un numero entero: ")
        
            if opcion == 1:
                self.registrosAireSimpleForecast = FicheroCSV(FICHERO_CSV, [VAROBJETIVO]) # Cargo el dichero CSV con la variables necesarias para el modelo 
                self.modeloSeleccionado = 1
                self.menuModelo("Forecast con una sola variable")
            elif opcion == 2:
                self.registrosAireExoForecast = FicheroCSV(FICHERO_CSV, [VAROBJETIVO, VAREXOGENA]) # Cargo el dichero CSV con la variables necesarias para el modelo 
                self.modeloSeleccionado = 2
                self.menuModelo("Forecast con una variable exogena")
            elif opcion == 3:
                self.registrosAireExoForecast = FicheroCSV(FICHERO_CSV, [VAROBJETIVO, VAREXOGENA]) # Cargo el dichero CSV con la variables necesarias para el modelo 
                self.modeloSeleccionado = 3
                self.menuModelo("Forecast MultiOutput")
            elif opcion == 4:
                self.ejecucionFULL()
            elif opcion == 5:
                self.steps = self.pedirNumeroEntero("Introduce el numero de pasos 'steps';  1 step = 5 minutos: ")
            elif opcion == 7:
                self.graficoDatos() 
            elif opcion == 8:
                subprocess.run(['pip','install','-r','requirements.txt'], shell=True)
            elif opcion == 9:
                salir = True
            else:
                print ("Introduce un numero entre 1 y 9")
        
        print ("Fin")

    # Menu para el modelo en especifico, recibe como parametro el titulo del modelo . 
    def menuModelo(self, nombreModelo):
        if (self.steps == 0):
            print ("ERROR: Debe de definir el parametro steps antes de entrar al menu del modelo")
            salir = True
        else:
            salir = False

        while not salir:
            print ("\n|============================================================|")
            print (self.cuadrarTitulo("|============ Menu: ", nombreModelo ))
            print ("|============================================================|")
            print ("1. Primera carga, Entrenar y buscar hiperparametros")
            print ("2. Reentrenar")
            print ("3. Prediccion")
            print ("4. Recargar Datos")
            print ("5. Ejecutar Test del modelo")
            print ("6. Exportar Graficos predicciones")
            print ("9. Menu anterior")
            print ("Elige una opcion")
        
            opcionMenuModelo = self.pedirNumeroEntero("Introduce un numero entero: ")
        
            try:
                if opcionMenuModelo == 1:
                    print ("\n===> Entrenamiento e hiperparametros <===")
                    self.entrenamientoAjuste()
                elif opcionMenuModelo == 2:
                    print ("\n===> Reentrenamiento <===")
                    self.reentrenamiento()
                elif opcionMenuModelo == 3:
                    print ("\n===> Prediccion <===")
                    self.prediccionModelo()
                elif opcionMenuModelo == 4:
                    print ("\n===> Recargar Datos <===")
                    self.cargaDatos()
                elif opcionMenuModelo == 5:
                    print ("\n===> Ejecutar Test del modelo <===")
                    self.test()
                elif opcionMenuModelo == 6:
                    print ("\n===> Exportar Graficos <===")
                    nomArchivo = input("Introduce el nombre del archivo (sin extension): ")
                    self.grafico(nomArchivo)
                elif opcionMenuModelo == 9:
                    self.salirMenuModelo() # Borro la df de resultados para no liarlos entre modelos 
                    salir = True
                else:
                    print ("Introduce un numero entre 1 y 9")
                    
            except AttributeError as atributeError:
                print ("¡ EXCEPCION !:"  )
                print (atributeError)
                print ("Variable sin definir, compruebe que ha ejecutado el modelo en el orden correcto")
            except Exception as exp :
                print ("¡ EXCEPCION NO CONTROLADA !:" )
                print (exp)
                print ("Recargue los datos y vuelva a intentarlo")
                print ("En caso de que el error persista reinicie el programa")
                


    ### Funciones del menu. Determinan la ejecución dependiendo del modelo seleccionado 
    ###################################################################################################

    def entrenamientoAjuste(self):
        if (self.modeloSeleccionado == 1):  # SimpleForecast 
            self.simpleForecastCarga()
        elif (self.modeloSeleccionado == 2):    # Forecast con Exogena
            self.exogenaForecastCarga()
        elif (self.modeloSeleccionado == 3):    # MultiOutput
            self.multiOutExogenaForecastCarga()

    def reentrenamiento(self):
        if (self.modeloSeleccionado == 1):  # SimpleForecast 
            self.simpleForecastEntrenamiento()
        elif (self.modeloSeleccionado == 2):    # Forecast con Exogena
            self.exogenaForecastEntrenamiento()
        elif (self.modeloSeleccionado == 3):    # MultiOutput
            self.multiOutExogenaForecastEntrenamiento()

    def prediccionModelo(self):
        if (self.modeloSeleccionado == 1):  # SimpleForecast 
            self.simpleForecastPrediccion()
        elif (self.modeloSeleccionado == 2):    # Forecast con Exogena
            num_personas = 0
            respuesta = (input("¿Desea definir una presencia para su prediccion?. En caso contratrio se cogeran los ultimos datos aportados Y/N")).upper()
            if (respuesta == 'Y'):
                num_personas = self.pedirNumeroEntero(f"¿Cuantas personas habra dentro de {self.steps * 5} min?")
            self.exogenaForecastPrediccion(respuesta, num_personas)
        elif (self.modeloSeleccionado == 3):    # MultiOutput
            num_personas = 0
            respuesta = (input("¿Desea definir una presencia para su prediccion?. En caso contratrio se cogeran los ultimos datos aportados Y/N")).upper()
            if (respuesta == 'Y'):
                num_personas = self.pedirNumeroEntero(f"¿Cuantas personas habra dentro de {self.steps * 5} min?")
            
            self.multiOutExogenaForecastPrediccion(respuesta, num_personas)

    def cargaDatos(self):
        if (self.modeloSeleccionado == 1):  # SimpleForecast 
            self.simpleForecastCargaDatos()
        elif (self.modeloSeleccionado == 2):    # Forecast con Exogena
            self.exogenaForecastCargaDatos()
        elif (self.modeloSeleccionado == 3):    # MultiOutput
            self.multiOutExogenaForecastCargaDatos()

    def test(self):
        if (self.modeloSeleccionado == 1):  # SimpleForecast 
            self.simpleForecastTest()
        elif (self.modeloSeleccionado == 2):    # Forecast con Exogena
            self.exogenaForecastTest()
        elif (self.modeloSeleccionado == 3):    # MultiOutput
            self.multiOutExogenaForecastTest()
    
    def grafico(self, nomArchivo):
        if (self.modeloSeleccionado == 1):  # SimpleForecast 
            self.simpleForecastGrafico(nomArchivo)
        elif (self.modeloSeleccionado == 2):    # Forecast con Exogena
            self.exogenaForecastGrafico(nomArchivo)
        elif (self.modeloSeleccionado == 3):    # MultiOutput
            self.multiOutExogenaForecastGrafico(nomArchivo)

    def salirMenuModelo(self):
        ''' Elimina los df que se les pasa al modelo: resultadoPrediccion y ventana para que no haya errores entre distintos modelos  '''
        self.resultadoPrediccion = None
        self.ventana = None
        del self.resultadoPrediccion
        del self.ventana


    # Dibuja en un mismo grafico todas las variables del dataSet
    def graficoDatos(self):
        df = pd.read_csv(FICHERO_CSV, sep=";", index_col=0, squeeze=True)
        df = df[["pm25", "pm10", VAROBJETIVO, "humedad", "temperatura", VAREXOGENA]]# Quito la última columna
        df = df.drop_duplicates(subset=[VAROBJETIVO],  keep="last")  # Elimino los duplicados 
        df = df.set_index(pd.to_datetime(df.index, format='%d-%m-%Y %H:%M:%S')) # Transformo el index en DateTime
        plt.clf()
        fig, ax = plt.subplots(figsize=(ALTO_GRAFICO, ANCHO_GRAFICO))
        df[VAROBJETIVO].plot(ax=ax, label='Co2 (ppm)')
        df[VAREXOGENA].plot(ax=ax, label='Presencia (Nº personas)')
        df[VARHUMEDAD].plot(ax=ax, label='Humendad (RH%)')
        df[VARTEMPERATURA].plot(ax=ax, label='Temperatura (ºC)')
        df[VARPM25].plot(ax=ax, label='PM2.5 (μg/m3)')
        df[VARPM10].plot(ax=ax, label='PM10 (μg/m3)')
        ax.legend()
        plt.title ("Grafico Completo datos de entrada ")
        plt.savefig( CARPETA_OUTPUT + "/GraficoCompleto.jpg")




    ### Primer Modelo: SIMPLE FORECAST 
    ### Prediccion con una unica variable de CO2 
    ######################################################################################################

    @mide_tiempo
    def simpleForecastCarga(self):        
        ''' Ejecuta la primera carga del modelo, el primer entrenamiento y la busqueda de hiperparametros '''
        # Parto los df en train/ Test , predicciones y ventana 
        datos_train = self.registrosAireSimpleForecast.df[:-self.steps]
        datos_test  = self.registrosAireSimpleForecast.df[-self.steps:]
        self.prediccion = pd.date_range(self.registrosAireSimpleForecast.df.index[len(self.registrosAireSimpleForecast.df.index) -1], periods=self.steps, freq="5min")   # Preparo el index del df para las predicciones 
        self.ventana = self.registrosAireSimpleForecast.df[-self.steps:]   # Datos a partir de los cuales comienza la prediccion

        if (self.modeloSimpleFK == None):
            self.modeloSimpleFK = Modelos(datos_train, datos_test, self.prediccion, self.steps)
        self.modeloSimpleFK.simpleForecastFit()
        #self.modeloSimpleFK.simpleForecastHiperparametros()

    
    @mide_tiempo    
    def simpleForecastEntrenamiento(self):
        ''' Ejecuta el entrenamieto del modelo '''
        if (self.modeloSimpleFK != None):
            self.modeloSimpleFK.simpleForecastFit()
        else:
            print ("Ejecute primero el paso 1")


    @mide_tiempo
    def simpleForecastPrediccion(self):
        '''Ejecuta la prediccion del modelo '''
        if (self.modeloSimpleFK != None):
            self.resultadoPrediccion = self.modeloSimpleFK.simpleForecastPredict(self.ventana)
        else:
            print ("Ejecute primero el paso 1")


    @mide_tiempo
    def simpleForecastCargaDatos(self):
        '''Vuelve a leer los datos del fichero CSV. reinicia el dataFrame de la prediccion '''
        self.registrosAireSimpleForecast = FicheroCSV(FICHERO_CSV, [VAROBJETIVO])
        self.modeloSimpleFK.dfTrain = self.registrosAireSimpleForecast.df[:-self.steps][VAROBJETIVO]
        self.modeloSimpleFK.dfTest = self.registrosAireSimpleForecast.df[-self.steps:][VAROBJETIVO]
        self.modeloSimpleFK.dfPrediccion = pd.date_range(self.registrosAireSimpleForecast.df.index[len(self.registrosAireSimpleForecast.df.index) -1], periods=self.steps, freq="5min")  
        self.ventana = self.registrosAireSimpleForecast.df[-self.steps:]
        self.prediccion = pd.date_range(self.registrosAireSimpleForecast.df.index[len(self.registrosAireSimpleForecast.df.index) -1], periods=self.steps, freq="5min")   # Preparo el index del df para las predicciones 


    @mide_tiempo
    def simpleForecastTest(self):
        '''Hace el test del modelo, devolviendo el error y creando un grafico '''
        if (self.modeloSimpleFK != None):
            self.modeloSimpleFK.simpleForecastPredictTest()
        else:
            print ("Ejecute primero el paso 1")


    @mide_tiempo
    def simpleForecastGrafico(self, nomArchivo):
        '''Realiza el grafico de la prediccion'''
        if (self.modeloSimpleFK != None):
            print(type(self.resultadoPrediccion))
            #if (type(self.resultadoPrediccion) != None):
            if (type(self.resultadoPrediccion).__name__ != 'NoneType'):
                # Grafico
                plt.clf()
                plt.title("Modelo: Forecast con RandomForest")
                plt.plot(self.ventana.index, self.ventana, c='r')
                plt.plot(self.resultadoPrediccion.index, self.resultadoPrediccion, c='g') #Pinto los datos reales de la validación
                plt.legend(["Ventana Datos Reales", "Prediccion"])
                plt.savefig(f"{CARPETA_OUTPUT}/{nomArchivo}.jpg")
            else:
                print ("Ejecute primero la predicción, paso 3")
        else:
            print ("Ejecute primero el paso 1")

    ##################################################   END   ###############################################
    



    
    ### Segundo Modelo:  FORECAST CON VARIABLE EXOGENA
    ### Prediccion del co2 con la presencia como variable exogena
    ######################################################################################################

    
    @mide_tiempo
    def exogenaForecastCarga(self):        
        '''Ejecuta la primera carga del modelo, el primer entrenamiento y la busqueda de hiperparametros '''
        # Parto los df en train/ Test , predicciones y ventana 
        datos_train = self.registrosAireExoForecast.df[:-self.steps]
        datos_test  = self.registrosAireExoForecast.df[-self.steps:]
        self.prediccion = pd.date_range(self.registrosAireExoForecast.df.index[len(self.registrosAireExoForecast.df.index) -1], periods=self.steps, freq="5min")   # Preparo el index del df para las predicciones 
        self.ventana = self.registrosAireExoForecast.df[-self.steps:] # Datos a partir de los cuales comienza la prediccion

        if (self.modeloExogFK == None):
            self.modeloExogFK = Modelos(datos_train, datos_test, self.prediccion, self.steps)
        self.modeloExogFK.exogenaForecastFit()
        #self.modeloExogFK.exogenaForecastHiperparametros()

    
    @mide_tiempo    
    def exogenaForecastEntrenamiento(self):
        '''Ejecuta el entrenamieto del modelo '''
        if (self.modeloExogFK != None):
            self.modeloExogFK.exogenaForecastFit()
        else:
            print ("Ejecute primero el paso 1 ")

    
    @mide_tiempo
    def exogenaForecastPrediccion(self, respuesta, num_personas):
        '''Ejecuta la prediccion del modelo '''
        if (self.modeloExogFK != None):
            
            if (respuesta == "Y"): # Ponemos a mano la variable exogena
                exogenaPrediccion = pd.DataFrame(data=num_personas, 
                            index = self.prediccion, 
                            columns = [VAREXOGENA])
            else:
                datosPresenciaVentana = self.ventana[VAREXOGENA].to_numpy()    # Reutilizamos los datos de la variable exogena de la ventana para la prediccion
                exogenaPrediccion = pd.DataFrame(data=datosPresenciaVentana, 
                            index = self.prediccion,   # Utilizamos el index de la prediccion 
                            columns = [VAREXOGENA])
            self.resultadoPrediccion = self.modeloExogFK.exogenaForecastPredict(self.ventana, exogenaPrediccion)
            self.prediccion = pd.date_range(self.registrosAireExoForecast.df.index[len(self.registrosAireExoForecast.df.index) -1], periods=self.steps, freq="5min")   # Preparo el index del df para las predicciones, si no lo reescribo, la segunda ejecución de esta función da error al construir el DF de la variable exogena 
        else:
            print ("Ejecute primero el paso 1")

    
    @mide_tiempo
    def exogenaForecastCargaDatos(self):
        ''' Vuelve a leer los datos del fichero CSV. reinicia el dataFrame de la prediccion '''
        self.registrosAireExoForecast = FicheroCSV(FICHERO_CSV, [VAROBJETIVO, VAREXOGENA])
        self.modeloExogFK.dfTrain = self.registrosAireExoForecast.df[:-self.steps][VAROBJETIVO]
        self.modeloExogFK.dfTest = self.registrosAireExoForecast.df[-self.steps:][VAROBJETIVO]
        self.modeloExogFK.dfPrediccion = pd.date_range(self.registrosAireExoForecast.df.index[len(self.registrosAireExoForecast.df.index) -1], periods=self.steps, freq="5min")  
        self.ventana = self.registrosAireExoForecast.df[-self.steps:]
        self.prediccion = pd.date_range(self.registrosAireExoForecast.df.index[len(self.registrosAireExoForecast.df.index) -1], periods=self.steps, freq="5min")   # Preparo el index del df para las predicciones 

    
    @mide_tiempo
    def exogenaForecastTest(self):
        '''Hace el test del modelo, devolviendo el error y creando un grafico '''
        if (self.modeloExogFK != None):
            self.modeloExogFK.exogenaForecastPredictTest()
        else:
            print ("Ejecute primero el paso 1")

    
    @mide_tiempo
    def exogenaForecastGrafico(self, nomArchivo):
        ''' Realiza el grafico de la prediccion'''
        if (self.modeloExogFK != None):
            if (type(self.resultadoPrediccion).__name__ != 'NoneType'):
            # Grafico
                plt.clf()
                plt.title("Modelo: Forecast con variable exogena y RandomForest")
                plt.plot(self.ventana.index, self.ventana[VAROBJETIVO], c='r')
                plt.plot(self.ventana.index, self.ventana[VAREXOGENA], c='r')
                plt.plot(self.resultadoPrediccion.index, self.resultadoPrediccion[VAROBJETIVO], c='g') 
                plt.plot(self.resultadoPrediccion.index, self.resultadoPrediccion[VAREXOGENA], c='g') 
                plt.legend(["Ventana Datos Reales", VAREXOGENA, "Prediccion", "Presencia Estimada"])
                plt.savefig(f"{CARPETA_OUTPUT}/{nomArchivo}.jpg")
            else:
                print ("Ejecute primero la precicción, paso 3")
        else:
            print ("Ejecute primero el paso 1")

    ##################################################   END   ###############################################





    ### Tercer Modelo: MULTIOUTPUT CON VARIABLE EXOGENA
    ### Prediccion del co2 con la presencia como variable exogena
    ######################################################################################################

    
    @mide_tiempo
    def multiOutExogenaForecastCarga(self):        
        '''Ejecuta la primera carga del modelo, el primer entrenamiento y la busqueda de hiperparametros '''
        # Parto los df en train/ Test , predicciones y ventana 
        datos_train = self.registrosAireExoForecast.df[:-self.steps]
        datos_test  = self.registrosAireExoForecast.df[-self.steps:]
        self.prediccion = pd.date_range(self.registrosAireExoForecast.df.index[len(self.registrosAireExoForecast.df.index) -1], periods=self.steps, freq="5min")   # Preparo el index del df para las predicciones 
        self.ventana = self.registrosAireExoForecast.df[-self.steps:] # Datos a partir de los cuales comienza la prediccion

        if (self.modeloMOExoFK == None):
            self.modeloMOExoFK = Modelos(datos_train, datos_test, self.prediccion, self.steps)
        self.modeloMOExoFK.exogenaMOForecastFit()
        #self.modeloMOExoFK.exogenaMOForecastHiperparametros()

    
    @mide_tiempo    
    def multiOutExogenaForecastEntrenamiento(self):
        '''Ejecuta el entrenamieto del modelo '''
        if (self.modeloMOExoFK != None):
            self.modeloMOExoFK.exogenaMOForecastFit()
        else:
            print ("Ejecute primero el paso 1 ")

    
    @mide_tiempo
    def multiOutExogenaForecastPrediccion(self, respuesta, num_personas ):
        '''Ejecuta la prediccion del modelo '''
        if (self.modeloMOExoFK != None):
            
            if ( respuesta == "Y"): # Ponemos a mano la variable exogena
                exogenaPrediccion = pd.DataFrame(data=num_personas, 
                            index = self.prediccion, 
                            columns = [VAREXOGENA])
            else:
                datosPresenciaVentana = self.ventana[VAREXOGENA].to_numpy()    # Reutilizamos los datos de la variable exogena de la ventana para la prediccion
                exogenaPrediccion = pd.DataFrame(data=datosPresenciaVentana, 
                            index = self.prediccion,  # Utilizamos el index de la prediccion 
                            columns = [VAREXOGENA])
            self.resultadoPrediccion = self.modeloMOExoFK.exogenaMOForecastPredict(self.ventana, exogenaPrediccion)
            self.prediccion = pd.date_range(self.registrosAireExoForecast.df.index[len(self.registrosAireExoForecast.df.index) -1], periods=self.steps, freq="5min")   # Preparo el index del df para las predicciones, si no lo reescribo, la segunda ejecución de esta función da error al construir el DF de la variable exogena 
        else:
            print ("Ejecute primero el paso 1")

    
    @mide_tiempo
    def multiOutExogenaForecastCargaDatos(self):
        '''Vuelve a leer los datos del fichero CSV. reinicia el dataFrame de la prediccion '''
        self.registrosAireExoForecast = FicheroCSV(FICHERO_CSV, [VAROBJETIVO, VAREXOGENA])
        self.modeloMOExoFK.dfTrain = self.registrosAireExoForecast.df[:-self.steps][VAROBJETIVO]
        self.modeloMOExoFK.dfTest = self.registrosAireExoForecast.df[-self.steps:][VAROBJETIVO]
        self.modeloMOExoFK.dfPrediccion = pd.date_range(self.registrosAireExoForecast.df.index[len(self.registrosAireExoForecast.df.index) -1], periods=self.steps, freq="5min")  
        self.ventana = self.registrosAireExoForecast.df[-self.steps:]
        self.prediccion = pd.date_range(self.registrosAireExoForecast.df.index[len(self.registrosAireExoForecast.df.index) -1], periods=self.steps, freq="5min")   # Preparo el index del df para las predicciones 

    
    @mide_tiempo
    def multiOutExogenaForecastTest(self):
        '''Hace el test del modelo, devolviendo el error y creando un grafico '''
        if (self.modeloMOExoFK != None):
            self.modeloMOExoFK.exogenaMOForecastPredictTest()
        else:
            print ("Ejecute primero el paso 1")

    
    @mide_tiempo
    def multiOutExogenaForecastGrafico(self, nomArchivo):
        '''Realiza el grafico de la prediccion'''
        if (self.modeloMOExoFK != None):
            if (type(self.resultadoPrediccion).__name__ != 'NoneType'):
                # Grafico
                plt.clf()
                plt.title("Modelo: Forecast MultiOutput con variable exogena y Lasso ")
                plt.plot(self.ventana.index, self.ventana, c='r')
                plt.plot(self.resultadoPrediccion.index, self.resultadoPrediccion, c='g') 
                plt.legend(["Ventana Datos Reales", "Presencia", "Prediccion"])
                plt.savefig(f"{CARPETA_OUTPUT}/{nomArchivo}.jpg")
            else:
                print ("Ejecute primero la precicción, paso 3")
        else:
            print ("Ejecute primero el paso 1")

    ##################################################   END   ###############################################

    def ejecucionFULL(self):
        num_personas = 0
        respuesta = (input("¿Desea definir una presencia para su prediccion?. En caso contratrio se cogeran los ultimos datos aportados Y/N")).upper()
        if (respuesta == 'Y'):
            num_personas = self.pedirNumeroEntero(f"¿Cuantas personas habra dentro de {self.steps * 5} min?")
        
        self.registrosAireSimpleForecast = FicheroCSV(FICHERO_CSV, [VAROBJETIVO])
        self.registrosAireExoForecast = FicheroCSV(FICHERO_CSV, [VAROBJETIVO, VAREXOGENA])

        # Simple Forecast
        self.simpleForecastCarga()
        self.simpleForecastPrediccion()
        self.simpleForecastGrafico("SimpleForecast_EjecucionDesatendida")
        self.salirMenuModelo() # Simulo la navegacion entre menus para resetear las variables 

        # Forecast con Exogena 
        self.exogenaForecastCarga()
        self.exogenaForecastPrediccion(respuesta, num_personas)
        self.exogenaForecastGrafico("ForecastConExogena_EjecucionDesatendida")
        self.salirMenuModelo() # Simulo la navegacion entre menus para resetear las variables 

        # Forecast MultiOutput con var Exogena
        self.multiOutExogenaForecastCarga()
        self.multiOutExogenaForecastPrediccion(respuesta, num_personas)
        self.multiOutExogenaForecastGrafico("ForecastMO_EjecucionDesatendida")
        self.salirMenuModelo() # Simulo la navegacion entre menus para resetear las variables 

    iconoAplicacion = ''' 
                                                                                                                                                                  
                                  ,&&&&&&%&&&&&&&&&.&&&&&&&&&&&&&&&&                                                          
                              *&&&&&&&,         /&&&&&&&*        *&&%&&&&.                                                     
                            &&&&&.                                   *&%&&&                                                   
                          &&&&/                                         %&&&&                                                 
                         &&&&                                             &%&&                                                
                        &&&#                                               &%&&                                               
                   (&&&&&&&                                                 %&&&&&&/                                          
               &&&&&&&#*           ,&&&&&&&&&#          .%&&&&&&&&%.          ./%&&&&&&#                                      
            (&&&&#               &&&&&&&%&&&&&&&(     &&&&%&&&&&&&&&&&               %&&&&*                                   
          *&%%&                ,&%&&&.      &&&&&(  ,&&&&&,       (&&&&&                .&%&&,                                  
         &&&&.                 &&&&&%               &&&&&%        &&&&&&                 .&&&&                                
        %&&&                   &&&&&%               &&&&&#        &&&&&&                   &&&#                               
       .&&&                    (%&&&&       (((((/  (&&&&&       ,%&&&&   &&&              /&&&                               
       %&&&                     (&&&&%&*  %&&&&&%    *&&&&%&%..&&&&&%&  &&% (%&/            &&&*                              
       #&&&                       .&&&%&&&&&&&(         &&%&&&&&%&&&       #&%&            .&&&*                              
        &&&#                                                            .&&&               %&&&                               
        *&&&/                                                           &&&&&&&%          #&&&.                               
         .&&&&                                  &&&&&&&                                  &&&&                                 
           %&&&&.            *******            &&&&&&&            *******            , &&&&/                                  
             *&&&&&#        .&&&&&&&            &&&&&&&            &&&&&&&         #&&&&&,                                     
                ,&&&&&&&&&/ .&&&&&&&            &&&&&&&            &&&&&&&  &&&&&&&&&%.                                       
                      *(%&/ .&&&&&&&            &&&&&&&            &&&&&&&  &&%(,                                              
                            .&&&&&&&            &&&&&&&            &&&&&&&                                                    
                            .&&&&&&&            &&&&&&&            &&&&&&&                                                    
                            .&&&&&&&        *&&&&&&&&&&&&&         &&&&&&&                                                    
                        /////&&&&&&&////      &&&&&&&&&%&     .////&&&&&&&////*                                               
                         ,&&&&&&&&&&&%&        (%&&&&&%.        &%&&&&&&&&&&&.                                                
                           &&&&&&&&&&*           &&%&&           #&%%&&&&&&%                                                  
                            *%&&&&&&              &&/              &&&&&&&,                                                    
                              &&&&(                                 %&&&&                                                     
                               (&                                    .&,                                                                                                                                                                                                         
            '''