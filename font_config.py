import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

def configure_font():
    """配置Matplotlib中文字体"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(BASE_DIR, 'NotoSansCJKsc-Regular.otf')
    
    # 如果存在本地字体文件，使用它
    if os.path.exists(font_path):
        try:
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.sans-serif'] = [font_prop.get_name()] + plt.rcParams['font.sans-serif']
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False
            return
        except Exception as e:
            print(f"加载本地字体失败: {e}")
    
    # 备选字体列表
    font_list = [
        'SimHei', 'Microsoft YaHei', 'DejaVu Sans',
        'PingFang SC', 'Hiragino Sans GB', 'WenQuanYi Micro Hei',
        'Noto Sans CJK SC', 'Source Han Sans SC', 'Noto Sans CJK JP'
    ]
    
    # 检查系统中可用的字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 选择第一个可用的字体
    for font_name in font_list:
        if font_name in available_fonts:
            plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False
            print(f"使用字体: {font_name}")
            return
    
    # 如果没有中文字体，使用默认方案
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False
    print("警告：未找到中文字体，可能显示方框")
