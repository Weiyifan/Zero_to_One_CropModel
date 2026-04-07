# SimpleCropModel

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
