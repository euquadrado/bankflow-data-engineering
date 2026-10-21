import csv
from datetime import datetime
from decimal import Decimal

from src.generate_data import generate


def test_generation_is_reproducible(tmp_path):
    first = generate(tmp_path / "a", customers=10, accounts=15, transactions=100)
    second = generate(tmp_path / "b", customers=10, accounts=15, transactions=100)
    assert first == second


def test_injected_errors_and_valid_base(tmp_path):
    generate(tmp_path, customers=10, accounts=15, transactions=100)
    with (tmp_path / "transacoes.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 106
    assert len({r["transacao_id"] for r in rows[:100]}) == 100
    for row in rows[:100]:
        assert Decimal(row["valor"]) > 0
        assert 1 <= int(row["conta_id"]) <= 15
        assert datetime.fromisoformat(row["data_transacao"]).year == 2025
        assert all(row.values())
    assert rows[100] == rows[0]
    assert Decimal(rows[101]["valor"]) < 0
    assert int(rows[102]["conta_id"]) == 16
    assert rows[103]["data_transacao"] == "2025-02-30T12:00:00"
    assert rows[104]["status"] == ""
    assert rows[105]["transacao_id"] == rows[5]["transacao_id"]
    assert rows[105] != rows[5]
