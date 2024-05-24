import pandas as pd


# Limpiar columnas vacías (aquellas que contienen solo valores nulos) de un DataFrame.
def eliminar_columnas_vacias(dataframe):
    # Reemplazar cadenas vacías y espacios en blanco con NaN
    dataframe_sin_valores_vacios = dataframe.replace(['', ' '], pd.NA)

    # Eliminar columnas que contienen solo NaN
    dataframe_sin_columnas_vacias = dataframe_sin_valores_vacios.dropna(axis=1, how='all')

    return dataframe_sin_columnas_vacias


# Elimina las comas que haya en una columna
def limpiar_columna(dataframe, columna):
    # Remove commas from the specified column
    dataframe[columna] = dataframe[columna].str.replace(',', '')

    return dataframe


def eliminar_columna_con_nulos(df):
    # Obtener una lista de columnas que contienen valores nulos
    columnas_con_nulos = df.columns[df.isnull().any()].tolist()

    # Eliminar las columnas que contienen valores nulos
    df.drop(columnas_con_nulos, axis=1, inplace=True)
    return df