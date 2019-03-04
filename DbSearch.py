import decimal, datetime
import json
import sqlalchemy
import sys

import AppConfig
import Combinatorics

from DbSchema import metaData, quadras, quinas


def jsonEncoder(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

def encodeRow(r):
    return { 'Concurso': r['Concurso'],
             'Data': r['Data'],
             'Resultado': [ r['D1'], r['D2'], r['D3'], r['D4'], r['D5'], r['D6'] ],
             'Premio': r['Premio'], 
             'Quantidade': r['Quantidade'] }

def main():
    ticket = []
    if len(sys.argv) == 1:
        # No input. Use sample ticket.
        ticket = [ 3, 6, 10, 17, 34, 37, 43 ]   # 1 sena, 6 quinas, 12 quadras
    else:
        ticket = sorted(map(int, sys.argv[1:]))

    if len(ticket) < 6:
        raise ValueError('Input ticket must have at least 6 elements')

    engine = sqlalchemy.create_engine(AppConfig.DB_CONNECTION, echo=False)
    concursos = sqlalchemy.Table('concursos', metaData, autoload=True, autoload_with=engine)
    with engine.connect() as conn:
        # Get all combinations for tickets larger than 6 elements
        ranks = [ Combinatorics.rank(x) for x in Combinatorics.allCombinations(ticket) ]

        select6 = sqlalchemy.select([ concursos.c.Concurso, concursos.c.Data, concursos.c.D1, concursos.c.D2, concursos.c.D3, concursos.c.D4, concursos.c.D5, concursos.c.D6, concursos.c.PremioSena.label('Premio'), sqlalchemy.func.count().label('Quantidade') ]) \
            .where(concursos.c.Rank.in_(ranks)) \
            .group_by(concursos.c.Concurso, concursos.c.Data, concursos.c.PremioSena) \
            .order_by(concursos.c.Concurso)

        select5 = sqlalchemy.select([ concursos.c.Concurso, concursos.c.Data, concursos.c.D1, concursos.c.D2, concursos.c.D3, concursos.c.D4, concursos.c.D5, concursos.c.D6, concursos.c.PremioQuina.label('Premio'), sqlalchemy.func.count().label('Quantidade') ]) \
            .select_from(quinas.join(concursos, quinas.c.Concurso == concursos.c.Concurso)) \
            .where(quinas.c.Rank.in_(ranks)) \
            .group_by(quinas.c.Concurso, concursos.c.Data, concursos.c.PremioQuina) \
            .order_by(concursos.c.Concurso)

        select4 = sqlalchemy.select([ concursos.c.Concurso, concursos.c.Data, concursos.c.D1, concursos.c.D2, concursos.c.D3, concursos.c.D4, concursos.c.D5, concursos.c.D6, concursos.c.PremioQuadra.label('Premio'), sqlalchemy.func.count().label('Quantidade') ]) \
            .select_from(quadras.join(concursos, quadras.c.Concurso == concursos.c.Concurso)) \
            .where(quadras.c.Rank.in_(ranks)) \
            .group_by(quadras.c.Concurso, concursos.c.Data, concursos.c.PremioQuadra) \
            .order_by(concursos.c.Concurso)

        result = { 'aposta': ticket, 
                   'senas': [ encodeRow(r) for r in conn.execute(select6) ], 
                   'quinas': [ encodeRow(r) for r in conn.execute(select5) ], 
                   'quadras': [ encodeRow(r) for r in conn.execute(select4) ] }
        print(json.dumps(result, default=jsonEncoder, indent=4))


main()
