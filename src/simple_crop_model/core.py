import numpy as np
from typing import List, Dict, Tuple, Optional
from .parameters import CropParameters


class SimpleCropModel:
    """
    简单作物生长模型
    
    基于积温驱动的物候发育，结合Beer-Lambert光截获定律
    和动态生物量分配模拟作物生长发育过程。
    
    Example:
        >>> params = CropParameters.maize()
        >>> model = SimpleCropModel(params)
        >>> weather = generate_weather(days=150)
        >>> results = model.run(weather)
    """
    
    def __init__(self, params: Optional[CropParameters] = None):
        self.params = params or CropParameters()
        self.reset()
    
    def reset(self):
        """重置模型状态到初始值"""
        self.day = 0
        self.gdd = 0.0  # Growing Degree Days累计
        self.biomass_total = 0.0
        self.biomass_leaf = 0.0
        self.biomass_stem = 0.0
        self.biomass_root = 0.0
        self.biomass_grain = 0.0
        self.lai = 0.0  # Leaf Area Index
        self.height = 5.0  # 株高 cm
        self.stage = "播种"
        self.daily_data: List[Dict] = []
    
    def calculate_gdd(self, tmin: float, tmax: float) -> float:
        """
        计算每日生长度日 (GDD)
        
        GDD = max(0, min(Tavg, Tmax_limit) - Tbase)
        
        Args:
            tmin: 日最低温度 (°C)
            tmax: 日最高温度 (°C)
            
        Returns:
            当日GDD值
        """
        tavg = (tmin + tmax) / 2
        tavg = min(tavg, self.params.max_temp)
        return max(0.0, tavg - self.params.base_temp)
    
    def update_phenology(self):
        """根据累计GDD更新物候发育阶段"""
        if self.gdd < self.params.emerge_gdd:
            self.stage = "播种-出苗"
        elif self.gdd < self.params.flower_gdd:
            self.stage = "营养生长"
        elif self.gdd < self.params.mature_gdd:
            self.stage = "生殖生长"
        else:
            self.stage = "成熟"
    
    def get_partition_coefficients(self) -> Tuple[float, float, float, float]:
        """
        获取当前物候阶段的生物量分配系数
        
        Returns:
            (叶分配系数, 茎分配系数, 根分配系数, 籽粒分配系数)
        """
        if self.gdd < self.params.flower_gdd:
            idx = 0  # 营养生长期
        elif self.gdd < self.params.mature_gdd:
            idx = 1  # 生殖早期
        else:
            idx = 2  # 成熟期
            
        return (
            self.params.partition_leaf[idx],
            self.params.partition_stem[idx],
            self.params.partition_root[idx],
            self.params.partition_grain[idx]
        )
    
    def calculate_photosynthesis(self, solar_rad: float) -> float:
        """
        计算日同化量 (基于Monteith方程)
        
        使用Beer-Lambert定律计算光截获:
        Q_intercepted = Q_total * (1 - exp(-k * LAI))
        
        生物量增长:
        ΔW = RUE * Q_intercepted
        
        Args:
            solar_rad: 日总辐射 (MJ/m²/day)
            
        Returns:
            潜在生物量增长 (g/m²/day)
        """
        intercepted_rad = solar_rad * (
            1 - np.exp(-self.params.light_extinction * self.lai)
        )
        return self.params.rue * intercepted_rad
    
    def update_lai(self):
        """更新叶面积指数"""
        if self.stage == "营养生长":
            # 指数增长阶段，受最大LAI限制
            growth = self.lai * self.params.lai_growth_rate
            self.lai += growth
        elif self.stage == "生殖生长":
            # 稳定期后缓慢下降
            if self.lai > self.params.max_lai * 0.8:
                self.lai *= 0.995
        
        self.lai = min(self.lai, self.params.max_lai)
    
    def step(self, tmin: float, tmax: float, solar_rad: float,
             water_stress: float = 1.0, nitrogen_stress: float = 1.0,
             **kwargs) -> Dict:
        """
        执行单步模拟 (一天)
        
        Args:
            tmin: 最低温度 (°C)
            tmax: 最高温度 (°C)
            solar_rad: 太阳辐射 (MJ/m²)
            water_stress: 水分胁迫因子 (0-1)
            nitrogen_stress: 氮素胁迫因子 (0-1)
            
        Returns:
            当日状态字典
        """
        self.day += 1
        
        # 1. 计算积温
        daily_gdd = self.calculate_gdd(tmin, tmax)
        self.gdd += daily_gdd
        
        # 2. 更新物候
        self.update_phenology()
        
        # 3. 光合作用
        potential_biomass = self.calculate_photosynthesis(solar_rad)
        actual_biomass = potential_biomass * water_stress * nitrogen_stress
        
        # 4. 生物量分配
        p_leaf, p_stem, p_root, p_grain = self.get_partition_coefficients()
        
        self.biomass_leaf += actual_biomass * p_leaf
        self.biomass_stem += actual_biomass * p_stem
        self.biomass_root += actual_biomass * p_root
        self.biomass_grain += actual_biomass * p_grain
        
        self.biomass_total = (
            self.biomass_leaf + self.biomass_stem + 
            self.biomass_root + self.biomass_grain
        )
        
        # 5. 更新LAI
        if self.day == 1:
            self.lai = 0.1
        else:
            self.update_lai()
            if self.biomass_leaf > 0:
                self.lai = self.biomass_leaf * self.params.specific_leaf_area
        
        # 6. 更新株高
        if self.stage == "营养生长":
            self.height += 0.8 * water_stress
        
        # 记录数据
        daily_record = {
            'day': self.day,
            'doy': kwargs.get('doy', self.day),  # 年积日
            'gdd': self.gdd,
            'stage': self.stage,
            'lai': self.lai,
            'height': self.height,
            'total_biomass': self.biomass_total,
            'leaf': self.biomass_leaf,
            'stem': self.biomass_stem,
            'root': self.biomass_root,
            'grain': self.biomass_grain,
            'daily_growth': actual_biomass,
            'stress': water_stress * nitrogen_stress
        }
        self.daily_data.append(daily_record)
        return daily_record
    
    def run(self, weather_data: List[Dict], verbose: bool = False) -> Dict:
        """
        运行完整生育期模拟
        
        Args:
            weather_data: 气象数据列表，每项为包含tmin, tmax, solar_rad等的字典
            verbose: 是否打印进度信息
            
        Returns:
            包含最终生物量、产量、逐日数据的字典
        """
        self.reset()
        
        for i, weather in enumerate(weather_data):
            self.step(
                tmin=weather['tmin'],
                tmax=weather['tmax'],
                solar_rad=weather['solar_rad'],
                water_stress=weather.get('water_stress', 1.0),
                nitrogen_stress=weather.get('nitrogen_stress', 1.0),
                doy=weather.get('day', i+1)
            )
            
            # 检查成熟
            if self.gdd >= self.params.mature_gdd:
                if verbose:
                    print(f"作物于第{self.day}天成熟 (GDD={self.gdd:.1f})")
                break
        
        return self._compile_results()
    
    def _compile_results(self) -> Dict:
        """编译最终输出结果"""
        if not self.daily_data:
            raise RuntimeError("模型尚未运行，请先调用run()")
            
        return {
            'crop_name': self.params.crop_name,
            'final_biomass': self.biomass_total,
            'grain_yield': self.biomass_grain,
            'harvest_index': self.biomass_grain / self.biomass_total if self.biomass_total > 0 else 0,
            'max_lai': max([d['lai'] for d in self.daily_data]),
            'maturity_day': self.day,
            'total_gdd': self.gdd,
            'daily_data': self.daily_data
        }


class OptimizedCropModel(SimpleCropModel):
    """
    优化的作物生长模型
    
    改进点：
    1. 更真实的LAI衰老过程
    2. 温度胁迫响应（高温抑制）
    3. 叶片生物量再分配
    4. 更精确的株高增长算法
    """
    
    def __init__(self, params: Optional[CropParameters] = None):
        super().__init__(params)
        self.senescence_rate = 0.02
        self.leaf_weight_ratio = 0.15
    
    def update_lai(self, daily_growth: float = 0):
        """优化的LAI更新算法"""
        sla = 0.002  # m²/g, 典型比叶面积
        
        if self.stage == "播种-出苗":
            self.lai += 0.02 * daily_growth
        elif self.stage == "营养生长":
            # 逻辑斯蒂增长
            growth_factor = (1 - self.lai / self.params.max_lai) * self.params.lai_growth_rate
            self.lai += self.lai * growth_factor + 0.001 * daily_growth
        elif self.stage == "生殖生长":
            # 灌浆后期开始衰老
            mid_grain_fill = (self.params.flower_gdd + self.params.mature_gdd) / 2
            if self.gdd > mid_grain_fill:
                self.lai *= (1 - self.senescence_rate)
        
        self.lai = max(0.1, min(self.lai, self.params.max_lai))
    
    def step(self, tmin: float, tmax: float, solar_rad: float,
             water_stress: float = 1.0, nitrogen_stress: float = 1.0,
             **kwargs) -> Dict:
        """优化的时间步长计算"""
        self.day += 1
        
        # 积温计算
        daily_gdd = self.calculate_gdd(tmin, tmax)
        self.gdd += daily_gdd
        
        # 物候更新
        self.update_phenology()
        
        # 光合作用
        potential_biomass = self.calculate_photosynthesis(solar_rad)
        
        # 胁迫计算
        stress_factor = min(water_stress, nitrogen_stress)
        
        # 温度胁迫 (高温抑制光合)
        if tmax > 35:
            heat_stress = max(0, 1 - (tmax - 35) * 0.05)
            stress_factor *= heat_stress
        
        actual_biomass = potential_biomass * stress_factor
        
        # 生物量分配
        p_leaf, p_stem, p_root, p_grain = self.get_partition_coefficients()
        
        self.biomass_leaf += actual_biomass * p_leaf
        self.biomass_stem += actual_biomass * p_stem
        self.biomass_root += actual_biomass * p_root
        self.biomass_grain += actual_biomass * p_grain
        
        # 叶片衰老导致的损失 (仅在生殖生长后期)
        if self.stage == "生殖生长":
            mid_grain_fill = (self.params.flower_gdd + self.params.mature_gdd) / 2
            if self.gdd > mid_grain_fill:
                senescence_loss = self.biomass_leaf * 0.01
                self.biomass_leaf -= senescence_loss
        
        self.biomass_total = sum([
            self.biomass_leaf, self.biomass_stem,
            self.biomass_root, self.biomass_grain
        ])
        
        # LAI更新
        self.update_lai(actual_biomass)
        
        # 株高更新 (更真实的逻辑)
        if self.stage == "营养生长":
            self.height += 0.5 * np.sqrt(water_stress)
        elif self.stage == "生殖生长":
            self.height += 0.1
        
        # 记录
        record = {
            'day': self.day,
            'doy': kwargs.get('doy', self.day),
            'gdd': self.gdd,
            'stage': self.stage,
            'lai': self.lai,
            'height': self.height,
            'total_biomass': self.biomass_total,
            'leaf': self.biomass_leaf,
            'stem': self.biomass_stem,
            'root': self.biomass_root,
            'grain': self.biomass_grain,
            'daily_growth': actual_biomass,
            'stress': stress_factor
        }
        self.daily_data.append(record)
        return record
