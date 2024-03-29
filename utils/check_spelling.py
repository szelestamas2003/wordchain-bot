import subprocess


def check_spelling(word: str, lang: str):
    result = subprocess.run(f"echo {word} | hunspell -d {lang}", shell=True, capture_output=True)
    if len(result.stderr) == 0:
        return result.stdout.decode("utf-8").splitlines()[1][0] in "*&"
    else:

        return False
