import os
import shutil
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

def limpar_pasta_trusted():
    """
    S01: Limpar apenas o conteúdo visível da pasta trusted,
    preservando:
    - a própria pasta trusted
    - arquivos e diretórios ocultos (iniciados com '.')
    """

    if not TRUSTED_BASE_DIR.exists():
        TRUSTED_BASE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Pasta '{TRUSTED_BASE_DIR}' criada com sucesso.")
        return

    for item in TRUSTED_BASE_DIR.iterdir():

        # Preserva arquivos/pastas ocultos
        if item.name.startswith('.'):
            continue

        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    print(f"Conteúdo da pasta '{TRUSTED_BASE_DIR}' removido com sucesso.")

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
        escrever em Parquet particionado por AnoMes.
        Resultado em pasta trusted/part, com compressão ZSTD e row groups de 100k linhas."""
    
    con.execute(f"""
        COPY (
            SELECT * FROM read_json('{str(RAW_BASE_DIR)}/**/data_set.json')
        ) TO '{str(TRUSTED_BASE_DIR)}/part' (
            FORMAT PARQUET, 
            COMPRESSION '{COMPRESSION_TYPE}',
            PARTITION_BY (AnoMes), 
            ROW_GROUP_SIZE 100000,
            OVERWRITE_OR_IGNORE TRUE
        )
    """)
    print("Dados JSON da camada RAW convertidos e particionados em Parquet.")

def quarentenar(con) -> None:
    # S02: WHERE Municipio_Ibge IS NULL OR Estado_Ibge IS NULL OR Sigla_Regiao IS NULL
    # COPY . TO trusted/quarantine/part
    """ S02: ler os Parquets particionados da etapa anterior, filtrar os registros que apresentarem valores nulos ou vazios em campos críticos (Municipio_Ibge, Estado_Ibge, Sigla_Regiao), 
        e escrever esses registros "quarentenados" em Parquet, mantendo a mesma estrutura de partições.
        Resultado em pasta trusted/quarantine/part, com compressão ZSTD e row groups de 100k linhas."""

    quarantine_dir = TRUSTED_BASE_DIR / "quarantine" / "part"

    quarantine_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    con.execute(f"""
        COPY (
            SELECT 
                * REPLACE (
                    REPLACE(UPPER(TRIM(Municipio)), 'N/D', 'NAO INFORMADO') AS Municipio,
                    REPLACE(UPPER(TRIM(Estado)), 'N/D', 'NAO INFORMADO') AS Estado,
                    REPLACE(UPPER(TRIM(Regiao)), 'N/D', 'NAO INFORMADO') AS Regiao
                )
            FROM read_parquet('{str(TRUSTED_BASE_DIR)}/part/**/*.parquet')
            WHERE Municipio_Ibge IS NULL OR Estado_Ibge IS NULL OR Sigla_Regiao IS NULL
        ) TO '{str(quarantine_dir)}' (
            FORMAT PARQUET, 
            COMPRESSION '{COMPRESSION_TYPE}',
            PARTITION_BY (AnoMes), 
            ROW_GROUP_SIZE 100000,
            OVERWRITE_OR_IGNORE TRUE
        )
    """)

    print("Registros com campos críticos nulos ou vazios QUARENTENADOS e particionados em Parquet.")

def normalizar_batini(con) -> None:
    # S03: TRIM, UPPER, strptime, :DOUBLE
    # COPY . TO trusted/norm
    """ S03: ler os Parquets particionados da etapa anterior, aplicar as transformações de normalização:
        Completude: valores nulos ou vazios em campos críticos
        Consistência: garantir que não traga valores nulos ou vazios,
        Acuácia: TRIM, UPPER, conversão de tipos, etc.,
        Temporalidade: filtrar apenas os períodos de interesse (202601 a 202604),        
        e escrever novamente em Parquet, mantendo a mesma estrutura de partições.
        Resultado em pasta trusted/norm, com compressão ZSTD e row groups de 100k linhas."""

    con.execute(f"""
        COPY (
            SELECT 
                * REPLACE (
                    UPPER(TRIM(Municipio)) AS Municipio,
                    UPPER(TRIM(Estado)) AS Estado,
                    UPPER(TRIM(Sigla_Regiao)) AS Sigla_Regiao,
                    UPPER(TRIM(Regiao)) AS Regiao
                )
            FROM read_parquet('{str(TRUSTED_BASE_DIR)}/part/**/*.parquet')
            WHERE Municipio_Ibge is not null AND Estado_Ibge is not null AND Sigla_Regiao is not null
            AND AnoMes IN ({', '.join([f"'{p}'" for p in get_periodos_pesquisa()])})
        ) TO '{str(TRUSTED_BASE_DIR)}/norm' (
            FORMAT PARQUET, 
            COMPRESSION '{COMPRESSION_TYPE}',
            PARTITION_BY (AnoMes), 
            ROW_GROUP_SIZE 100000,
            OVERWRITE_OR_IGNORE TRUE
        )
    """)

    print("Dados NORMALIZADOS e particionados em Parquet.")

def deduplicar(con) -> None:
    # S03: DISTINCT ON (chave)

    con.execute(f"""
        COPY (
            SELECT DISTINCT ON (AnoMes, Municipio_Ibge) *
            FROM read_parquet('data/trusted/norm/**/*.parquet')
            ORDER BY AnoMes DESC
         ) TO '{str(TRUSTED_BASE_DIR)}/dedup' (
            FORMAT PARQUET, 
            COMPRESSION '{COMPRESSION_TYPE}',
            PARTITION_BY (AnoMes), 
            ROW_GROUP_SIZE 100000,
            OVERWRITE_OR_IGNORE TRUE
        )
    """)

    print("Dados DEDUPLICADOS e particionados em Parquet.")

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
    limpar_pasta_trusted()

    connection = duckdb.connect()

    # DuckDB primeiro — sem tocar na RAM
    # inspecionar_raw(connection)
    particionar_raw(connection)
    quarentenar(connection)    
    normalizar_batini(connection)
    deduplicar(connection)
    # Pandas entra aqui, não antes
    # fronteira Raw → Trusted
    # df_ok, df_err = validar(df)

    # df_ok.to_parquet(f"{TRUSTED_BASE_DIR}/final.parquet")
    # if len(df_err):
        # df_err.to_parquet(
            # "data/quarantine/violations.parquet"
        # )

if __name__ == "__main__":
    main()
