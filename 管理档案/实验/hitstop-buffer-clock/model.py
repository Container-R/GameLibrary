"""A single window check and three age policies; no native input pipeline."""
from dataclasses import dataclass

FREEZE_START, FREEZE_END = 80, 145
CHECK, LIMIT = 155, 55


@dataclass(frozen=True)
class Input:
    event_ms: int
    delivered_ms: int


def action_ms(wall_ms):
    frozen_so_far = max(0, min(wall_ms, FREEZE_END) - FREEZE_START)
    return wall_ms - frozen_so_far


def check(req, policy):
    # The single check is allowed only once CHECK is reached and this request
    # is in the inbox. Later delivery cannot retroactively populate the inbox.
    if req.delivered_ms > CHECK:
        return (None, "undelivered")
    if policy == "event-wall":
        age = CHECK - req.event_ms
    elif policy == "receipt-wall":
        age = CHECK - req.delivered_ms
    elif policy == "event-action":
        age = action_ms(CHECK) - action_ms(req.event_ms)
    else:
        raise ValueError(policy)
    return (age, "consumed" if age < LIMIT else "expired")


if __name__ == "__main__":
    policies = ("event-wall", "receipt-wall", "event-action")
    test_cases = [
        (Input(75, 150), [(80, "expired"), (5, "consumed"), (15, "consumed")]),
        (Input(85, 86), [(70, "expired"), (69, "expired"), (10, "consumed")]),
        (Input(85, 145), [(70, "expired"), (10, "consumed"), (10, "consumed")]),
        (Input(100, 101), [(55, "expired"), (54, "consumed"), (10, "consumed")]),
        (Input(105, 106), [(50, "consumed"), (49, "consumed"), (10, "consumed")]),
        (Input(105, 156), [(None, "undelivered")] * 3),
    ]
    assert action_ms(CHECK) == 90
    assert action_ms(85) == action_ms(105) == 80
    assert action_ms(CHECK) - action_ms(75) == 15
    assert action_ms(CHECK) - action_ms(150) == 5
    assert 5 < 12 <= 15
    for req, expected in test_cases:
        actual = [check(req, policy) for policy in policies]
        assert actual == expected, (req, actual, expected)
        details = " | ".join(
            f"{p}={age if age is not None else '-'}:{status}"
            for p, (age, status) in zip(policies, actual)
        )
        print(f"event={req.event_ms} receipt={req.delivered_ms} check={CHECK} | {details}")
