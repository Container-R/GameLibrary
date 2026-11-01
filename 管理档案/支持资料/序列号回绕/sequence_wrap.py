"""Finite teaching model, not a transport protocol or chronology detector."""

EQUAL = 'equal'
FORWARD = 'forward'
BACKWARD = 'backward'
AMBIGUOUS = 'ambiguous'


def validate_field(value, bits):
    if type(bits) is not int or not 2 <= bits <= 16:
        raise ValueError('bits must be an integer from 2 through 16')
    if type(value) is not int or not 0 <= value < (1 << bits):
        raise ValueError('value must be an integer within the declared field')


def compare(candidate, reference, bits):
    """Classify one pair in one declared bit domain. Not a total order.

    The RFC leaves half-space ordering undefined. This model deliberately
    returns an explicit ambiguous label instead of choosing an ordering.
    """
    validate_field(candidate, bits)
    validate_field(reference, bits)
    distance = (candidate - reference) % (1 << bits)
    half = 1 << (bits - 1)
    if distance == 0:
        return EQUAL
    if distance < half:
        return FORWARD
    if distance == half:
        return AMBIGUOUS
    return BACKWARD


WINDOW_SIZE = 4096
WINDOWS = 16
FREE_WINDOWS = 8


def reliable_window_not_rejected(candidate, current):
    """Model ONLY ENet v1.3.18's initial incoming window guard.

    Scope: ordinary reliable commands and an already-selected valid channel.
    True is not admission, acknowledgement, dispatch, delivery or freshness.
    No peer state, duplicates, queue, allocation, fragments or transport here.
    """
    validate_field(candidate, 16)
    validate_field(current, 16)
    candidate_window = candidate // WINDOW_SIZE
    current_window = current // WINDOW_SIZE
    if candidate < current:
        candidate_window += WINDOWS
    return current_window <= candidate_window < current_window + FREE_WINDOWS - 1
