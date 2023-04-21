# EDA_Indicadores_Economicos_vs_Mercados
Este EDA trata de analizar la interactuación histórica entre el comportamiento de varios de los principales indicadores económicos y los mercados bursátiles en los Estados Unidos para encontrar posibles correlaciones y tendencias de mercado.


# Datos
# Listar los indicadores por su tipo
irates = ["1-Month Treasury Yield",
          "3-Month Treasury Yield",
          "2-Year Treasury Yield",
          "5-Year Treasury Yield",
          "10-Year Treasury Yield",
          "20-Year Treasury Yield",
          "30-Year Treasury Yield",
          "15-Year Mortgage Rate",
          "30-Year Mortgage Rate"]
irate_yld = ["3m5y",
             "3m10y",
             "2y10y",
             "2y20y",
             "5y10y",
             "10y30y",
             "10yTrea30yFRM"]
inflation = ["CPI",
       #       "Inflation rate",
             "PPI",
       #       "PPI rate"
             ] 
usd = ["US Dollar Index"] 
gdp = ["GDP",
      #  "GDP Growth",
       "Real GDP",
      #  "RGDP Growth",
       ]
unemployment = ["Unemployment Rate"]

# Agrupar las listas de indicadores en un diccionario
indicator_dict = {"interest_rates":irates,
                  "interest_rate_spread":irate_yld,
                  "inflation":inflation,
                  "usd":usd,
                  "gdp":gdp,
                  "unemployment":unemployment}


# Hipotesis
- Hay una correlación negativa entre el comportamiento de los tipos de interés y la bolsa en los Estados Unidos
- Cuando los tipos de interés a largo plazo bajan en comparación con los del corto plazo, es muy probable que se aproxime una crisis bursátil.
- Una elevada inflación suele causar bajadas en los mercados bursátiles.
- Hay una correlación negativa entre el USD (Dólar) y los mercados bursátiles de USA.
- Los movimientos en el PIB de USA (GDP) y el mercado bursátil son correlacionados.
- El desempleo y el mercado de valores tienen una correlación negativa.
- Un elevado desempleo suele causar una subida en los tipos de interés; lo que, a su vez, causa la subida de los mercados.
