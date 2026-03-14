from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CropParameters:
    """
    作物参数配置类
    
    包含作物生长发育、光合作用、生物量分配等全套参数
    
    Attributes:
        base_temp: 基础温度 (°C)，低于此温度不发育
        max_temp: 最高有效温度 (°C)，高于此温度按上限计算
        emerge_gdd: 出苗所需积温 (°C·day)
        flower_gdd: 开花所需积温 (°C·day)
        mature_gdd: 成熟所需积温 (°C·day)
        max_lai: 最大叶面积指数
        lai_growth_rate: LAI增长速率系数
        specific_leaf_area: 比叶面积 (m²/g)
        rue: 辐射利用效率 (g/MJ)
        light_extinction: 光 extinction coefficient
        partition_*: 各器官生物量分配系数列表 [营养期, 生殖早期, 成熟期]
    """
    
    # 发育参数
    base_temp: float = 10.0
    max_temp: float = 35.0
    emerge_gdd: float = 100.0
    flower_gdd: float = 800.0
    mature_gdd: float = 1600.0
    
    # 生长参数
    max_lai: float = 5.0
    lai_growth_rate: float = 0.08
    specific_leaf_area: float = 0.025
    
    # 光合参数
    rue: float = 3.0  # Radiation Use Efficiency
    light_extinction: float = 0.6
    
    # 分配参数 (按生育阶段: [营养期, 生殖期, 成熟期])
    partition_leaf: List[float] = field(default_factory=lambda: [0.5, 0.3, 0.0])
    partition_stem: List[float] = field(default_factory=lambda: [0.3, 0.3, 0.0])
    partition_root: List[float] = field(default_factory=lambda: [0.2, 0.2, 0.0])
    partition_grain: List[float] = field(default_factory=lambda: [0.0, 0.2, 1.0])
    
    # 可选的作物名称和描述
    crop_name: str = "Generic Crop"
    description: str = ""
    
    def __post_init__(self):
        """验证参数有效性"""
        if self.base_temp >= self.max_temp:
            raise ValueError("base_temp must be less than max_temp")
        if any(p < 0 or p > 1 for p in self.partition_leaf):
            raise ValueError("Partition coefficients must be between 0 and 1")
        if not (0.99 <= sum(self.partition_leaf) <= 1.01):
            raise ValueError("Partition coefficients should sum to 1.0")
    
    @classmethod
    def maize(cls) -> "CropParameters":
        """预定义的玉米参数"""
        return cls(
            crop_name="Maize",
            base_temp=8.0,
            max_temp=30.0,
            emerge_gdd=80,
            flower_gdd=1200,
            mature_gdd=2400,
            max_lai=5.5,
            lai_growth_rate=0.1,
            rue=4.0,
            light_extinction=0.65,
            partition_leaf=[0.45, 0.15, 0.0],
            partition_stem=[0.30, 0.25, 0.0],
            partition_root=[0.25, 0.10, 0.0],
            partition_grain=[0.0, 0.50, 1.0],
            description="Spring maize parameters optimized for temperate regions"
        )
    
    @classmethod
    def wheat(cls) -> "CropParameters":
        """预定义的冬小麦参数"""
        return cls(
            crop_name="Wheat",
            base_temp=0.0,
            max_temp=30.0,
            emerge_gdd=150,
            flower_gdd=800,
            mature_gdd=1600,
            max_lai=6.0,
            lai_growth_rate=0.09,
            rue=3.2,
            light_extinction=0.65,
            partition_leaf=[0.50, 0.20, 0.0],
            partition_stem=[0.30, 0.20, 0.0],
            partition_root=[0.20, 0.10, 0.0],
            partition_grain=[0.0, 0.50, 1.0]
        )
    
    @classmethod
    def rice(cls) -> "CropParameters":
        """预定义的水稻参数"""
        return cls(
            crop_name="Rice",
            base_temp=10.0,
            max_temp=35.0,
            emerge_gdd=100,
            flower_gdd=900,
            mature_gdd=1800,
            max_lai=7.0,
            lai_growth_rate=0.12,
            rue=2.8,
            light_extinction=0.55,  # 更直立叶片
            partition_leaf=[0.45, 0.15, 0.0],
            partition_stem=[0.30, 0.20, 0.0],
            partition_root=[0.25, 0.10, 0.0],
            partition_grain=[0.0, 0.55, 1.0]
        )
