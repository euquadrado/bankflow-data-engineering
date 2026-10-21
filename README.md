# BankFlow — Pipeline ETL e Análise de Transações Financeiras

Projeto de portfólio para Engenharia de Dados Júnior. Simula transações bancárias
para estudar ingestão, qualidade, SQL e indicadores, usando apenas dados fictícios.

**Estado atual: Fase 1 concluída localmente.** Gerador e modelagem disponíveis.
Conexão Oracle, ETL e dashboard ainda não implementados. Nenhuma alteração foi
executada na VM ou no banco.

## Executar a primeira fase

Python 3.10 ou superior, no diretório do projeto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.generate_data
python -m pytest -q
```

O gerador também funciona sem instalar dependências: utiliza a biblioteca padrão.
Gera 1.000 clientes, 1.500 contas e 50.000 transações válidas em 2025,
mais seis linhas inconsistentes. Distribui datas pelo ano e inclui PIX, TED,
depósito, pagamento e transferência, com quatro status bancários.
O valor é construído em centavos inteiros e gravado com duas casas decimais.

Arquivos em `data/generated/`: clientes.csv, contas.csv, transacoes.csv e
manifest.json com contagens, semente e hashes SHA-256. A mesma semente e parâmetros
produzem os mesmos dados. Gerar novamente no mesmo destino substitui apenas os
arquivos do gerador; use `--output` para preservar um lote anterior.

```powershell
python -m src.generate_data --output data/generated/outro_lote --seed 43 --year 2024
```

## Arquitetura e regras

CSV → Oracle RAW → STAGING → modelo dimensional → Power BI.
Veja [a modelagem](docs/architecture.md).

As seis inconsistências conhecidas são duplicata exata, valor negativo, conta
inexistente, data inválida, status vazio e identificador repetido com conteúdo
divergente. Os testes atuais verificam a geração desses cenários e a
reprodutibilidade; ainda não são testes do ETL ou da idempotência no Oracle.

## Estrutura

- src/generate_data.py: geração determinística.
- tests/test_generate_data.py: verificação dos dados gerados.
- docs/architecture.md: camadas, chaves e decisões de modelagem.
- .env.example: nomes das variáveis, sem senhas.
- requirements.txt: Pandas, python-oracledb e pytest para as próximas etapas.

## Próximas fases

2. Inspecionar o laboratório, apresentar DDL, obter autorização e criar objetos exclusivos.
3. Implementar carga em lotes, transações e logs com Python e Pandas.
4. Implementar qualidade, conciliação, idempotência e testes de integração opcionais.
5. Criar SQL analítico, views e guia Power BI com medidas DAX.
6. Preparar execução Linux, cron documentado e revisão para GitHub.

Nenhum agendamento será ativado automaticamente. Não utilizar DROP ou TRUNCATE
em objetos existentes. Credenciais e dados gerados ficam fora do Git.

## O que explicar em uma entrevista

RAW mantém evidência da origem; STAGING separa registros válidos; o modelo
dimensional simplifica indicadores. Semente fixa permite reproduzir defeitos.
Precisão decimal evita erros financeiros. Testar cenários conhecidos permite
avaliar o tratamento de erros quando o ETL for implementado.
