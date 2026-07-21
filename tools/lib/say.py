"""The build pipeline's one voice (see docs/LOGGING.md, the contract this file implements).

Every line the tools print goes through here so it carries the same tag and one verb from
the closed set below; bare print() anywhere else under tools/ is a contract violation
(LogContractTests source-scans for it). Three calls:

    say(verb, msg)     an ordinary progress line
    warn(verb, msg)    something odd but survivable; prefixed WARN:, run continues
    fail(verb, msg)    a hard stop; prefixed FAIL:, printed to stderr, exits 1

fail() accepts a multi-line msg: the first line gets the FAIL: prefix, the rest print
indented under it, every line tagged (so a grep for the tag still catches the details).

VERBS is pinned one-for-one against the glossary table in docs/LOGGING.md by
LogContractTests; change both together or the test gate goes red.
"""
import sys

TAG = "[Offensive Chemist]"

VERBS = ("gate", "generate", "names", "abilities", "icons", "test", "deploy", "package")


def _emit(stream, verb, text):
    if verb not in VERBS:
        raise ValueError(f"unknown log verb {verb!r}; the closed set is {VERBS} (see docs/LOGGING.md)")
    print(f"{TAG} [{verb}] {text}", file=stream, flush=True)


def say(verb, msg):
    _emit(sys.stdout, verb, msg)


def warn(verb, msg):
    _emit(sys.stdout, verb, f"WARN: {msg}")


def fail(verb, msg):
    lines = str(msg).splitlines() or [""]
    _emit(sys.stderr, verb, f"FAIL: {lines[0]}")
    for extra in lines[1:]:
        _emit(sys.stderr, verb, f"  {extra}")
    sys.exit(1)
