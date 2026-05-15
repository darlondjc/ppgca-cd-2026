# 🎓 PPGCA 2026 — Projeto de Ciência de Dados

> **Mestrado Profissional em Ciência de Dados**
> Prof. Josenildo Silva · IFMA · Turma 2026.1

---

## 👥 Grupo

| Nome | Matrícula | E-mail |
|------|-----------|--------|
| Darlon Coqueiro | <ainda sem matrícula> | darlondjc@gmail.com |
| Marcela Moraes | <ainda sem matrícula> | marcelamoraesa@hotmail.com |
| Agnes Freire | <ainda sem matrícula> | agnesfreire.aof@gmail.com |

---

## 📋 Sobre o Projeto

> O projeto se dá acerca dos dados de **Transações Pix liquidadas por Município e por Pessoas Físicas (PF) e Jurídicas (PJ)**, considerando a perspectiva do pagador e do recebedor.
>
> Através da API escolhida, o projeto se propõe a entender os padrões de crescimento, distribuição geográfica e perfil de uso do Pix no Brasil, considerando volume financeiro, quantidade de transações, tipo de usuário (PF e PJ), estado e região. **Observação:** Para fins didáticos e pedagógicos, foi escolhido o período de **Janeiro a Abril** de 2026, com no máximo **10.000 registros por mês**.
>
> **Fonte de Dados:** Estatísticas do Pix / [Transações Pix por Município](https://dadosabertos.bcb.gov.br/dataset/pix/resource/268e3bf6-b096-4006-83cd-813697012ece).
>
> API **para testes no navegador** disponível no [link](https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/aplicacao#!/recursos/TransacoesPixPorMunicipio).
>
> URL da API **para uso no arquivo .env** no [link](https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/TransacoesPixPorMunicipio(DataBase=@DataBase)).
>
> **Estratégia de Carga:** _Full load_, com volume de dados é crescente. Porém há o uso de _hashes_ para garantia de idempotência para evitar duplicidade. Foi utilizado também o recurso de _watermark_ para verificação de latência entre execuções. Ambos os arquivos de _hashes_ e _watermark_ ficam disponíveis no diretório data/control.

---

## 🚀 Como Rodar (Zero Config)

> **Regra de Ouro:** O professor clona este repositório, executa os comandos abaixo
> e tudo funciona. "Funciona na minha máquina" é **falha grave**.

### Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado

### Setup Inicial

```bash
# 1. Clone o repositório
git clone https://github.com/darlondjc/ppgca-cd-2026.git
cd ppgca-cd-2026

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env preenchendo **SOMENTE** o API_BASE_URL com a URL informada (se vazia). Para essa API em específico não foi preciso uso de API_KEY.

# 3. Instale as dependências
uv sync
```

### Executar o Pipeline Completo

```bash
# Sprint 1 — Ingestão (coleta da API para data/raw)
uv run python src/ingest.py

# Resultado esperado: 
[INGEST] Script de ingestão iniciado.
Lendo dados para o período 01/2026...
Encontrados X novos registros persistidos para 01/2026.
Y registros coletados e salvos em data/raw/202601/data_set.json. Desses, são Z registros novos.
Lendo dados para o período 02/2026...
Encontrados X novos registros persistidos para 02/2026.
Y registros coletados e salvos em data/raw/202602/data_set.json. Desses, são Z registros novos.
Lendo dados para o período 03/2026...
Encontrados X novos registros persistidos para 03/2026.
Y registros coletados e salvos em data/raw/202603/data_set.json. Desses, são Z registros novos.
Lendo dados para o período 04/2026...
Encontrados X novos registros persistidos para 04/2026.
Y registros coletados e salvos em data/raw/202604/data_set.json. Desses, são Z registros novos.
Total coletado: W registros. Total de novos registros: K.
Latência do pipeline: T min
[INGEST] ✅ Sprint 1 concluído.
```

```bash
# Sprint 2 — Qualidade & Trusted Layer
uv run python src/transform.py

# Resultado esperado:

```

### Executar o notebook EDA - Diagnóstico de Qualidade 
> Comando usado para geração nas subetapas de transformação:
```bash
uv run quarto render notebooks/eda_qualidade.qmd

# Resultado esperado
Output created: eda_qualidade.html
```
> Após a execução da etapa inteira de transformação, uma nova geração desse arquivo poderá conter resultados diferentes devido as etapas de **quarentena, normalização e deduplicação**.