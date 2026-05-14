import os
import duckdb
import pandas as pd

from datetime import datetime
from pathlib import Path

#from pandera.polars import DataFrameSchema
from util import get_periodos_pesquisa

# ── Configuração ──────────────────────────────────────────────────────────────
RAW_BASE_DIR = Path("data/raw")
TRUSTED_BASE_DIR = Path("data/trusted")
COMPRESSION_TYPE = "ZSTD"  # Opções: 'ZSTD', 'SNAPPY', 'GZIP', etc.
#SCHEMA = DataFrameSchema({}) # S05

# ── Funções ───────────────────────────────────────────────────────────────────

def inspecionar_raw(con):    
    # S02: DESCRIBE LIMIT 0
    resultado = con.execute(f"""
        DESCRIBE SELECT *
        FROM read_json_auto('{str(RAW_BASE_DIR)}/**/data_set.json')
        LIMIT 0
    """).fetchdf()
    
    print("Inspeção da camada RAW:")
    print(resultado.info())
    print(resultado[['column_name', 'column_type']])

def particionar_raw(con):
    """ S02: ler JSON, 
        escrever em Parquet particionado por AnoMes e Sigla_Regiao.
        Resultado em pasta trusted/part, com compressão ZSTD e row groups de 100k linhas."""
    
    con.execute(f"""
        COPY (
            SELECT * FROM read_json('{str(RAW_BASE_DIR)}/**/data_set.json')
        ) TO '{str(TRUSTED_BASE_DIR)}/part' (
            FORMAT PARQUET, 
            COMPRESSION '{COMPRESSION_TYPE}',
            PARTITION_BY (AnoMes, Sigla_Regiao), 
            ROW_GROUP_SIZE 100000,
            OVERWRITE_OR_IGNORE TRUE
        )
    """)
    print("Dados JSON da camada RAW convertidos e particionados em Parquet.")

def normalizar(con) -> None:
    # S03: TRIM, UPPER, strptime, :DOUBLE
    # COPY . TO trusted/norm.parquet
    return

def deduplicar(con) -> None:
    # S03: DISTINCT ON (id_emenda)
    return    

def tratar_nulos(con) -> pd.DataFrame:
    # S04: mediana via DuckDB + KNN sklearn
    return    

def tratar_extremos(df) -> pd.DataFrame:
    # S04: IQR + winsorização Pandas
    return

def validar(df) -> tuple:
    # S05: schema.validate(lazy=True)
    # retorna (df_trusted, df_quarentena)
    return
    

def ingest_data(self, data, table_name: str, partition_col: str = None) -> str:
    
    # Criar caminho com timestamp pra versionamento
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    parquet_path = os.path.join(self.base_path, table_name, timestamp)
    # Salvar como Parquet
    if partition_col:
        data.to_parquet(parquet_path, partition_cols=[partition_col], index=False)
    else:
        os.makedirs(parquet_path, exist_ok=True)
        file_path = os.path.join(parquet_path, f"{table_name}.parquet")
        data.to_parquet(file_path, index=False)

    print(f"Dados ingeridos em: {parquet_path}")
    return parquet_path

def register_parquet(self, table_name: str, parquet_path: str):
    # capturar todos os .parquet dentro das partições
    pattern = os.path.join(parquet_path, "**", "*.parquet")

    self.conn.execute(f"""
            CREATE OR REPLACE TABLE {table_name}
            AS SELECT * FROM read_parquet('{pattern}', hive_partitioning=true)
        """)
    print(f"Tabela '{table_name}' registrada no DuckDB.")

def query_data(self, sql_query: str) -> pd.DataFrame:
    result = self.conn.execute(sql_query).fetchdf()
    print("Consulta executada com sucesso.")
    return result

# ── Ponto de Entrada ──────────────────────────────────────────────────────────

def main():
    print("Pipeline de Transformação - Em construção")

    connection = duckdb.connect()

    # DuckDB primeiro — sem tocar na RAM
    inspecionar_raw(connection)
    particionar_raw(connection)    
    # normalizar(connection)
    # deduplicar(connection)
    # Pandas entra aqui, não antes
    # df = tratar_nulos(connection)
    # df = tratar_extremos(df)
    # fronteira Raw → Trusted
    # df_ok, df_err = validar(df)

    # df_ok.to_parquet(f"{TRUSTED_BASE_DIR}/final.parquet")
    # if len(df_err):
        # df_err.to_parquet(
            # "data/quarantine/violations.parquet"
        # )

if __name__ == "__main__":
    main()
