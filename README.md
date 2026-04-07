# Zero_to_One_CropModel

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于生理过程的简单作物生长模拟模型，适用于产量预测、气候变化影响评估和农艺措施优化。

## 模型特点

- **积温驱动**: 基于Growing Degree Days (GDD)的物候发育模型
- **光截获模拟**: Beer-Lambert定律计算冠层光截获
- **生物量分配**: 动态分配同化物到叶、茎、根、籽粒
- **胁迫响应**: 模拟水分、氮素和温度胁迫的影响
- **模块化设计**: 易于扩展和参数校准

## 核心方程

1. **积温计算**: $GDD = \max(0, T_{avg} - T_{base})$
2. **光截获**: $Q_{int} = Q_{total} \times (1 - e^{-k \times LAI})$
3. **生物量增长**: $\Delta W = RUE \times Q_{int} \times f(stress)$
4. **生物量分配**: 按生育期动态分配至各器官

## 快速开始

### 安装

```bash
git clone https://github.com/Weiyifan/Zero_to_One_CropModel.git
cd Zero_to_One_CropModel
pip install -e .
```

### 基础用法

```python
from simple_crop_model import CropParameters, OptimizedCropModel, generate_weather

# 1. 使用预定义作物参数 (玉米、小麦、水稻)
params = CropParameters.maize()

# 2. 生成气象数据
weather = generate_weather(start_day=120, days=150)

# 3. 运行模拟
model = OptimizedCropModel(params)
results = model.run(weather)

# 4. 查看结果
print(f"产量: {results['grain_yield']:.0f} g/m²")
print(f"生物量: {results['final_biomass']:.0f} g/m²")
print(f"收获指数: {results['harvest_index']:.2f}")

```
### 自定义作物参数

```python
from simple_crop_model import CropParameters

# 创建自定义参数 (以大豆为例)
soybean_params = CropParameters(
    crop_name="Soybean",
    base_temp=10.0,
    flower_gdd=800,
    mature_gdd=1600,
    max_lai=6.0,
    rue=3.0,
    partition_leaf=[0.55, 0.20, 0.0],
    partition_stem=[0.25, 0.20, 0.0],
    partition_root=[0.20, 0.10, 0.0],
    partition_grain=[0.0, 0.50, 1.0]
)

```

### 预定义作物参数

| 作物 | 基础温度 | 开花GDD | 成熟GDD | RUE | Max LAI |
| -- | ---- | ----- | ----- | --- | ------- |
| 玉米 | 8°C  | 1200  | 2400  | 4.0 | 5.5     |
| 小麦 | 0°C  | 800   | 1600  | 3.2 | 6.0     |
| 水稻 | 10°C | 900   | 1800  | 2.8 | 7.0     |

## 加载人工设定天气数据

本文档介绍如何使用 `WeatherDataLoader` 从 CSV 文件或 DataFrame 加载人工设定的天气数据，替代随机生成的测试数据。

`WeatherDataLoader` 类提供了两种加载天气数据的方式：
- `from_csv()` - 从 CSV 文件加载
- `from_dataframe()` - 从 pandas DataFrame 加载

### 数据格式要求

#### 必需字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `day` | int | 年积日（一年中的第几天） |
| `tmin` | float | 每日最低温度（°C） |
| `tmax` | float | 每日最高温度（°C） |
| `solar_rad` | float | 太阳辐射（MJ/m²） |

#### 可选字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `rain` | float | 降雨量，用于计算水分胁迫系数 |

#### 输出格式

加载后的数据为字典列表，每个字典包含：

```python
{
    'day': int,              # 年积日
    'tmin': float,           # 最低温度
    'tmax': float,           # 最高温度
    'solar_rad': float,      # 太阳辐射
    'water_stress': float,   # 水分胁迫系数（1.0 表示无胁迫）
    'nitrogen_stress': 1.0   # 氮胁迫系数（固定为1.0）
}
```

### 加载实际天气使用方法

#### 1. 从 CSV 文件加载

##### 准备数据文件

创建 `weather_data.csv`：

```csv
day,tmin,tmax,solar_rad,rain
1,5.2,12.5,8.5,2.3
2,4.8,13.1,9.2,0.0
3,6.1,14.2,10.5,1.5
4,5.5,12.8,7.8,0.0
5,4.2,11.9,8.1,3.2
```

##### 加载代码

```python
from src.simple_crop_model.weather import WeatherDataLoader

# 加载天气数据
weather = WeatherDataLoader.from_csv('weather_data.csv')

# 查看第一天数据
print(weather[0])
# 输出: {'day': 1, 'tmin': 5.2, 'tmax': 12.5, 'solar_rad': 8.5, 
#        'water_stress': 1.0, 'nitrogen_stress': 1.0}
```

#### 2. 从 DataFrame 加载

```python
import pandas as pd
from src.simple_crop_model.weather import WeatherDataLoader

# 创建示例数据
df = pd.DataFrame({
    'day': [1, 2, 3, 4, 5],
    'tmin': [5.2, 4.8, 6.1, 5.5, 4.2],
    'tmax': [12.5, 13.1, 14.2, 12.8, 11.9],
    'solar_rad': [8.5, 9.2, 10.5, 7.8, 8.1],
    'rain': [2.3, 0.0, 1.5, 0.0, 3.2]
})

# 从 DataFrame 加载
weather = WeatherDataLoader.from_dataframe(df)
```

#### 3. 自定义列名

如果 CSV 文件的列名与默认不同，可以通过参数指定：

```python
weather = WeatherDataLoader.from_csv(
    'weather_data.csv',
    day_col='doy',           # 日期列名
    tmin_col='temp_min',     # 最低温度列名
    tmax_col='temp_max',     # 最高温度列名
    rad_col='radiation',     # 辐射列名
    rain_col='precipitation' # 降雨列名
)
```


#### 4.完整示例

```python
import pandas as pd
from src.simple_crop_model.weather import WeatherDataLoader
from src.simple_crop_model.crop import SimpleCropModel

# 1. 准备人工天气数据
weather_df = pd.DataFrame({
    'day': range(1, 31),
    'tmin': [5 + i*0.1 for i in range(30)],
    'tmax': [15 + i*0.2 for i in range(30)],
    'solar_rad': [10 + 5*(i%7)/7 for i in range(30)],
    'rain': [2.0 if i % 5 == 0 else 0.0 for i in range(30)]
})

# 2. 加载天气数据
weather = WeatherDataLoader.from_dataframe(weather_df)

# 3. 创建作物模型并运行模拟
crop = SimpleCropModel(weather=weather)
results = crop.simulate()

print(f"最终生物量: {results['biomass'][-1]:.2f} kg/ha")
```

#### 5.加载天气注意事项

1. **数据完整性**：确保 CSV 文件包含所有必需字段，否则会抛出 `ValueError`
2. **数据类型**：温度、辐射等数值应为数值类型
3. **日期连续性**：建议提供连续的日期序列（day 1, 2, 3...），但不是必须的
4. **胁迫系数**：目前仅支持基于降雨的简单水分胁迫计算，如需更复杂的胁迫模型，可在加载后手动修改 `water_stress` 值

### 项目结构

```plain
SimpleCropModel/
├── src/simple_crop_model/  # 核心源码
│   ├── core.py            # 模型类
│   ├── parameters.py      # 作物参数
│   ├── weather.py         # 气象工具
│   └── utils.py           # 辅助函数
├── examples/              # 使用示例
│   ├── basic_usage.py     # 基础示例
│   ├── maize_simulation.py # 玉米多场景对比
│   └── yield_analysis.py  # 敏感性分析
├── tests/                 # 单元测试
└── docs/                  # 文档
```

### 示例场景
#### 1. 不同播期产量比较
运行 examples/maize_simulation.py 查看不同播期对玉米产量和发育的影响。
#### 2. 参数敏感性分析
运行 examples/yield_analysis.py 分析RUE和LAI对产量的敏感性。

### 引用
如果你在工作中使用了本模型，请引用：

```plain
@software{simple_crop_model,
  author = {Weiyifan},
  title = {SimpleCropModel: A Process-based Crop Growth Simulation Model},
  year = {2026},
  url = {https://github.com/Weiyifan/Zero_to_One_CropModel}
}
```

### 许可证
MIT License - 详见 LICENSE 文件
