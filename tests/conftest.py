"""Shared harness for the v0.9.9.5 red-phase guard tests (V09995-SOL-001 §12).

These tests are written BEFORE the modules they exercise. Per §12.1 a missing
module must produce a FAILURE with an actionable message, never a collection
ERROR -- a test that errors out proves nothing about the logic it claims to
guard. `require_module` and `require_file` enforce that.

Run via ./tests/run-all.sh (the only trusted runner; per-suite green counts
have historically been subsets).
"""
import importlib
import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V0995 = os.path.join(REPO_ROOT, 'deployment', 'v0.9.9.5')

# Where the implementation modules will land once written (§5.1, §8.1).
_MODULE_DIRS = (
    os.path.join(V0995, 'opt', 'd3kos', 'services', 'safehelm'),
    os.path.join(V0995, 'opt', 'd3kos', 'services'),
)
for _d in _MODULE_DIRS:
    if _d not in sys.path:
        sys.path.insert(0, _d)


def require_module(name, spec_ref):
    """Import a module under test, or FAIL (not error) with an actionable message.

    MUST be called from inside a test body, never from a fixture: pytest
    reports a fixture-time pytest.fail() as an ERROR, and §12.1 requires these
    guards to FAIL. Use `lazy_module` for a fixture-friendly wrapper, or a
    factory fixture that calls this when the test invokes it.
    """
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        pytest.fail(
            f'NOT YET IMPLEMENTED: {name}.py ({exc})\n'
            f'  Expected under: {_MODULE_DIRS[0]}\n'
            f'  Spec: V09995_SOLUTION_DESIGN.md {spec_ref}\n'
            f'  This is the §12 red-phase guard. Failing here is correct until '
            f'the module is written.',
            pytrace=False,
        )


class _LazyModule:
    """Defers import until first attribute access, i.e. until the test body runs.

    A fixture may return one of these safely: nothing is imported at setup
    time, so a missing module surfaces as a FAILURE inside the test rather
    than a setup ERROR. Attribute reads and writes both delegate to the real
    module, so monkeypatching through the proxy works.
    """

    __slots__ = ('_lm_name', '_lm_spec', '_lm_mod')

    def __init__(self, name, spec_ref):
        object.__setattr__(self, '_lm_name', name)
        object.__setattr__(self, '_lm_spec', spec_ref)
        object.__setattr__(self, '_lm_mod', None)

    def resolve(self):
        mod = object.__getattribute__(self, '_lm_mod')
        if mod is None:
            mod = require_module(object.__getattribute__(self, '_lm_name'),
                                 object.__getattribute__(self, '_lm_spec'))
            object.__setattr__(self, '_lm_mod', mod)
        return mod

    def __getattr__(self, item):
        return getattr(self.resolve(), item)

    def __setattr__(self, item, value):
        setattr(self.resolve(), item, value)


def lazy_module(name, spec_ref):
    """Fixture-safe handle on a module under test. Imports on first use."""
    return _LazyModule(name, spec_ref)


def require_file(relpath, spec_ref):
    """Read a config/unit file under deployment/v0.9.9.5, or FAIL with a message."""
    full = os.path.join(V0995, relpath)
    if not os.path.isfile(full):
        pytest.fail(
            f'NOT YET IMPLEMENTED: {relpath}\n'
            f'  Expected at: {full}\n'
            f'  Spec: V09995_SOLUTION_DESIGN.md {spec_ref}\n'
            f'  This is the §12 red-phase guard.',
            pytrace=False,
        )
    with open(full, encoding='utf-8') as fh:
        return fh.read()


class FakeClock:
    """Deterministic replacement for time.time() in state-machine tests."""

    def __init__(self, start=1_000_000.0):
        self.now = float(start)

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += float(seconds)
        return self.now


@pytest.fixture
def clock():
    return FakeClock()
