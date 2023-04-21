from src.utils.libraries import *
# Crear el objeto FRED a partir de la API Key
fred = Fred(api_key=fred_key)
def indicator_extraction(fred_dict, calc_dict):
    """
     Extrae datos de indicadores económicos de FRED y realiza cálculos según el indicador.

     Args:
     - fred_dict (dict): Un diccionario que contiene el código y el nombre de cada indicador económico a extraer.
     - calc_dict (dict): Un diccionario que contiene el código y el nombre de cada columna calculada para agregar al DataFrame.

     Returns:
     - indicators_df (pd.DataFrame): Un DataFrame que contiene los datos de los indicadores económicos extraídos y las columnas calculadas.
     """
    indicators_df = pd.DataFrame() # DataFrame para almacenar los datos extraidos
    # Acceder al diccionario de indicadores economicos para extraer sus datos (utilizando el objeto 'fred' y la funcion 'get_series') y almacenarlos en un DataFrame
    for code,indicator in fred_dict.items():
        indicators_df[indicator] = fred.get_series(code)
        # Printamos el resultado de la extraccion de cada indicador con su codigo, indicador, rows y fecha de inicio
        # Realizar los siguientes calculos dependiendo del indicador y añadirlo al DataFrame
        if code == 'CES0500000003':
            indicators_df[calc_dict[code]] = (indicators_df[indicator] - indicators_df[indicator].shift(12))/indicators_df[indicator]*100
        # elif code == 'CPIAUCSL':
        #     indicators_df[calc_dict[code]] = indicators_df[indicator].pct_change()
        # elif code == 'PPIFIS':
        #     indicators_df[calc_dict[code]] = indicators_df[indicator].pct_change()
        elif code == 'GFDEBTN':
            indicators_df[calc_dict[code]] = (indicators_df[indicator] * .1) / indicators_df['GDP']
        elif code == 'BOPTIMP':
            indicators_df[calc_dict[code]] = indicators_df[indicator] - indicators_df['Exports']
        elif code == 'IEABC':
            indicators_df[calc_dict[code]] = indicators_df[indicator] / indicators_df["GDP"]
    # Crear nuevas columnas para los 'spread' de los tipos de interes (tipos a largo plazo - tipos a cortos plazo)
    # 3m5y,3m10y, 2y10y, 2y20y, 5y10y, 10y30y, 10yTrea30yFRM
    indicators_df["3m5y"] =  indicators_df["5-Year Treasury Yield"] - indicators_df["3-Month Treasury Yield"]
    indicators_df["3m10y"] = indicators_df["10-Year Treasury Yield"] - indicators_df["3-Month Treasury Yield"]
    indicators_df["2y10y"] = indicators_df["10-Year Treasury Yield"] - indicators_df["2-Year Treasury Yield"]
    indicators_df["2y20y"] = indicators_df["20-Year Treasury Yield"] - indicators_df["2-Year Treasury Yield"]
    indicators_df["5y10y"] = indicators_df["10-Year Treasury Yield"] - indicators_df["5-Year Treasury Yield"]
    indicators_df["10y30y"] = indicators_df["30-Year Treasury Yield"] - indicators_df["10-Year Treasury Yield"]
    indicators_df["10yTrea30yFRM"] = indicators_df["30-Year Mortgage Rate"] - indicators_df["10-Year Treasury Yield"]
    # Guardar el DataFrame como un archivo csv
    indicators_df.to_csv(r"src\data\raw\indicators_df.csv")
    print(f'Indicators Extracted: {indicators_df.columns}')
    return indicators_df

def market_extraction(stocks, start, end):
    """
     Extrae datos de mercado históricos para una lista determinada de acciones entre una fecha de inicio y finalización especificada.

     Args:
     - stocks (lst): Lista de acciones para extraer datos.
     - start (str): fecha de inicio en formato yyyy-mm-dd.
     - end (str): fecha de finalización en formato yyyy-mm-dd.

     Returns:
     - market_hist (pd.DataFrame): Pandas DataFrame que contiene datos de mercado históricos para las acciones y el rango de fechas especificados.
     """
    # Permite crear el DataFrame
    yfin.pdr_override()
    # Extraer los precios de !Yahoo Finanzas para cada uno de los indices y almacenarlos en el DataFrame 'markets'
    markets = pdr.get_data_yahoo(stocks,start=start,end=end)
    # Filtrar el DataFrame quedandonos con la columna de 'Adj Close' y el rango temporal previamente definido
    market_hist = markets["Adj Close"].loc[start:end]# Guardar el DataFrame como un archivo csv
    market_hist.to_csv(r"src\data\raw\market_hist.csv")
    return market_hist


def limpiar_markets(markets_dict, start, end):
    """
     Limpia los datos de mercado de los archivos de datos sin procesar y guarda los archivos procesados en el
     carpeta procesada. Filtra datos de mercado para el intervalo de tiempo especificado y
     crea marcos de datos de rendimiento diarios y acumulativos.

     Args:
     - start (str): fecha de inicio en formato YYYY-MM-DD
     - end (str): fecha de finalización en formato YYYY-MM-DD

     Returns:
     - df_markets (pd.DataFrame): DataFrame de datos de mercado filtrados
     - df_market_rets (pd.DataFrame): DataFrame de rentabilidades diarias del mercado
     - df_market_cum (pd.DataFrame): DataFrame de rentabilidades acumuladas del mercado
     """
    # Extraer datos de la carpeta 'raw'
    df_markets = pd.read_csv(r'src\data\raw\market_hist.csv',index_col=0, header=0)
    df_markets = df_markets.rename(columns=markets_dict)
    # Filtrar los datos de mercado de los primeros 23 años
    df_markets = df_markets.loc[start:end]
    df_markets.index = pd.to_datetime(df_markets.index, utc=True)
    df_markets.index = df_markets.index.strftime('%Y-%m-%d')

    # Crear DataFrame de rendimiento diario de mercados
    df_market_rets = df_markets.pct_change().fillna(0)
    df_market_rets.index = pd.to_datetime(df_market_rets.index, utc=True)
    df_market_rets.index = df_market_rets.index.strftime('%Y-%m-%d')
    # Crear DataFrame de rendimiento acumulado de mercados
    df_market_cum = df_market_rets.cumsum().fillna(0)

    # Guardar tablas procesadas de mercados
    df_markets.to_csv(r"src\data\processed\market_hist.csv")
    df_market_rets.to_csv(r"src\data\processed\market_rets.csv")
    df_market_cum.to_csv(r"src\data\processed\market_cum.csv")
    return df_markets, df_market_rets, df_market_cum

def limpiar_indicators(df_ind,indicator_dict, start, end):
    """
    Función que limpia y procesa los datos del DataFrame de indicadores económicos.

    Args:
    - df_ind (DataFrame): DataFrame de los indicadores económicos.
    - indicator_dict (dict): Diccionario con los nombres y columnas de los indicadores.
    - start (str): Fecha de inicio del periodo a limpiar.
    - end (str): Fecha de fin del periodo a limpiar.

    Returns:
    - df_ind (DataFrame): DataFrame de los indicadores económicos sin procesar.
    - df_ind_limpio (DataFrame): DataFrame de los indicadores económicos procesado y limpio.
    """
    # Limpiar datos del DataFrame de indicadores economicos
    df_ind = df_ind.loc[start:end]
    # Rellenar los datos vacios con el dato anterior
    df_ind_limpio = df_ind.fillna(method='ffill')
    # Rellenar los siguientes datos vacios con el ultimo dato
    df_ind_limpio.fillna(method='bfill', inplace=True) 
    # Guardar las tablas de indicadores en csv
    for ind_name, ind_list in indicator_dict.items():
        df_ind[ind_list].dropna().to_csv(r"src\data\processed\{0}.csv".format(ind_name))
    return df_ind, df_ind_limpio

def analisis_univariante(indicators, medidas):
    """
    This function calculates several univariate statistical measures for each indicator in the given pandas dataframes.

    Args:
    - indicators: A dictionary of pandas dataframes. Each dataframe represents an indicator.
    - medidas: A list of strings with the names of the statistical measures to be calculated.

    Returns:
    - A transposed pandas dataframe with the indicators as columns and the statistical measures as rows.
    """
    df_measures = pd.DataFrame(index=medidas)
    for inds, df in indicators.items():
        if inds == "market_cum" or inds == "market_hist":
            pass # Pasar para esos dos indicadores 
        else:
            if inds == "market_rets":
                df = df*100
            else:
                pass
            for n, indicator in enumerate(df.columns):
                # Definir las medidas de Posicion
                mean = df[indicator].mean()
                mode = df[indicator].mode()
                median = df[indicator].median()

                # Definir los cuartile
                Percentil_0 = df[indicator].quantile(0)
                Percentil_25 = df[indicator].quantile(0.25)
                Percentil_75 = df[indicator].quantile(0.75)
                Percentil_100 = df[indicator].quantile(1)

                # Definir las medidas de Variabilidad
                var = df[indicator].var()
                std = df[indicator].std()

                # Definir las medidas de Forma
                skew = df[indicator].skew()
                kurt = df[indicator].kurt()

                data=[mean, median, mode[0], Percentil_0, Percentil_25, Percentil_75, Percentil_100, var, std, skew, kurt]

                df_measures[indicator] = pd.Series(data=data,index = medidas,name=indicator)
                                    
                medidas_tup = zip(medidas, data)

                fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(15, 3))
                plt.subplots_adjust(hspace=0.5)
                fig.suptitle(indicator, fontsize=12, y=0.9)
                
                sns.histplot(df[indicator], kde=True, ax=axs[0])
                axs[0].axvline(mean, color="red", linestyle="--", label="Mean")
                axs[0].axvline(median, color="green", linestyle="--", label="Median")
                axs[0].axvline(mode[0], color="blue", linestyle="--", label="Mode")
                axs[0].axvline(Percentil_25, color="yellow", linestyle="--", label="25th Percentile")
                axs[0].axvline(Percentil_75, color="yellow", linestyle="--", label="75th Percentile")
                axs[0].legend(loc='upper right', fontsize=10)
                axs[1].boxplot(df[indicator])
                plt.tight_layout();
                plt.close(fig)

                # Create an HTML table
                table = HTML(df_measures[[indicator]].round(4).to_html(index=True))
                # Display the chart and table side by side
                display(table, fig)
    return df_measures.T
    """
    This code defines a function called "analisis_univariante" that takes in two arguments, 
    "indicators" and "medidas". It creates a new empty dataframe called "df_measures" with an index of "medidas". 
    It then loops through each key-value pair in "indicators", 
    which is expected to be a dictionary with indicator names as keys and dataframes with indicator data as values. 
    For each dataframe, the code calculates various measures of central tendency, variability, and shape, and creates a histogram and boxplot using seaborn. 
    It also creates an HTML table of the measures for each indicator and displays it alongside the charts. 
    Finally, the function returns the "df_measures" dataframe with the calculated measures for each indicator.
    """

def analisis_bivariante(markets, indicators_names, stock_start, stock_end, df_market_hist, df_market_cum, inds_dict):
    """
    Genera gráficos y tablas de análisis bivariados para datos del mercado de valores vs indicadores económicos.

    Args:
    - markets (lista): Lista de nombres de mercado (str) para analizar.
    - indicators_names (lista): Lista de nombres de indicadores (str) a analizar.
    - stock_start (str): Fecha de inicio (AAAA-MM-DD) para el análisis.
    - stock_end (str): Fecha de finalización (AAAA-MM-DD) para el análisis.
    - df_market_rets (pandas.DataFrame): DataFrame con datos de rentabilidad del mercado.
    - df_market_cum (pandas.DataFrame): DataFrame con datos de rentabilidad acumulada del mercado.
    - df_inds (pandas.DataFrame): DataFrame con datos del indicador.

    Returns:
    - df_ind_mkt (pandas.DataFrame): DataFrame con datos de mercado e indicadores combinados.
    - df_ind_mkt_values ​​(pandas.DataFrame): DataFrame con rendimientos acumulados del mercado fusionado y datos de indicadores.
    """
    for ind, df_ind in inds_dict.items():
        df_ind_chg = df_ind.pct_change().fillna(0)
        df_ind_mkt = pd.merge(df_market_hist[markets], df_ind_chg[indicators_names], left_index=True, right_index=True)
        df_ind_mkt[markets] = df_ind_mkt[markets].pct_change().fillna(0)
        if ind == "interest_rate_spread" or ind == "interest_rates":
            df_ind_mkt_values = pd.merge(df_market_cum[markets], df_ind[indicators_names].loc[stock_start:stock_end].fillna(0), left_index=True, right_index=True)
        else:
            df_ind_mkt_values = pd.merge(df_market_cum[markets], df_ind[indicators_names].loc[stock_start:stock_end].pct_change().cumsum().fillna(0), left_index=True, right_index=True)

        for market in markets:
            for indicator in indicators_names:
                fig = plt.figure(figsize=(10,10))
                fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(16, 8), )
                plt.subplots_adjust(hspace=0.5, top=1, wspace=0.5)
                fig.suptitle(market+" vs "+indicator, fontsize=12, y=1)
                sns.histplot(data=[df_ind_mkt[market],df_ind_mkt[indicator]], color="#4CB391", fill=True, alpha=0.5, kde=True, ax=axs[0,0])
                sns.boxplot(data=df_ind_mkt[[market,indicator]],ax=axs[1,0])
                sns.regplot(x=df_ind_mkt[market], y=df_ind_mkt[indicator],ax=axs[1,1])
                df_ind_mkt_values[[market,indicator]].plot(ax=axs[0,1])
                plt.tight_layout();
                plt.close(fig)

                df_corr = df_ind_mkt.corr()
                # Create an HTML table
                table = HTML(pd.DataFrame(df_corr[[market]].loc[indicator]).round(4).to_html(index=True))
                # Display the chart and table side by side
                display(table, fig)

    return df_ind_mkt, df_ind_mkt_values, df_corr

def analisis_multivariante(markets, indicators, df_market_hist):

    """
    Realiza un análisis multivariado de los datos proporcionados.

    Args:
    - mercados (lista): una lista de cadenas que representan los nombres de los mercados a analizar.
    - indicadores (dict): un diccionario donde las claves son cadenas que representan los nombres de los indicadores
        y los valores son pandas DataFrames que representan los datos del indicador.
    - df_market_hist (pandas DataFrame): un DataFrame que representa los datos de rentabilidad del mercado.

    Returns:
    - df_ind_mkt (pandas DataFrame): un DataFrame que representa datos combinados de rendimientos e indicadores del mercado.
    - df_corr (pandas DataFrame): un DataFrame que representa la matriz de correlación de df_ind_mkt.

    Hace lo siguiente:
    - Para cada indicador y su correspondiente DataFrame en 'indicators':
        - Calcula el cambio porcentual del DataFrame y llena cualquier NaN con 0.
        - Guarda el DataFrame como un archivo csv.
        - Fusiona los datos del indicador y los datos de rendimiento del mercado.
        - Calcula los valores de correlación mínimos y máximos de los datos de rendimiento del mercado.
        - Traza un mapa de calor de la matriz de correlación de los datos combinados.
        - Traza un diagrama de caja de los datos combinados.
        - Traza un diagrama de pares de los datos combinados.
    """
    corr_dict = {}
    for indicator, df_indicator in indicators.items():
        df_ind_pct_chg = df_indicator.pct_change().fillna(0)
        # Guardar el DataFrame como un archivo csv
        df_ind_pct_chg.to_csv(r"src\data\processed\pct_change\{0}.csv".format(indicator))
        # Merge los datos de indicadores y los datos de mercado
        df_ind_mkt = pd.merge(df_market_hist[markets], df_ind_pct_chg, left_index=True, right_index=True)
        df_ind_mkt[markets] = df_ind_mkt[markets].pct_change().fillna(0)
        min = df_ind_mkt.corr().min().min()
        max = df_ind_mkt.corr().max().max()
        center = (max+min)/2
        fig, axs = plt.subplots(nrows=2,ncols=1,figsize=(15,15))
        fig.suptitle(indicator)
        sns.heatmap(df_ind_mkt.corr(),vmin=min, vmax=max, center=center,
                    cmap=sns.color_palette("RdYlGn", as_cmap=True),
                    square=True, linewidths=.5, annot=True, fmt='.3f', ax=axs[0]);
        df_ind_mkt.boxplot(figsize=(20,10),ax=axs[1]);
        sns.pairplot(df_ind_mkt, diag_kind="kde", kind="reg")
        df_corr = df_ind_mkt.corr().round(4)
        corr_dict[indicator] = df_corr
    return df_ind_mkt, corr_dict

def analisis_estadistico(indicators, markets, df_market_hist, alpha):
    df_ttest = pd.DataFrame(index=["indicator","market","t_statistic", "p_value"])
    contador = 0
    for indicator, df_ind in indicators.items():
        for market in markets:
            for ind in df_ind.columns:
                ind_returns = np.array(df_ind[ind].pct_change().fillna(0))
                market_returns = np.array(df_market_hist[market].pct_change().fillna(0))

                ind_mean = np.mean(ind_returns)
                market_mean = np.mean(market_returns)
                ind_std = np.std(ind_returns)
                market_std = np.std(market_returns)

                t_statistic, p_value = ttest_ind(ind_returns, market_returns)

                print(f'{ind} mean return: ', ind_mean)
                print(f'{market} mean return: ', market_mean)
                print(f'{ind} standard deviation: ', ind_std)
                print(f'{market} standard deviation: ', market_std)
                print(f't-statistic: ', t_statistic)
                print(f'p-value: ', p_value)
                contador += 1
                df_ttest[contador] = pd.Series([ind,market,t_statistic, p_value],index=["indicator","market","t_statistic", "p_value"])
    df_ttest = df_ttest.T.set_index(["indicator","market"])
    for df in indicators.values():
        for ind in df.columns:
            plt.figure(figsize=(5,8))  
            plt.barh(y = df_ttest.loc[ind,"p_value"].sort_values(ascending=True).index,
                    width = df_ttest.loc[ind,"p_value"].sort_values(ascending=True))
            plt.vlines(x=alpha, color='r', linestyle='-', ymin=0, ymax=df_ttest.loc[ind,"p_value"].sort_values(ascending=True).index[-1])
            plt.title(ind)
    return df_ttest