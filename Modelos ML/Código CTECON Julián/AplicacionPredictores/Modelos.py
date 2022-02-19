from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from CONSTANTES import VAROBJETIVO, VAREXOGENA, CARPETA_OUTPUT, ANCHO_GRAFICO, ALTO_GRAFICO
plt.rcParams['figure.figsize'] = (ANCHO_GRAFICO, ALTO_GRAFICO)

# Modelado y Forecasting
# ==============================================================================
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

from skforecast.ForecasterAutoreg import ForecasterAutoreg
from skforecast.ForecasterAutoregMultiOutput import ForecasterAutoregMultiOutput
from skforecast.model_selection import grid_search_forecaster




class Modelos:
    """ Contiene todo los modelos ML con lo que vamos a trabajar"""

    dfTrain  = pd.DataFrame()   # Garda la parte de train de los datos. CARGADOS EN EL CONSTRUCTOR
    dfTest = pd.DataFrame() # Guarda la parte de test de los datos.  CARGADOS EN EL CONSTRUCTOR
    dfPrediccion = pd.DataFrame() # Guarda el index para realizar la prediccion.  CARGADOS EN EL CONSTRUCTOR
    dfTrainExo = pd.DataFrame() # guarda los mismos datos de train pero con la variable exogena.  CARGADOS EN EL CONSTRUCTOR


    # Hiperparametros Ferecast para prueba de mejora de los hiperparametros 
    lags_grid = [10, 15, 20]
    param_grid = {'n_estimators': [50, 100, 500], 'max_depth': [3, 5, 10]}
    steps = 0

    mejorLag = int(6) #En un principio lo inicializo a 6
    mejorProfundidad = int(100)
    mejorEstimacion = int(5)
    mejorAlpha = int(46)

    forecaster_rf = None #MODELO
    
    ### Inicio la clase recogiendo el DF con el que van a trabajar los modelos 
    def __init__(self, dfTrain, dfTest, dfPrediccion, steps):
        self.dfTrain = dfTrain  
        self.dfTrainExo = dfTrain   # Con las variables exogenarias
        self.dfTrain = self.dfTrain[VAROBJETIVO] # Unicamente con el dato a predecir 
        self.dfTest = dfTest
        self.dfTestExo = dfTest  # Con las variables exogenarias
        self.dfTest = self.dfTest[VAROBJETIVO] # Unicamente con el dato a predecir 
        self.dfPrediccion = dfPrediccion  # Guarda el index (sin datos) para realizar la prediccion. Ultimo registro de df + nº steps 
        self.steps = steps # nº de saltos 

        print (f"Datos de Train: {len(self.dfTrain)}")
        print (f"Datos de Test: {len(self.dfTest)}")
        print (f"Datos de Prediccion: {len(self.dfPrediccion)}")
        
    ### Forecast simple, RandomForest
    ### La entrada es solo el INDEX de tiempo y los valores de CO2
    ##################################################################################################################################################################
    def simpleForecastFit(self):    
        ''' Carga la regresión en el modelo y hace el FIT'''
        self.forecaster_rf = ForecasterAutoreg(
                        regressor=RandomForestRegressor(max_depth=self.mejorProfundidad, n_estimators=self.mejorEstimacion, random_state=123) , #, max_features =10
                        lags=self.mejorLag
                    )
        self.forecaster_rf.fit(y=self.dfTrain)

    def simpleForecastPredictTest(self):      
        ''' Ejecuta la predicción con los datos de Test, devuelve un gráfico del error.'''
        prediccionesTest = self.forecaster_rf.predict( steps= self.steps )
        prediccionesTest = pd.Series(data=prediccionesTest, index=self.dfTest.index)  # Se añade el índice temporal a las predicciones
        prediccionesTest.head()
        error_mse = mean_squared_error(
                y_true = self.dfTest,
                y_pred = prediccionesTest
            )
        plt.clf()
        plt.title( f"Error Test = {error_mse}")
        plt.plot(prediccionesTest.index, self.dfTest, c='r') #Pinto los datos reales de la validación
        plt.plot(prediccionesTest.index, prediccionesTest, c='g') 
        plt.legend(["Datos Reales","Prediccion Test"])
        plt.savefig(f"{CARPETA_OUTPUT}/ErrorTestForecastSimple.jpg")
        print(f"Error de test (mse): {error_mse}")
        return error_mse

    def simpleForecastPredict(self, ventana):
        '''Predice con los pasos de la variable steps  a partir de los datos de la última ventana '''
        print (f"Datos de Ventana: {len(ventana)}")
        predicciones = self.forecaster_rf.predict(steps=self.steps , last_window=ventana[VAROBJETIVO]) #Hay que meter la ventana 
        predicciones = pd.Series(data=predicciones, index=self.dfPrediccion)  # Se añade el índice temporal a las predicciones.
        return predicciones
    
    def simpleForecastHiperparametros (self):
        ''' Obtiene los mejores valores para Lag, Depth y estimaciones'''
        dfMejorResultadoEstimacion = grid_search_forecaster(
                        forecaster  = self.forecaster_rf,
                        y           = self.dfTrain,
                        param_grid  = self.param_grid,
                        lags_grid   = self.lags_grid,
                        steps       = self.steps,
                        method      = 'cv',
                        metric      = 'mean_squared_error',
                        initial_train_size    = int(len(self.dfTrain)*0.5), #Tamaño de train/test para el calculo de hiperparametros 
                        allow_incomplete_fold = False,
                        return_best = True,
                        verbose     = False
                   )
        # Guardo los mejores hiperparametros                    
        # Seteo los hiperparametros en la regresion 
        self.mejorLag = int( dfMejorResultadoEstimacion.values[0][0].max() ) # Mejor Lag
        self.mejorProfundidad = int( dfMejorResultadoEstimacion.values[0][1]["max_depth"] ) # Mejor Profundidad
        self.mejorEstimacion = int( dfMejorResultadoEstimacion.values[0][1]["n_estimators"] )  # Mejor nº de estimacions           


        # Vuelvo a hacer el fit del modelo 
        self.simpleForecastFit()


    ### Forecast Con Variables Exogenas, RandomForest
    ### La entrada es el INDEX de tiempo, el CO2 y una variable exogena, el aforamiento (PRESENCIA/VAREXOGENA)
    ##################################################################################################################################################################
    def exogenaForecastFit(self):
        ''' Carga la regresión en el modelo y hace el FIT con la variable exogena '''
        self.forecaster_rf = ForecasterAutoreg(
                        regressor= RandomForestRegressor(max_depth=self.mejorProfundidad, n_estimators=self.mejorEstimacion, random_state=123),
                        lags=self.mejorLag
                    )
        self.forecaster_rf.fit(y=self.dfTrain, exog = self.dfTrainExo[VAREXOGENA] ) 

    def exogenaForecastPredictTest(self):
        ''' Ejecuta la predicción con los datos de Test, devuelve un gráfico del error.'''
        predicciones = self.forecaster_rf.predict( steps= self.steps , exog=self.dfTestExo[VAREXOGENA])
        predicciones = pd.Series(data=predicciones, index=self.dfTest.index)  # Se añade el indice temporal a las predicciones

        error_mse = mean_squared_error(
                y_true = self.dfTestExo[VAROBJETIVO],
                y_pred = predicciones
            )
        plt.clf()
        plt.title( f"Error Test = {error_mse}")
        plt.plot(predicciones.index, self.dfTestExo, c='r')#Pinto los datos reales de la validación
        plt.plot(predicciones.index, predicciones, c='g') 
        plt.legend(["Datos Reales",VAREXOGENA,"Prediccion Test"])
        plt.savefig(f"{CARPETA_OUTPUT}/ErrorTestForecastVariableExogena.jpg")
        print(f"Error de test (mse): {error_mse}")

    def exogenaForecastPredict(self, ventana, exogenaPrediccion):
        '''Predice con los pasos de la variable steps  a partir de los datos de la última ventana con la variable exogena'''
        print (f"Datos de Ventana: {len(ventana)}")
        predicciones = self.forecaster_rf.predict(steps=self.steps, exog=exogenaPrediccion[VAREXOGENA], last_window=ventana[VAROBJETIVO])
        predicciones = pd.DataFrame(data=predicciones, index=self.dfPrediccion,columns = [VAROBJETIVO])  # Se añade el índice temporal a las predicciones.
        predicciones[VAREXOGENA] = exogenaPrediccion[VAREXOGENA]
        return predicciones
    
    def exogenaForecastHiperparametros (self):
        ''' Obtiene los mejores valores para Lag, Depth y estimaciones'''
        dfMejorResultadoEstimacion = grid_search_forecaster(
                        forecaster  = self.forecaster_rf,
                        y           = self.dfTrain,  #Valor fijo para predecir el CO2
                        exog        = self.dfTrainExo[VAREXOGENA], #Nombre variable exogena 
                        param_grid  = self.param_grid,
                        lags_grid   = self.lags_grid,
                        steps       = self.steps,
                        method      = 'cv',
                        metric      = 'mean_squared_error',
                        initial_train_size    = int(len(self.dfTrain)*0.5), #Tamaño de train/test para el calculo de hiperparametros 
                        allow_incomplete_fold = False,
                        return_best = True,
                        verbose     = False
                   )

         # Seteo los hiperparametros en la regresion 
        self.mejorLag = int( dfMejorResultadoEstimacion.values[0][0].max())  # Mejor Lag
        self.mejorProfundidad = int (dfMejorResultadoEstimacion.values[0][1]["max_depth"]) # Mejor Profundidad
        self.mejorEstimacion = int ( dfMejorResultadoEstimacion.values[0][1]["n_estimators"])  # Mejor nº de estimacions   


        self.exogenaForecastFit()

    ### Forecast Con Variables Exogenas y MultiOutput y Lasso
    ### La entrada es el INDEX de tiempo, el CO2 y una variable exogena, el aforamiento (PRESENCIA/VAREXOGENA)
    ##################################################################################################################################################################
    def exogenaMOForecastFit(self):
        ''' Carga la regresión en el modelo y hace el FIT con la variable exogena '''
        self.forecaster_rf = ForecasterAutoregMultiOutput(
                        regressor= Lasso(random_state=123, alpha = self.mejorAlpha),
                        lags=self.mejorLag,
                        steps = self.steps
                    )
        self.forecaster_rf.fit(y=self.dfTrain, exog = self.dfTrainExo[VAREXOGENA] ) 

    def exogenaMOForecastPredictTest(self):
        ''' Ejecuta la predicción con los datos de Test, devuelve un gráfico del error.'''
        predicciones = self.forecaster_rf.predict( steps= self.steps, exog= self.dfTestExo[VAREXOGENA] )
        predicciones = pd.Series(data=predicciones, index=self.dfTest.index)  # Se añade el índice temporal a las predicciones

        error_mse = mean_squared_error(
                y_true = self.dfTestExo[VAROBJETIVO],
                y_pred = predicciones
            )
            
        plt.clf()
        plt.title( f"Error Test = {error_mse}")
        plt.plot(predicciones.index, self.dfTestExo, c='r')
        plt.plot(predicciones.index, predicciones, c='g') #Pinto los datos reales de la validación
        plt.legend(["Datos Reales",VAREXOGENA,"Prediccion Test"])
        plt.savefig(f"{CARPETA_OUTPUT}/ErrorTestForecastMOVariableExogena.jpg")
        print(f"Error de test (mse): {error_mse}")

    def exogenaMOForecastPredict(self, ventana, exogenaPrediccion):
        '''Predice con los pasos de la variable steps  a partir de los datos de la última ventana con la variable exogena'''
        print (f"Datos de Ventana: {len(ventana)}")
        predicciones = self.forecaster_rf.predict(steps=self.steps, exog=exogenaPrediccion[VAREXOGENA], last_window=ventana[VAROBJETIVO])
        predicciones = pd.DataFrame(data=predicciones, index=self.dfPrediccion, columns = [VAROBJETIVO])  # Se añade el índice temporal a las predicciones.
        predicciones[VAREXOGENA] = exogenaPrediccion[VAREXOGENA]
        return predicciones
    
    def exogenaMOForecastHiperparametros (self):
        ''' Obtiene los mejores valores para Lag y alpha'''
        param_grid = {'alpha': np.logspace(-5, 5, 10)}
        
        dfMejorResultadoEstimacion = grid_search_forecaster(
                        forecaster  = self.forecaster_rf,
                        y           = self.dfTrain, 
                        exog        = self.dfTrainExo[VAREXOGENA], 
                        param_grid  = param_grid,   #Local a la función 
                        lags_grid   = self.lags_grid,
                        steps       = self.steps,
                        method      = 'cv',
                        metric      = 'mean_squared_error',
                        initial_train_size    = int(len(self.dfTrain)*0.5), #Tamaño de train/test para el calculo de hiperparametros 
                        allow_incomplete_fold = False,
                        return_best = True,
                        verbose     = False
                   )

         # Seteo los hiperparametros para la regresion 
        
        self.mejorLag = int ( dfMejorResultadoEstimacion.values[0][0].max() )  # Mejor Lag
        self.mejorAlpha = int ( dfMejorResultadoEstimacion.values[0][1]["alpha"] )  # Mejor Alpha


        self.exogenaMOForecastFit()
    