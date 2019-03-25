
import keyboard
import re


def print_special(*x, end="\n"):
    print("\033[92m", end="")
    for elem in x:
        print(str(elem), end=" ")
    print(end=end)
    print("\033[0m", end="")
    return


def print_warning(*x, end="\n"):
    print("\033[93m", end="")
    for elem in x:
        print(str(elem), end=" ")
    print(end=end)
    print("\033[0m", end="")
    return


# Consider using file=sys.stderr
def print_error(*x, end="\n"):
    print("\033[31m", end="")
    for elem in x:
        print(str(elem), end=" ")
    print(end=end)
    print("\033[0m", end="")
    return


def check_quit():
    return keyboard.is_pressed("alt") and keyboard.is_pressed("q")


def clean_data(val):
    """ manual cleaning of potentially incorrectly recognized values """
    val = val.replace("o", "0")\
        .replace("c", "0")\
        .replace("d", "0")\
        .replace("l", "1")\
        .replace(",", "")
    # val = val.replace("e", "2")
    # val = val.replace("/", "7")
    # val = val.replace("t", "7")
    # val = val.replace("s", "9")
    return val


def find_regex(expression, text):
    regex = re.findall(expression, text)
    if regex:
        # transform regex from list of tuples to list
        if isinstance(regex[-1], tuple):
            regex = [regex[i][j] for i in range(0, len(regex)) for j in range(0, len(regex[i]))]
        # accept only the last non-empty match (eases up writing regex)
        while not regex[-1]:
            regex = regex[:-1]
            if not regex:
                return None
        return clean_data(regex[-1])
    return None


def is_close_match(s1, s2, tolerance=1, allow_different_length=True):
    """ returns whether or not two strings only differ by the number of tolerated characters """
    if s1 == s2:
        return True
    if not allow_different_length and len(s1) != len(s2):
        return False

    # exhausted = abs(len(s1) - len(s2))
    exhausted = 0
    for i in range(0, min(len(s1), len(s2))):
        if s1[i] != s2[i]:
            exhausted += 1
        if exhausted > tolerance:
            return False

    return exhausted <= tolerance


def close_match_in(match, text, tolerance=1):
    """ returns whether or not a string is found as a close match within a text """
    if match in text:
        return True
    if len(match) >= len(text):
        return is_close_match(match, text, tolerance=tolerance)

    for i in range(0, len(text) - len(match)):
        if is_close_match(match, text[i:i + len(match)]):
            return True

    return False
