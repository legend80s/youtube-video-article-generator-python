import logging
import sys

# 只配置一次
if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(asctime)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: None | str = None) -> logging.Logger:
    """获取日志记录器的快捷函数"""
    return logging.getLogger(name or __name__)


# 导出
__all__ = ["get_logger"]
