import logging

class ExtraFormatter(logging.Formatter):
    """Custom formatter to append 'extra' fields to the log message."""
    def format(self, record):
        # Define the standard attributes we want to skip when looking for 'extra' data
        standard_attrs = (
            'args', 'asctime', 'created', 'exc_info', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs', 'message',
            'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated',
            'stack_info', 'thread', 'threadName'
        )
        
        # Get the base formatted message
        log_msg = super().format(record)
        
        # Extract extra fields by filtering out standard record attributes
        extra_data = {k: v for k, v in record.__dict__.items() if k not in standard_attrs and not k.startswith('_')}
        
        if extra_data:
            return f"{log_msg} | {extra_data}"
        return log_msg

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if getattr(logger, "_configured", False):
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    
    # Use our new Custom Formatter
    formatter = ExtraFormatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False
    logger._configured = True

    return logger