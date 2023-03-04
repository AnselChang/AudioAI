from enum import Enum

DEBUG = 1
RELEASE = 2

# Print things conditionally, depending on level of debug
class Logger:

    def __init__(self, globalMode):
        self.globalMode = globalMode

    def log(self, mode, message: str):
        if self.globalMode == DEBUG or self.globalMode == mode:
            print(message)