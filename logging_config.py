from loguru import logger

logger.add("logs/app.log", rotation="500 MB")
