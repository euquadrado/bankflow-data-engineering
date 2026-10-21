# Modelagem proposta — Fase 1

CSV → RAW → STAGING → ANALYTICS → Power BI.

RAW preserva cada linha original, inclusive erros. STAGING contém apenas registros
válidos. ANALYTICS organiza os dados para consultas e indicadores. Essas são
camadas lógicas em um schema exclusivo BANKFLOW no PDB ORCLPDB1.

| Objeto planejado | Chave e relacionamento |
| --- | --- |
| BF_RAW_CLIENTES / CONTAS / TRANSACOES | PK (lote_id, numero_linha); campos de origem textuais |
| BF_STG_CLIENTES | PK cliente_id |
| BF_STG_CONTAS | PK conta_id; FK cliente_id → clientes |
| BF_STG_TRANSACOES | PK transacao_id; FK conta_id → contas |
| BF_DIM_CLIENTE | PK cliente_id; atributos fictícios do cliente |
| BF_DIM_TEMPO | PK data_id (YYYYMMDD); data, ano, mês |
| BF_DIM_TIPO_TRANSACAO | PK tipo_id; descrição única |
| BF_FATO_TRANSACOES | PK transacao_id; FKs cliente_id, data_id, tipo_id; conta_id, valor, status |
| BF_LOG_EXECUCOES | PK execucao_id; lote, início, fim, status e contagens |
| BF_ERROS_QUALIDADE | PK erro_id; execução, linha, regra e motivo |

Grão da fato: uma transação válida, incluindo status bancários não aprovados.
Rejeição bancária e rejeição de qualidade são conceitos diferentes.
Volume financeiro movimentado deverá considerar apenas status APROVADO.
Não modelamos saldo nem partidas contábeis nesta versão.

Valores serão NUMBER(18,2) no Oracle e Decimal no Python; nunca float.
Datas inválidas devem chegar à RAW como texto, para permitir auditoria.
Índices planejados: FKs das contas, transações e fato; evitar índices redundantes
sobre PKs. DDL e privilégios serão detalhados na Fase 2 antes de execução.

Idempotência planejada: hash do conteúdo identifica o lote, unicidade identifica
transações. Reexecução do lote concluído não recarrega dados; um ID com conteúdo
divergente será rejeitado e registrado. A implementação pertence às Fases 3–4.
