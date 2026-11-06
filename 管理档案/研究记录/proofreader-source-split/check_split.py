"""Original synthetic grouping example; no model training or quality measurement."""
import json

LINES = {
    "A": ("请把钥匙交给守卫。", "请把钥匙交给守位。"),
    "B": ("桥边的灯已经亮了。", "桥边的灯已经凉了。"),
    "C": ("钟响以后再打开城门。", "钟响以候再打开城门。"),
    "D": ("先把地图收进背包。", "先把地图收进背抱。"),
}
ROWS = {
    (source, variant): {"source": source, "changed": variant, "text": text}
    for source, pair in LINES.items()
    for variant, text in enumerate(pair)
}


def describe(train_keys, test_keys):
    assert set(train_keys).isdisjoint(test_keys)
    assert set(train_keys) | set(test_keys) == set(ROWS)
    train = [ROWS[key] for key in train_keys]
    test = [ROWS[key] for key in test_keys]
    return {
        "train_rows": len(train),
        "test_rows": len(test),
        "train_changed_rows": sum(row["changed"] for row in train),
        "test_changed_rows": sum(row["changed"] for row in test),
        "shared_texts": sorted({r["text"] for r in train} & {r["text"] for r in test}),
        "shared_sources": sorted({r["source"] for r in train} & {r["source"] for r in test}),
    }


bad_train = [("A", 0), ("B", 1), ("C", 0), ("D", 1)]
bad_test = [("A", 1), ("B", 0), ("C", 1), ("D", 0)]
good_train = [(source, variant) for source in "AB" for variant in (0, 1)]
good_test = [(source, variant) for source in "CD" for variant in (0, 1)]
result = {
    "split_variants": describe(bad_train, bad_test),
    "split_sources": describe(good_train, good_test),
    "scope": "Synthetic identity and count checks only; no model, accuracy or natural-error assessment.",
}
for item in (result["split_variants"], result["split_sources"]):
    assert (item["train_rows"], item["test_rows"]) == (4, 4)
    assert (item["train_changed_rows"], item["test_changed_rows"]) == (2, 2)
    assert item["shared_texts"] == []
assert result["split_variants"]["shared_sources"] == list("ABCD")
assert result["split_sources"]["shared_sources"] == []
print(json.dumps(result, ensure_ascii=False, indent=2))
