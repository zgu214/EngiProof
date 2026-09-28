"""Run the unittest suite and report failures as GitHub annotations (job logs are not always readable)."""
import sys
import unittest


def _escape(text: str) -> str:
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def main() -> int:
    suite = unittest.defaultTestLoader.discover("tests")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    for kind, items in (("failure", result.failures), ("error", result.errors)):
        for test, trace in items:
            print(f"::error title=test-{kind}::{_escape(test.id() + chr(10) + trace[-1500:])}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
