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
git clone https://github.com/yourusername/simple-crop-model.git
cd simple-crop-model
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
