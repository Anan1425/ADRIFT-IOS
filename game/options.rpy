init python:
    # 游戏基本信息
    config.name = "ADRIFT"
    config.version = "1.0"

    # 构建配置
    build.name = "adrift"
    build.executable_name = "adrift"

    # 音频
    config.has_sound = True
    config.has_music = True
    config.has_voice = True

    # 转场效果
    config.enter_transition = dissolve
    config.exit_transition = dissolve
    config.intra_transition = dissolve

    # 窗口
    config.window = "auto"
    config.window_show_transition = Dissolve(.2)
    config.window_hide_transition = Dissolve(.2)

    # 存档目录
    config.save_directory = "adrift_02-1775894988"

    # 窗口图标
    config.window_icon = "gui/window_icon.png"

    # 主菜单音乐
    config.main_menu_music = "audio/bgm_5.mp3"


# 构建分类规则
build.classify('**~', None)
build.classify('**.bak', None)
build.classify('**/.**', None)
build.classify('**/#**', None)
build.classify('**/thumbs.db', None)
build.classify('**.rpy', None)
build.classify('**.save', None)

build.classify('game/**.png', 'archive')
build.classify('game/**.jpg', 'archive')
build.classify('game/**.rpyc', 'archive')
build.classify('game/**.mp3', 'archive')
build.classify('game/**.ttf', 'archive')

build.documentation('*.html')
build.documentation('*.txt')
