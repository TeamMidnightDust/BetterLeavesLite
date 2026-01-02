import os

def printGreen(out): print("\033[92m{}\033[00m".format(out))
def printCyan(out): print("\033[96m{}\033[00m" .format(out))
def printOverride(out): print(" -> {}".format(out))

def list_files_alphabetically(folder: str) -> list[str]:
    return sorted((file for file in os.listdir(folder) if not os.path.isdir(os.path.join(folder, file))), key=str.lower)
