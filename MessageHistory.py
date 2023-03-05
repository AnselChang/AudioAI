import TextWindow

class MessageHistory:

    def __init__(self):
        self.window = TextWindow.TextWindow()
        self._messages = []

        self.promptAdded = False

    def addUserMessage(self, message: str, display: bool = True):
        self._messages.append({"role": "user", "content": message})

        if self.promptAdded:
            self.window.deleteLastLine()
            self.promptAdded = False

        if display:
            self.window.addText(f"YOU: {message}")

    def addAIMessage(self, message: str, display: bool = True):
        self._messages.append({"role": "assistant", "content": message})
        if display:
            self.window.addText(f"AI: {message}")

        if not self.promptAdded:
            self.promptAdded = True
            self.window.addText("~~speak to input a command to the AI~~")

    def get(self) -> list:
        return self._messages