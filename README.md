# 坦克大战（Windows 可运行）

这是一个使用 **Python + Tkinter** 编写的简易坦克大战小游戏，可直接在 Windows 上运行。

## 环境要求

- Windows 10/11
- Python 3.10+（建议安装官方版本，通常自带 Tkinter）

## 运行方式

在项目目录中执行：

```bash
python tank_battle.py
```

## 操作说明

- `W` / `S`：前进 / 后退
- `A` / `D`：左转 / 右转
- `J`：开火
- `R`：游戏结束后重新开始

## 玩法

- 你有 3 点生命值。
- 击毁敌方坦克可得分。
- 清空敌方坦克后会刷新新一波敌人。

## 打包为 Windows 可执行文件（可选）

如需生成 `.exe`：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed tank_battle.py
```

生成文件位于 `dist/tank_battle.exe`。
