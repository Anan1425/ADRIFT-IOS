#!/bin/bash
# ADRIFT iOS 一键编译脚本 (macOS)
# 使用方法: ./build_ios.sh
# 需要: macOS 14+, Xcode 15+, 网络连接

set -e

# 配置
RENPY_VERSION="8.4.1"
RENPY_SHORT="8.4"
APP_NAME="ADRIFT"
BUNDLE_ID="com.adrift.game"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
WORK_DIR="$PROJECT_DIR/build-work"
OUTPUT_DIR="$PROJECT_DIR/output"

echo "============================================"
echo "  ADRIFT iOS 编译脚本"
echo "  Ren'Py $RENPY_VERSION"
echo "============================================"
echo ""

# 检查是否在 macOS 上
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "错误: 此脚本必须在 macOS 上运行"
    exit 1
fi

# 检查 Xcode
if ! command -v xcodebuild &> /dev/null; then
    echo "错误: 未安装 Xcode 命令行工具"
    echo "请运行: xcode-select --install"
    exit 1
fi
echo "[OK] Xcode 已安装"

# 创建工作目录
echo ""
echo "[1/7] 准备工作目录..."
mkdir -p "$WORK_DIR" "$OUTPUT_DIR"
cd "$WORK_DIR"

# 下载 Ren'Py SDK
echo ""
echo "[2/7] 下载 Ren'Py SDK..."
if [ ! -d "renpy-sdk" ]; then
    curl -fL -o renpy-sdk.tar.bz2 "https://www.renpy.org/dl/${RENPY_VERSION}/renpy-${RENPY_VERSION}-sdk.tar.bz2"
    tar -xjf renpy-sdk.tar.bz2
    mv "renpy-${RENPY_VERSION}-sdk" renpy-sdk
    rm renpy-sdk.tar.bz2
fi
echo "[OK] Ren'Py SDK 就绪"

# 下载 renios
echo ""
echo "[3/7] 下载 iOS 支持包 (renios)..."
cd renpy-sdk
if [ ! -d "renios" ]; then
    RENIOS_DONE=0
    for url in \
        "http://update.renpy.org/${RENPY_SHORT}/renios-${RENPY_VERSION}.zip" \
        "https://www.renpy.org/dl/${RENPY_VERSION}/renios.zip" \
        "https://www.renpy.org/dl/${RENPY_VERSION}/renios-${RENPY_VERSION}.zip"; do
        echo "  尝试: $url"
        if curl -fL -o renios.zip "$url" 2>/dev/null; then
            unzip -q renios.zip
            rm renios.zip
            RENIOS_DONE=1
            echo "  [OK] 下载成功"
            break
        fi
    done
    if [ $RENIOS_DONE -eq 0 ]; then
        echo "  错误: 无法下载 renios"
        echo "  请手动在 Ren'Py Launcher 中点击 iOS -> Download renios"
        exit 1
    fi
else
    echo "[OK] renios 已存在"
fi
cd "$WORK_DIR"

# 设置项目
echo ""
echo "[4/7] 设置项目..."
mkdir -p renpy-sdk/projects
rm -rf "renpy-sdk/projects/${APP_NAME}"
cp -r "$PROJECT_DIR/game" "renpy-sdk/projects/${APP_NAME}"
echo "[OK] 项目已复制"

# 创建 Xcode 项目
echo ""
echo "[5/7] 创建 Xcode 项目..."
cd renpy-sdk
./renpy.sh launcher ios_create \
    "projects/${APP_NAME}" \
    "$WORK_DIR/xcode-output/${APP_NAME}" 2>&1 | tail -5

# 更新游戏文件
echo ""
echo "[6/7] 更新游戏文件到 Xcode 项目..."
./renpy.sh launcher ios_populate \
    "projects/${APP_NAME}" \
    "$WORK_DIR/xcode-output/${APP_NAME}" 2>&1 | tail -5

cd "$WORK_DIR"

# 定位 Xcode 项目
XCODEPROJ=$(find xcode-output -name "*.xcodeproj" -type d | head -1)
if [ -z "$XCODEPROJ" ]; then
    echo "错误: 未找到 Xcode 项目"
    exit 1
fi
PROJECT_DIR_XCODE="$(cd "$(dirname "$XCODEPROJ")" && pwd)"
SCHEME=$(basename "$XCODEPROJ" .xcodeproj)
echo "  项目: $XCODEPROJ"
echo "  Scheme: $SCHEME"

# 配置 Info.plist
echo ""
echo "[7/7] 配置 Info.plist 并编译..."
INFO_PLIST=$(find "$PROJECT_DIR_XCODE" -name "Info.plist" -not -path "*/build/*" | head -1)

if [ -f "$INFO_PLIST" ]; then
    # 横屏
    /usr/libexec/PlistBuddy -c "Delete :UISupportedInterfaceOrientations" "$INFO_PLIST" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c "Add :UISupportedInterfaceOrientations array" "$INFO_PLIST"
    /usr/libexec/PlistBuddy -c "Add :UISupportedInterfaceOrientations:0 string UIInterfaceOrientationLandscapeLeft" "$INFO_PLIST"
    /usr/libexec/PlistBuddy -c "Add :UISupportedInterfaceOrientations:1 string UIInterfaceOrientationLandscapeRight" "$INFO_PLIST"

    # 不锁屏
    /usr/libexec/PlistBuddy -c "Delete :UIIdleTimerDisabled" "$INFO_PLIST" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c "Add :UIIdleTimerDisabled bool true" "$INFO_PLIST"

    # 全屏
    /usr/libexec/PlistBuddy -c "Delete :UIRequiresFullScreen" "$INFO_PLIST" 2>/dev/null || true
    /usr/libexec/PlistBuddy -c "Add :UIRequiresFullScreen bool true" "$INFO_PLIST"

    # Bundle ID
    /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier ${BUNDLE_ID}" "$INFO_PLIST" 2>/dev/null || \
    /usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string ${BUNDLE_ID}" "$INFO_PLIST"

    echo "  [OK] Info.plist 已配置"
fi

# 编译
cd "$PROJECT_DIR_XCODE"
echo "  开始编译 (可能需要 3-5 分钟)..."
xcodebuild \
    -project "$SCHEME.xcodeproj" \
    -scheme "$SCHEME" \
    -configuration Release \
    -sdk iphoneos \
    -derivedDataPath build \
    CODE_SIGNING_ALLOWED=NO \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGN_IDENTITY="" \
    ONLY_ACTIVE_ARCH=NO \
    build 2>&1 | tail -20

# 查找 .app
APP_PATH=$(find build -name "*.app" -type d | head -1)
if [ -z "$APP_PATH" ]; then
    echo "错误: 编译失败，未找到 .app"
    exit 1
fi

# 打包 IPA
mkdir -p Payload
cp -r "$APP_PATH" Payload/
zip -qr "${APP_NAME}.ipa" Payload/
rm -rf Payload

# 复制到输出目录
cp "${APP_NAME}.ipa" "$OUTPUT_DIR/"
cp -r "$PROJECT_DIR_XCODE" "$OUTPUT_DIR/xcode-project"

echo ""
echo "============================================"
echo "  编译完成！"
echo "============================================"
echo ""
echo "IPA 文件: $OUTPUT_DIR/${APP_NAME}.ipa"
echo "Xcode 项目: $OUTPUT_DIR/xcode-project/"
echo ""
echo "安装方法:"
echo "  1. 使用 Sideloadly (推荐): https://sideloadly.io"
echo "  2. 使用 AltStore: https://altstore.io"
echo "  3. 使用 Xcode: 打开 xcode-project 中的 .xcodeproj"
echo ""
