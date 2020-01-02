import logging

def format_logger(logger, context):

    logger_stream = logging.StreamHandler()
    logger_fmt = logging.Formatter(r'%(levelname)s:%(name)s: "%(path)s": %(message)s')
    logger_stream.setFormatter(logger_fmt)
    logger.setLevel(logging.INFO)
    logger.addHandler(logger_stream)

    return logging.LoggerAdapter(logger, context)