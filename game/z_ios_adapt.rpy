# -*- coding: utf-8 -*-
# iOS 适配配置文件 - ADRIFT
# 将此文件放在 game/ 目录下，Ren'Py 会自动加载并覆盖原始配置
# 目标：完美适配 iPhone 横屏比例（19.5:9），完美填充屏幕
#
# 原理：Ren'Py 的样式在所有 init 块执行完毕后才构建，
# 因此在高优先级 init 中覆盖分辨率和 GUI 参数即可生效。

init 1 python hide:
    # ============================================================
    # 1. 分辨率覆盖 - iPhone 横屏比例
    # ============================================================
    # 原始: 1920x1080 (16:9 = 1.778:1)
    # 目标: 2436x1125 (iPhone X 系列横屏, 19.5:9 = 2.168:1)
    # 此比例与 iPhone 12/13/14/15/16 系列完全一致
    # Ren'Py 会自动缩放到设备物理分辨率
    import math
    config.screen_width = 2436
    config.screen_height = 1125

    # 重新计算 3D 透视参数（基于新宽度）
    fov = 75
    z = (2436 / 2) / math.tan(math.radians(fov / 2))
    config.perspective = (100.0, z, 100000.0)

    # 更新虚拟尺寸
    _preferences.virtual_size = (2436, 1125)
    _preferences.physical_size = None

    # ============================================================
    # 2. 移动端性能优化
    # ============================================================
    # 启用 OpenGL（iOS 原生支持）
    config.gl_enable = True

    # 增加图片缓存（移动端内存充足时提升加载速度）
    config.image_cache_size_mb = 512


init 2 python:
    # ============================================================
    # 3. GUI 变体覆盖 - small（手机端小屏适配）
    # ============================================================
    # 原始 small variant 基于 1920x1080
    # 新分辨率 2436x1125，宽度增加 26.9%，高度增加 4.2%
    # 策略：保持垂直尺寸不变，水平尺寸按比例扩展
    @gui.variant
    def small():
        # --- 文字大小（高度变化小，保持原尺寸确保可读性）---
        gui.text_size = 45
        gui.name_text_size = 54
        gui.notify_text_size = 38
        gui.interface_text_size = 45
        gui.button_text_size = 45
        gui.label_text_size = 51

        # --- 对话框适配 ---
        # 高度保持 360（垂直空间变化不大）
        gui.textbox_height = 360
        # 水平位置按宽度比例调整：120 * 1.269 ≈ 152
        gui.name_xpos = 152
        gui.dialogue_xpos = 170
        # 对话框宽度扩展：1650 * 1.269 ≈ 2094，留边距设为 2050
        gui.dialogue_width = 2050

        # --- 滑块 ---
        gui.slider_size = 54

        # --- 选项按钮 ---
        # 宽度扩展：1860 * 1.269 ≈ 2360，留边距设为 2300
        gui.choice_button_width = 2300
        gui.choice_button_text_size = 45

        # --- 导航间距 ---
        gui.navigation_spacing = 30
        gui.pref_button_spacing = 15

        # --- 历史记录 ---
        gui.history_height = 285
        # 宽度扩展：1035 * 1.269 ≈ 1313
        gui.history_text_width = 1313

        # --- 快捷按钮 ---
        gui.quick_button_text_size = 30

        # --- 存档槽位 ---
        # 横屏更宽，保持 2x2 确保每个槽位足够大，易于触控
        gui.file_slot_cols = 2
        gui.file_slot_rows = 2

        # --- NVL 模式适配 ---
        gui.nvl_height = 255
        # 名字区域：458 * 1.269 ≈ 581
        gui.nvl_name_width = 581
        gui.nvl_name_xpos = 620
        # 文本区域：1373 * 1.269 ≈ 1742
        gui.nvl_text_width = 1742
        gui.nvl_text_xpos = 657
        gui.nvl_text_ypos = 8
        # 思考气泡：1860 * 1.269 ≈ 2360
        gui.nvl_thought_width = 2360
        gui.nvl_thought_xpos = 38
        # NVL 按钮
        gui.nvl_button_width = 2360
        gui.nvl_button_xpos = 38

    # ============================================================
    # 4. 触控变体覆盖 - touch（触控优化）
    # ============================================================
    @gui.variant
    def touch():
        # 增大快捷按钮边框，提升触控体验
        gui.quick_button_borders = Borders(80, 25, 80, 0)

        # 增大按钮最小点击区域
        # iOS 人机界面指南建议最小 44pt = 132px @3x
        gui.button_borders = Borders(30, 20, 30, 20)
