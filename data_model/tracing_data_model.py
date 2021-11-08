class TracingDataModel:
    """tracing（准确来说是span）实体类.

    Attributes:
        trace_id: str，记录调用过程的trace_id.
        span_id: str，记录调用过程的span_id.
        operation_name: str，操作的方法名.
        parent_span: str，父span_id.
        span_kind: str，span之间的关系类型，CHILD_OF或FOLLOWS_FROM.
        start_timestamp: int。span的开始时间.
        duration: int，span的执行时间.
        attribute: dict，span中提取的需要额外关注的关键字段.
        links: list，参考OpenTelemetry中的links，作为特殊调用情况的扩展（还没涉及过）.
        events: list，记录调用过程中发生的一些事件.
    """

    def __init__(self):
        self.trace_id = ''
        self.span_id = ''
        self.operation_name = ''
        self.parent_span = ''
        self.span_kind = ''
        self.start_timestamp = 0
        self.duration = 0
        self.attribute = dict()
        self.links = []
        self.events = []
