import re

from LLM_Collab_Module_Completion.utils.parse_completion import extract_method_snippets

# in repo root dir:
# PYTHONPATH=.. python -m pytest -q tests/test_parse_completion/test_extract_method_snippets.py

# PYTHONPATH=.. python -m pytest -s tests/test_parse_completion/test_extract_method_snippets.py


text1 = '''
class TimeUtils:
    """
    This is a time util class, including getting the current time and date, adding seconds to a datetime, converting between strings and datetime objects, calculating the time difference in minutes, and formatting a datetime object.
    """
    
    def __init__(self):
        """
        Get the current datetime
        """
        self.datetime = datetime.datetime.now()
    
    def get_current_time(self):
        """
        Return the current time in the format of '%H:%M:%S'
        :return: string
        >>> timeutils = TimeUtils()
        >>> timeutils.get_current_time()
        "19:19:22"
        """
        return time.strftime("%H:%M:%S", time.localtime())
    
    def add_seconds(self, seconds):
        """
        Add the specified number of seconds to the current time
        :param seconds: int, number of seconds to add
        :return: string, time after adding the specified number of seconds in the format '%H:%M:%S'
        >>> timeutils.add_seconds(600)
        "19:29:22"
        """
        return time.strftime("%H:%M:%S", time.localtime(time.time() + seconds))
    
    def get_minutes(self, string_time1, string_time2):
        """
        Calculate how many minutes have passed between two times, and round the results to the nearest
        :return: int, the number of minutes between two times, rounded off
        >>> timeutils.get_minutes("2001-7-18 1:1:1", "2001-7-18 2:1:1")
        60
        """
        time1 = datetime.datetime.strptime(string_time1, "%Y-%m-%d %H:%M:%S")
        time2 = datetime.datetime.strptime(string_time2, "%Y-%m-%d %H:%M:%S")
        return round((time2 - time1).total_seconds() / 60)
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
