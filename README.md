# 🎓 PPGCA 2026 — Projeto de Ciência de Dados

> **Mestrado Profissional em Ciência de Dados**
> Prof. Josenildo Silva · IFMA · Turma 2026.1

---

## 👥 Grupo

| Nome | Matrícula | E-mail |
|------|-----------|--------|
| Darlon Coqueiro | ... | ... |
| Integrante 2 | ... | ... |
| Integrante 3 | ... | ... |

---

## 📋 Sobre o Projeto

> **TODO:** Descreva o problema de negócio escolhido pelo grupo.
>
> **Pergunta Central:** Qual é a pergunta de negócio que este projeto responde?
>
> **Fonte de Dados:** Qual API ou dataset foi utilizado?

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
# Edite o .env preenchendo o API_KEY e API_BASE_URL

# 3. Instale as dependências
uv sync
```

### Executar o Pipeline Completo

```bash
# Sprint 1 — Ingestão (coleta da API para data/raw)
uv run python src/ingest.py

# Resultado esperado: 
X registros coletados e salvos em RAW_FILE. Desses, são Y registros novos.
Latência do pipeline: T min
[INGEST] ✅ Sprint 1 concluído.
```
