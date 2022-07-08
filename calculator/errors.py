class InvalidValue(Exception):
    def __init__(self, string: str) -> None:
        super().__init__(
            "Received whitespace or an empty string."
            if string == ""
            else f'Term "{string}" is not a number.'
        )
