"""Scalar inheritance model, not the Unity prefab serialization engine."""
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Layer:
    name: str
    radius: str | None = None
    source: "Layer | None" = None

    def effective(self):
        if self.radius is not None:
            return Decimal(self.radius), self.name
        if self.source is None:
            raise ValueError(f"{self.name}: no radius in source chain")
        return self.source.effective()

base = Layer("BaseEnemy", "0.40")
patrol = Layer("Patrol", source=base)
scout = Layer("Scout", "0.35", base)
a = Layer("Scout-A", source=scout)
b = Layer("Scout-B", "0.30", scout)
layers = (patrol, scout, a, b)

def check(label, expected):
    actual = [layer.effective() for layer in layers]
    assert actual == [(Decimal(n), origin) for n, origin in expected], actual
    print(label + ": " + " | ".join(f"{v} [{k}]" for v, k in actual))

check("before", [("0.40","BaseEnemy"),("0.35","Scout"),("0.35","Scout"),("0.30","Scout-B")])
base.radius = "0.50"
check("update base", [("0.50","BaseEnemy"),("0.35","Scout"),("0.35","Scout"),("0.30","Scout-B")])
b.radius = None
check("revert scene only", [("0.50","BaseEnemy"),("0.35","Scout"),("0.35","Scout"),("0.35","Scout")])
b.radius = "0.30"
scout.radius = None
check("revert variant only", [("0.50","BaseEnemy"),("0.50","BaseEnemy"),("0.50","BaseEnemy"),("0.30","Scout-B")])
base.radius = "0.55"
check("second base update", [("0.55","BaseEnemy"),("0.55","BaseEnemy"),("0.55","BaseEnemy"),("0.30","Scout-B")])
