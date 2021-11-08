class MetricDataModel:
    """metric实体类.

    Attributes:
        name: str，metric名称.
        label: dict，metric所附带的标识属性.
        sample: dict，metric的数据点，包含以下两个字段:
        - timestamp: list，
        - value: list,
    """
    def __init__(self):
        self.name = ''
        self.label = {
            'unit': '',
            'type': ''
        }
        self.sample = {
            'timestamp': [],
            'value': []
        }
