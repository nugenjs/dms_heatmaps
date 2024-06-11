import os

def listDirectoriesInPath(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]