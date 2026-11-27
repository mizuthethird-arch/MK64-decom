"""Handover notes: every settled contract names producer, consumer, decisions and open questions.

A contract is settled when its producer has written down what the consumer must rely on. A handover
note that is missing any of the four fields is rejected, and each rejection names the exact reason.
"""

REQUIRED_FIELDS = ("producer", "consumer", "settled_decisions", "open_questions")


def validate_note(contract_id, note):
    """Returns the list of reasons this note is rejected; empty means the note is complete."""
    if not isinstance(note, dict):
        return [f"{contract_id}: note is not a mapping, got {type(note).__name__}"]

    reasons = []
    for field in REQUIRED_FIELDS:
        value = note.get(field)
        if value is None:
            reasons.append(f"{contract_id}: missing field {field}")
        elif isinstance(value, str) and not value.strip():
            reasons.append(f"{contract_id}: field {field} is empty")
        elif isinstance(value, (list, tuple)) and len(value) == 0 and field != "open_questions":
            reasons.append(f"{contract_id}: field {field} is empty")
    return reasons


def validate_handovers(notes):
    """Returns every rejection across a mapping of contract id to note."""
    reasons = []
    for contract_id in sorted(notes):
        reasons.extend(validate_note(contract_id, notes[contract_id]))
    return reasons
