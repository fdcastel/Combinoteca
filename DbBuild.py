import logging
import pandas
import pathlib
import requests
import sqlalchemy
import zipfile 

import AppConfig
import Combinatorics
import DbSchema

def getHtmlResults():
    sourceUrl = 'http://www1.caixa.gov.br/loterias/_arquivos/loterias/D_mgsasc.zip'

    dataPath = pathlib.Path(AppConfig.DATA_FOLDER)
    zipFilePath = dataPath.joinpath('D_mgsasc.zip')

    resultFileName = 'd_megasc.htm'
    resultFilePath = dataPath.joinpath(resultFileName)

    if not resultFilePath.is_file():
        # File doesn't exists. Download it.
        logging.info(f'Downloading from "{sourceUrl}"...')
        req = requests.get(sourceUrl, allow_redirects=True)
        with open(zipFilePath, 'wb') as file:
            file.write(req.content)

	    # Unzip it
        logging.info('Unzipping...')
        with zipfile.ZipFile(zipFilePath, 'r') as zip:
            zip.extract(resultFileName, dataPath)

    # Return html content
    with open(resultFilePath, 'r') as file:
        return file.read()


def createDataFrame(results):
    # Parse html
    logging.info('Parsing html...')
    dfs = pandas.read_html(results, header=0, index_col=0, parse_dates=['Data Sorteio'], thousands='.', decimal=',')
    df = pandas.DataFrame(dfs[0])

    # Drop duplicate rows. Drop unused columns. Rename columns.
    columnsToKeep = ['Data Sorteio', '1ª Dezena', '2ª Dezena', '3ª Dezena', '4ª Dezena', '5ª Dezena', '6ª Dezena', 'Arrecadacao_Total', 
                     'Ganhadores_Sena', 'Rateio_Sena', 'Ganhadores_Quina', 'Rateio_Quina', 'Ganhadores_Quadra', 'Rateio_Quadra', 'Valor_Acumulado']
    columnsToDrop = [col for col in df.columns if col not in columnsToKeep] 

    df.drop_duplicates(subset=columnsToKeep, inplace=True)
    df.drop(labels=columnsToDrop, axis=1, inplace=True)

    df.rename(columns={'Data Sorteio': 'Data',
                       '1ª Dezena': 'D1',
                       '2ª Dezena': 'D2',
                       '3ª Dezena': 'D3',
                       '4ª Dezena': 'D4',
                       '5ª Dezena': 'D5',
                       '6ª Dezena': 'D6',
                       'Arrecadacao_Total': 'Arrecadacao',
                       'Ganhadores_Sena': 'Senas',
                       'Rateio_Sena': 'PremioSena',
                       'Ganhadores_Quina': 'Quinas',
                       'Rateio_Quina': 'PremioQuina',
                       'Ganhadores_Quadra': 'Quadras',
                       'Rateio_Quadra': 'PremioQuadra',
                       'Valor_Acumulado': 'Acumulado'}, inplace=True)

    # Add Rank column
    #   https://stackoverflow.com/a/12377083
    df['Rank'] = df.apply(lambda row: Combinatorics.rank([row['D1'], row['D2'], row['D3'], row['D4'], row['D5'], row['D6']]), axis=1)

    return df


def createDatabase(df):
    engine = sqlalchemy.create_engine(AppConfig.DB_CONNECTION, echo=False)

    logging.info('Creating database...')
    with engine.connect() as conn:
        # Recreate tables
        df.to_sql('concursos', con=conn, if_exists='replace')
        conn.execute('CREATE INDEX "ix_concursos_Rank" ON "concursos" ("Rank");')
        DbSchema.metaData.drop_all(conn)
        DbSchema.metaData.create_all(conn)

        # For each draw, calculate all 5-matches ('quinas') and 4-matches ('quadras') combinations
        logging.info('Creating auxiliary tables...')
        for index, row in df.iterrows():
            if index % 10 == 0:
                logging.info(f'   {index}...')

            s = [ row['D1'], row['D2'], row['D3'], row['D4'], row['D5'], row['D6'] ]
            quinasMatches = Combinatorics.partialMatches(s, 5)
            conn.execute(DbSchema.quinas.insert(), [ {'Concurso': index, 'Rank': Combinatorics.rank(q), 'D1': q[0], 'D2': q[1], 'D3': q[2], 'D4': q[3], 'D5': q[4], 'D6': q[5] } for q in quinasMatches ])

            quadrasMatches = Combinatorics.partialMatches(s, 4)
            conn.execute(DbSchema.quadras.insert(), [ {'Concurso': index, 'Rank': Combinatorics.rank(q), 'D1': q[0], 'D2': q[1], 'D3': q[2], 'D4': q[3], 'D5': q[4], 'D6': q[5] } for q in quadrasMatches ])

            if index == AppConfig.DB_MAX_RESULTS:
                break

    logging.info('All done!')


def main():
    html = getHtmlResults()
    data = createDataFrame(html)
    createDatabase(data)


main()
