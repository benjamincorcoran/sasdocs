import logging

def format_logger(logger, context, logOut='sasdocs.log'):
    if not logger.handlers:
        logger_stream = logging.StreamHandler()
        logger_fmt = logging.Formatter(r'%(levelname)s:%(name)s: "%(path)s": %(message)s')
        logger_stream.setFormatter(logger_fmt)
        logger.setLevel(logging.INFO)
        logger.addHandler(logger_stream)
            
        logger_file = logging.FileHandler(logOut)
        logger_file.setLevel(logging.DEBUG)
        logger_file.setFormatter(logger_fmt)
        logger.addHandler(logger_file)

    return logging.LoggerAdapter(logger, context)
