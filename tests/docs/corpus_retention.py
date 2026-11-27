"""Retention policy for the parity corpus.

The real corpus tool is built in a later phase and does not exist yet. This module is the policy it
must call: given the recorded scene sizes, it says what may be pruned and what it refuses to prune,
and it refuses outright when the corpus is over the ceiling.
"""

CEILING_BYTES = 20 * 1024 * 1024 * 1024
KEEP_DECIDED = "required by the release gate: never pruned"
REFUSE_CEILING = "corpus is over the ceiling: prune refused until the release-gate scenes are explained"
REFUSE_IMMUTABLE = "a release-gate scene may never be pruned"


def report(scenes):
    """Returns a dict describing the corpus against the retention policy.

    Each scene is a dict with name, bytes, and optional release_gate and recorded_at keys.
    The report names the largest scenes and the total against the ceiling.
    """
    total = sum(scene["bytes"] for scene in scenes)
    largest = sorted(scenes, key=lambda scene: scene["bytes"], reverse=True)[:5]
    return {
        "total_bytes": total,
        "ceiling_bytes": CEILING_BYTES,
        "over_ceiling": total > CEILING_BYTES,
        "largest_scenes": [(scene["name"], scene["bytes"]) for scene in largest],
        "protected": [scene["name"] for scene in scenes if scene.get("release_gate")],
    }


def plan_prune(scenes, free_bytes_needed):
    """Returns (names to prune, reasons refused); never returns a release-gate scene for pruning."""
    protected = [scene for scene in scenes if scene.get("release_gate")]
    prunable = sorted(
        (scene for scene in scenes if not scene.get("release_gate")),
        key=lambda scene: (scene["bytes"], scene["name"]),
    )

    freed = 0
    chosen = []
    for scene in prunable:
        if freed >= free_bytes_needed:
            break
        chosen.append(scene["name"])
        freed += scene["bytes"]

    refusals = []
    if freed < free_bytes_needed:
        refusals.append(REFUSE_CEILING)
    if any(name in chosen for name in (scene["name"] for scene in protected)):
        refusals.append(REFUSE_IMMUTABLE)
    return chosen, refusals
