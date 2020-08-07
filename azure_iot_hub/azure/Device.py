class Device:
    def __init__(self, name, kind="generic", function_url=None,
                 connection_string=None):
        self.name = name
        self.kind = kind
        self.device_name = f'{name}-{kind}'
        self.function_url = function_url
        self.connection_string = connection_string
