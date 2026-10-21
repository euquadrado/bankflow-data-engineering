"""Gera dados inteiramente fictícios e reproduzíveis; não acessa o banco."""
import argparse
import csv
import hashlib
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

TYPES = ("PIX", "TED", "DEPOSITO", "PAGAMENTO", "TRANSFERENCIA")
STATUSES = ("APROVADO", "PENDENTE", "CANCELADO", "REJEITADO")


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def generate(output, seed=42, year=2025, customers=1000, accounts=1500, transactions=50000):
    if customers < 1 or accounts < customers or transactions < 6:
        raise ValueError("Exige clientes >= 1, contas >= clientes e transações >= 6")
    start = datetime(year, 1, 1)
    seconds = int((datetime(year + 1, 1, 1) - start).total_seconds())
    rng = random.Random(seed)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    clients = [{"cliente_id": i, "nome": f"Cliente Ficticio {i:04d}",
                "segmento": rng.choice(("VAREJO", "ALTA_RENDA", "DIGITAL"))}
               for i in range(1, customers + 1)]
    bank_accounts = [{"conta_id": i, "cliente_id": ((i - 1) % customers) + 1,
                      "tipo_conta": rng.choice(("CORRENTE", "POUPANCA"))}
                     for i in range(1, accounts + 1)]
    rows = []
    for i in range(1, transactions + 1):
        cents = rng.randint(100, 2500000)
        rows.append({"transacao_id": i, "conta_id": rng.randint(1, accounts),
                     "data_transacao": (start + timedelta(seconds=rng.randrange(seconds))).isoformat(),
                     "tipo": rng.choice(TYPES), "valor": f"{cents // 100}.{cents % 100:02d}",
                     "status": rng.choices(STATUSES, weights=(85, 5, 4, 6))[0]})
    # Seis linhas adicionais; preserva as 50.000 transações válidas originais.
    invalid = [dict(rows[i]) for i in range(6)]
    for i, row in enumerate(invalid):
        row["transacao_id"] = transactions + i + 1
    invalid[0] = dict(rows[0])  # Duplicata exata.
    invalid[1]["valor"] = "-50.00"
    invalid[2]["conta_id"] = accounts + 1
    invalid[3]["data_transacao"] = f"{year}-02-30T12:00:00"
    invalid[4]["status"] = ""
    invalid[5]["transacao_id"] = rows[5]["transacao_id"]  # ID repetido, conteúdo divergente.
    invalid[5]["valor"] = "999999.99"
    rows.extend(invalid)
    write_csv(output / "clientes.csv", list(clients[0]), clients)
    write_csv(output / "contas.csv", list(bank_accounts[0]), bank_accounts)
    write_csv(output / "transacoes.csv", list(rows[0]), rows)
    manifest = {"seed": seed, "ano": year, "clientes": customers, "contas": accounts,
                "transacoes_validas": transactions, "linhas_transacoes": len(rows),
                "inconsistencias_injetadas": 6,
                "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(output.glob("*.csv"))}}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/generated"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--year", type=int, default=2025)
    args = parser.parse_args()
    print(json.dumps(generate(args.output, args.seed, args.year), indent=2))
