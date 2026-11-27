# The 100% Rust rule

Every shipped crate is Rust. The transpiler and all tooling are Rust. The only C++ in this repository is the frozen oracle, built with CMake, and it never ships.

## The rule

| Section | Language | Ships |
|---|---|---|
| Every crate under `rust/` | Rust only | Yes |
| The transpiler and all tooling | Rust only | No, but they are still Rust |
| The frozen oracle under `oracle/` | C++ only, built with CMake | Never shipped |

"No C++ in a shipped artifact" is literal. A shipped binary may not contain a single C or C++ object, whether it came from a crate, a vendored library, a build script or a system library that was statically linked.

## The single exception

The frozen oracle is the one and only C++ in this repository.

| Property | Value |
|---|---|
| What it is | the decompilation, frozen by commit, built with CMake, used to record reference frames, audio and save images |
| Where it lives | `oracle/` |
| Language | C and C++ |
| Ships | Never. It is a measurement instrument, not a product. |
| Allowed to appear in a release | No, in any form |

Any second exception requires a written decision from the owner. There is no implicit exception for convenience libraries, build dependencies or platform glue.

## The check that proves it

A reviewer or CI job must fail the build when a C or C++ object reaches a shipped artifact. The check has two halves, and both must hold.

### Half one: the dependency tree is all Rust

Every crate that the shipped binary links must be resolved from the workspace or a registry as Rust source. No crate may build and link C or C++ through a `-sys` crate or a `cc` build dependency.

| What it inspects | What fails |
|---|---|
| `cargo tree` for the shipped package | any package whose build script compiles C or C++ |
| the workspace manifests | any `-sys` crate that is not on a reviewed allowlist |
| the lockfile | any package name that is not verifiable and maintained |

### Half two: the linked binary has no foreign objects

The linked binary itself is inspected, not the manifests.

| What it inspects | What fails |
|---|---|
| the symbols of the shipped binary | any symbol introduced by C or C++ that is not part of the C runtime the platform provides |
| the dynamic dependency list | any shared library that is not a platform system library |
| the build output directory | any `.o` or `.a` under `rust/` that the link consumed |

The exact command a reviewer runs:

```sh
# Fail when a C or C++ object reaches a shipped artifact.
# Exit 0 means the artifact is all Rust; any other exit code means fail.
set -eu
binary="$1"

# 1. no C++ runtime symbol may be present in the shipped binary
if nm -C "$binary" | grep -E '(_Z|std::|__cxa_|__gxx_)'; then
  echo "FAIL: the shipped binary contains C++ symbols" >&2
  exit 1
fi

# 2. the binary must not depend on a C or C++ runtime library
if ldd "$binary" | grep -E 'libstdc\+\+|libgcc_s'; then
  echo "FAIL: the shipped binary links a C or C++ runtime" >&2
  exit 1
fi

echo "OK: $binary is all Rust"
```

The rule that makes this command correct: a C++ object leaves C++ symbols (`_Z` mangling, `std::`, `__cxa_`, `__gxx_`) and a dependency on `libstdc++` or a non-platform `libgcc_s` behind it. A pure Rust binary has neither.

## Specification, not yet implemented

This page is a specification. `rust/`, `oracle/` and every `Cargo.toml` do not exist yet, so the command above has nothing to inspect and nothing runs it.

| Part of this page | Executable today |
|---|---|
| the rule and the single exception | prose |
| the two halves of the check | prose |
| the exact command above | specification, not yet implemented: it needs a built binary, and none exists yet |

This is the same split that [rom-contract.md](rom-contract.md) records for the importer. When the first shipped crate is built, this command becomes the CI gate for it, and the page is updated to say so. Until then, a reviewer is expected to run it by hand against any artifact that is proposed for shipping.

The check belongs in the release job, not the fast unit job, because it needs a linked binary. A breach blocks the release rather than the merge.

## What this rule does not claim

| Not claimed | Why |
|---|---|
| that the decompilation is Rust | the decompilation is C and C++, frozen as the oracle, and it never ships |
| that no C is linked at all | the C runtime the platform provides is unavoidable and is not counted as a shipped C object |
| that the toolchain is distributed | the toolchain builds the product; it is not part of it |

## Related

- [scope.md](scope.md): what the rebuild ships and the three deliverables
- [legal.md](legal.md): the legal, asset and key policy
- [assets.md](assets.md): the detailed no-assets policy
