# ADRIFT iOS 版

将 Ren'Py 视觉小说《ADRIFT》移植到 iPhone/iPad，完美适配 iOS 横屏比例（19.5:9），完美填充屏幕。

## 快速开始（无需 Mac）

使用 GitHub Actions 自动编译，全程在云端完成，你只需要下载最终的 `.ipa` 文件。

### 步骤

1. **注册 GitHub 账号**（如果还没有）：https://github.com

2. **创建新仓库**：
   - 点击 GitHub 右上角 `+` → `New repository`
   - 名称随意（如 `adrift-ios`）
   - 选择 `Public` 或 `Private`
   - 不要勾选 "Add a README file"
   - 点击 `Create repository`

3. **上传项目文件**：
   - 将本文件夹（`ADRIFT-iOS`）内的**所有文件和文件夹**上传到新仓库
   - 包括：`.github/`、`game/`、`scripts/`、`README.md` 等
   - 可以直接拖拽文件到 GitHub 网页上传

4. **触发自动编译**：
   - 上传完成后，点击仓库顶部的 `Actions` 标签
   - 你会看到一个名为 `Build iOS IPA` 的工作流正在运行
   - 等待约 10-20 分钟（首次运行需要下载 Ren'Py SDK）

5. **下载 IPA**：
   - 工作流运行完成后（显示绿色 ✓），点击进入该次运行
   - 拉到页面底部 `Artifacts` 区域
   - 点击 `ADRIFT-iOS-IPA` 下载
   - 解压得到 `ADRIFT.ipa` 文件

6. **安装到 iPhone**：
   - 参考下方「安装到 iPhone」章节

---

## 手动编译（有 Mac）

如果你有 Mac，可以使用一键脚本本地编译：

```bash
# 1. 确保已安装 Xcode
xcode-select --install

# 2. 进入 scripts 目录
cd scripts

# 3. 添加执行权限并运行
chmod +x build_ios.sh
./build_ios.sh
```

编译完成后，IPA 文件在 `output/ADRIFT.ipa`。

---

## 安装到 iPhone

### 方法一：Sideloadly（推荐，最简单）

1. 下载 Sideloadly：https://sideloadly.io
2. 安装并打开 Sideloadly
3. 用 USB 连接 iPhone 到电脑
4. 在 Sideloadly 中：
   - **iCloud/Apple ID**：输入你的 Apple ID
   - **IPA File**：选择下载的 `ADRIFT.ipa`
   - 点击 **Start**
5. 等待安装完成
6. 在 iPhone 上：设置 → 通用 → VPN与设备管理 → 信任你的 Apple ID
7. 打开游戏

> 免费 Apple ID 签名的应用 7 天后过期，需要重新用 Sideloadly 安装。

### 方法二：AltStore

1. 下载 AltStore：https://altstore.io
2. 按官网指引安装 AltServer 到电脑
3. 在 iPhone 上安装 AltStore
4. 在 AltStore 中点击 `+`，选择 `ADRIFT.ipa`
5. 等待安装完成

### 方法三：Xcode（需要 Mac）

1. 用 Xcode 打开 `output/xcode-project/ADRIFT.xcodeproj`
2. 连接 iPhone，选择设备
3. 配置签名（选择你的 Apple ID Team）
4. 按 `Cmd+R` 编译安装

---

## 项目结构

```
ADRIFT-iOS/
├── .github/
│   └── workflows/
│       └── build-ios.yml      # GitHub Actions 自动编译配置
├── game/
│   ├── archive.rpa             # 游戏资源包
│   ├── z_ios_adapt.rpy        # iOS 适配配置（分辨率/UI）
│   ├── options.rpy             # 游戏选项配置
│   ├── script_version.txt      # 脚本版本
│   ├── libs/                   # 第三方库
│   └── tl/                     # 翻译文件
├── scripts/
│   └── build_ios.sh            # Mac 一键编译脚本
└── README.md                   # 本文件
```

## 适配说明

- **分辨率**：2436×1125（iPhone 横屏 19.5:9），与 iPhone 12~16 系列完全一致
- **UI 适配**：对话框、菜单、按钮等所有界面元素已按新比例调整
- **触控优化**：按钮点击区域增大，符合 iOS 人机界面指南
- **安全区域**：Ren'Py 自动适配刘海屏/灵动岛，内容不被遮挡
- **横屏锁定**：仅支持横屏，视觉小说最佳体验

## 常见问题

**Q: GitHub Actions 运行失败怎么办？**
A: 点击失败的工作流，查看日志中的错误信息。常见原因：
- renios 下载失败 → 重新运行工作流
- Xcode 编译错误 → 查看日志中的具体错误

**Q: 安装后打开闪退？**
A: 可能是签名问题。确保在 iPhone 设置中信任了开发者证书。

**Q: 7 天后应用不能用了？**
A: 免费 Apple ID 签名有效期 7 天。重新用 Sideloadly 安装即可，存档不会丢失。

**Q: 可以上架 App Store 吗？**
A: 可以。需要 Apple 开发者账号（$99/年），在 Xcode 中配置正式签名后 Archive 上传。

## 技术信息

- 引擎：Ren'Py 8.4.1
- 游戏：ADRIFT v1.0
- 目标平台：iOS 15.0+
- 设备：iPhone / iPad（横屏）
- 架构：arm64
