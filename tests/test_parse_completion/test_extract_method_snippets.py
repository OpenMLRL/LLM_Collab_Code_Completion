import re

from LLM_Collab_Module_Completion.utils.parse_completion import extract_method_snippets

# in repo root dir:
# PYTHONPATH=.. python -m pytest -q tests/test_parse_completion/test_extract_method_snippets.py

# PYTHONPATH=.. python -m pytest -s tests/test_parse_completion/test_extract_method_snippets.py


text1 = '''
def A(self):
    pass
def A(self):
    pass
'''


def test_extract_method_snippets_on_text1_all_methods():
    # Collect all method names from text1
    allowed = set(re.findall(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text1, flags=re.M))
    print('=' * 50)
    print(len(allowed))
    print('=' * 50)
    # Run extraction
    result = extract_method_snippets(text1, allowed_methods=allowed)

    # Basic validations: all methods found and normalized def lines
    assert set(result.keys()) == allowed
    for name, src in result.items():
        assert src.startswith(f"def {name}(")


def _main():
    allowed = set(re.findall(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text1, flags=re.M))
    result = extract_method_snippets(text1, allowed_methods=allowed)

    ok = True
    if set(result.keys()) != allowed:
        print("Mismatch in methods:")
        print(" expected:", sorted(allowed))
        print(" actual:", sorted(result.keys()))
        ok = False
    for name, src in result.items():
        if not src.startswith(f"def {name}("):
            print(f"Snippet for {name} not normalized: startswith={src[:20]!r}")
            ok = False

    print("Methods found:", ", ".join(sorted(result.keys())))
    print("Status:", "OK" if ok else "FAILED")


if __name__ == "__main__":
    _main()
