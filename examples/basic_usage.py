"""
基础使用示例 - 展示SimpleCropModel的基本功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from simple_crop_model import CropParameters, SimpleCropModel, generate_weather
from simple_crop_model.utils import print_summary

def main():
    # 1. 创建作物参数 (使用预定义的玉米参数)
    params = CropParameters.maize()
    print(f"作物: {params.crop_name}")
    print(f"基础温度: {params.base_temp}°C")
    
    # 2. 生成气象数据 (模拟夏季120天)
    weather = generate_weather(start_day=120, days=150, base_temp=20)
    
    # 3. 初始化模型
    model = SimpleCropModel(params)
    
    # 4. 运行模拟
    print("\n运行模拟...")
    results = model.run(weather, verbose=True)
    
    # 5. 输出结果
    print_summary(results)
    
    # 6. 保存详细数据到CSV (可选)
    import pandas as pd
    df = pd.DataFrame(results['daily_data'])
    df.to_csv('simulation_output.csv', index=False)
    print("\n详细数据已保存到 simulation_output.csv")

if __name__ == "__main__":
    main()
