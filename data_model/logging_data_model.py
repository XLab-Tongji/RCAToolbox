class LoggingDataModel:
    """logging实体类.

    Attributes:
        timestamp: int，日志时间戳.
        trace_id: str，记录调用过程的trace_id.
        span_id: str，记录调用过程的span_id.
        severity_text: str，记录严重性文本，如INFO、WARN等.
        severity_number: int，记录日志的严重等级，相对标准的规范：
        - 1-4: Trace;
        - 5-8: DEBUG;
        - 9-12: INFO;
        - 13-16: WARN;
        - 17-20: ERROR;
        - 21-24: FATAL.
        name: str，日志名称.
        body: str，日志体.
        resource: dict，标识日志来源.
        attribute: dict，日志中提取出的需要额外关注的关键字段.
        type: 日志类型，确定日志的粒度.
    """

    def __init__(self):
        self.timestamp = 0
        self.trace_id = ''
        self.span_id = ''
        self.severity_text = ''
        self.severity_number = 9
        self.name = ''
        self.body = ''
        self.resource = dict()
        self.attribute = dict()
        self.type = ''
