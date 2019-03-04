from sqlalchemy import Table, Column, BigInteger, String, MetaData, ForeignKey


metaData = MetaData()

quinas = Table('quinas', metaData,
    Column('Rank', BigInteger, primary_key=True),
    Column('Concurso', BigInteger, primary_key=True),
    Column('D1', BigInteger),
    Column('D2', BigInteger),
    Column('D3', BigInteger),
    Column('D4', BigInteger),
    Column('D5', BigInteger),
    Column('D6', BigInteger)
)
quadras = Table('quadras', metaData,
    Column('Rank', BigInteger, primary_key=True),
    Column('Concurso', BigInteger, primary_key=True),
    Column('D1', BigInteger),
    Column('D2', BigInteger),
    Column('D3', BigInteger),
    Column('D4', BigInteger),
    Column('D5', BigInteger),
    Column('D6', BigInteger)
)
