"""
SimpleCropModel - 基于生理过程的作物生长模拟模型

该模型实现了：
- 积温(GDD)驱动的物候发育
- Beer-Lambert光截获定律
- 动态生物量分配
- 环境胁迫响应
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .parameters import CropParameters
from .core import SimpleCropModel, OptimizedCropModel
from .weather import generate_weather, WeatherDataLoader

__all__ = [
    "CropParameters",
    "SimpleCropModel", 
    "OptimizedCropModel",
    "generate_weather",
    "WeatherDataLoader"
]
