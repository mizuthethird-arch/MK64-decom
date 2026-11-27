# Secrets and signing identity

This page lists every secret the project will need, where each lives, who owns it, how it is rotated and what happens if it is missing or leaked. No secret is stored in this repository, in any artifact, or in this page.

## The rule

| Rule | Meaning |
|---|---|
| No secret in the repository | not in code, configuration, tests, fixtures, documentation, commit messages, logs or images |
| No secret in a build | not baked into a container layer, a binary, a cache or an artifact |
| No secret in this page | this page names secrets; it never contains one, and every value here is a placeholder |
| The ROM is not a secret | the game image is not confidential material, but it is copyrighted data and is never committed either |

The last rule matters because it is easy to conflate the two. A secret must be *hidden*; the ROM must be *absent*. They are enforced by different checks: a secret scan for the first, and the ROM guards described in [assets.md](assets.md) for the second.

## Every secret the project needs

| Secret | Storage | Owner | Rotation | If missing or leaked: missing | If missing or leaked: leaked |
|---|---|---|---|---|---|
| Windows signing certificate and private key | the release secret store, never the tree | human owner | every 12 months, and immediately on any suspicion of exposure | the release is blocked; development builds are labelled and never published | revoke the certificate with the issuing authority, replace it, then re-sign every artifact still in the support window |
| Linux release signing key | the release secret store, never the tree | human owner | every 12 months, and immediately on suspicion | the release is blocked | revoke, republish the detached signature with the new key, and record the rotation in the release notes |
| CI token used by the release job | the CI secret store, scoped to the release environment | human owner | every 90 days | the release job refuses to run | rotate first, then review the job logs for unauthorised use |
| Azure Trusted Signing or EV certificate credentials | the release secret store, never the tree | human owner | per the issuer's schedule, and immediately on suspicion | signing is unavailable; the release is blocked | revoke with the issuer, rotate the credential, and re-sign |
| Future ROM-adjacent key material | nowhere until a task names a real need | human owner | not yet defined | not applicable yet | not applicable yet |
| Any token an agent needs | the CI secret store only, never a file | human owner | every 90 days | the job fails closed | rotate first, then audit |

The last two rows are deliberately vague: no ROM-adjacent key is needed today, and inventing a name or a storage location for one would be a fabricated fact. When a task establishes a real need, this table gains a concrete row.

The game image itself is **not a secret**. It is the player's own file, held where the player keeps it, and the project never obtains, stores or distributes one.

## What the scan must do

The scan runs as the **secret scan** job on every pull request. It blocks the pull request when it finds a secret.

| Requirement | Exact statement a reviewer can check |
|---|---|
| Pinned tool | gitleaks pinned by digest, never a floating tag |
| Working-tree scan | a working-tree scan runs on every pull request and blocks the merge on any finding |
| History scan | a full history scan runs only when `vars.MK64_HISTORY_SCAN` is set, because it is slow and only needed before a release or after a leak |
| Custom rule | a custom private-key-header rule flags a bare header line that starts `-----BEGIN`, names a key type, and ends `PRIVATE KEY-----`, because a truncated or copied header is still a leak. This page spells the header out in pieces on purpose: the contiguous form is itself a secret-shaped literal that push protection rejects |
| Failure behaviour | a finding fails the job and names the file and the rule; the job never reports success on zero scanned files |

A scan that passes because it scanned nothing is worse than no scan, so the job must also assert that it actually examined files.

## False positives that must not fail

A scanner that fails on a sha1 gets disabled within a week. These shapes are explicitly allowed and the scan must not report them:

| Allowed shape | Why |
|---|---|
| a sha1 or sha256 literal | the ROM pin and every recorded hash are published on purpose |
| a clearly named test fixture | a fixture labelled `test-fixture`, `example`, `placeholder`, `dummy` or `fake` is a fixture, not a secret |
| an example value in documentation | this page and [rom-contract.md](rom-contract.md) show shapes, never values |
| a base64 blob that is not assigned to a secret-shaped name | encoded data is not a secret by itself |

The rule set is proven against the fixtures in `src/tests/docs/test_secrets.py`.

## What to do when a secret leaks

| Step | Action |
|---|---|
| 1 | rotate the secret first, in the store, before touching anything else |
| 2 | remove it from the working tree |
| 3 | if it reached history, rewrite that history and force-push with the owner's approval |
| 4 | audit what the secret could reach, and record the audit |
| 5 | report the incident under the procedure in [legal.md](legal.md) |

Rotation comes first because a secret that is still valid while being removed is still leaked.

## Prose and executable

| Part of this page | Executable today |
|---|---|
| the secret table, the rotation rules and the leak procedure | prose |
| the false-positive allowlist and the detection rules | yes: `src/tests/docs/secret_scan.py` with `src/tests/docs/test_secrets.py` |
| the CI secret scan job | not yet implemented: the ci workflow does not carry a secret scan job yet, and the workflow files are outside the docs lane |

The scan rules are executable and tested; the CI job that runs gitleaks is being added by the toolkit lane. Until that job exists, nothing enforces this page automatically.

## Related

- [assets.md](assets.md): the no-assets rule and the guards that enforce it
- [legal.md](legal.md): the incident procedure if a secret or game data is exposed
- [release.md](release.md): the releases that depend on the signing keys
