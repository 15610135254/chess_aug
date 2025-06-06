# 数据文件说明

本目录包含中国象棋AI系统的训练数据和分析结果。由于文件较大，使用Git LFS (Large File Storage) 进行管理。

## 📁 文件列表

| 文件名 | 大小 | 描述 |
|--------|------|------|
| `chess_training_data.json` | 154MB | 完整的象棋训练数据集 |
| `move_frequency_analysis.json` | 94MB | 移动频率分析结果（JSON格式） |
| `move_frequency_analysis.txt` | 68MB | 移动频率分析结果（文本格式） |
| `gameinfo.csv` | 581KB | 游戏信息数据 |
| `moves.csv` | 15MB | 移动记录数据 |

## 🔄 如何获取数据文件

### 方法1: 克隆仓库时自动下载（推荐）

如果你的系统已安装Git LFS：

```bash
# 克隆仓库（会自动下载LFS文件）
git clone https://github.com/15610135254/chess_aug.git
cd chess_aug
```

### 方法2: 手动安装Git LFS并下载

如果Git LFS未安装：

```bash
# 1. 安装Git LFS
# macOS
brew install git-lfs

# Ubuntu/Debian
sudo apt install git-lfs

# Windows
# 从 https://git-lfs.github.io/ 下载安装

# 2. 初始化Git LFS
git lfs install

# 3. 克隆仓库
git clone https://github.com/15610135254/chess_aug.git
cd chess_aug

# 4. 下载LFS文件
git lfs pull
```

### 方法3: 检查现有仓库的LFS文件

如果你已经克隆了仓库但数据文件很小（指针文件）：

```bash
cd chess_aug

# 检查LFS文件状态
git lfs ls-files

# 下载所有LFS文件
git lfs pull

# 或下载特定文件
git lfs pull --include="data/chess_training_data.json"
```

## 📊 数据格式说明

### chess_training_data.json
```json
[
  {
    "board": "棋盘状态字符串（180字符）",
    "player": "red|black",
    "move": "移动坐标（4位数字）"
  }
]
```

### move_frequency_analysis.json
```json
{
  "棋盘状态": [
    {
      "move": "移动坐标",
      "frequency": 频率数值,
      "player": "red|black",
      "description": "移动描述"
    }
  ]
}
```

### gameinfo.csv / moves.csv
标准CSV格式的游戏信息和移动记录。

## ⚠️ 注意事项

1. **存储空间**: 完整数据约347MB，请确保有足够的磁盘空间
2. **网络带宽**: 首次下载需要较好的网络连接
3. **Git LFS限制**: GitHub LFS有带宽限制，大量下载可能受限

## 🛠 故障排除

### 问题1: 数据文件显示为小文件（几KB）
这表示下载的是LFS指针文件，不是实际数据。解决方法：
```bash
git lfs pull
```

### 问题2: Git LFS未安装
错误信息：`git: 'lfs' is not a git command`
解决方法：按照上述方法安装Git LFS

### 问题3: LFS带宽超限
如果遇到GitHub LFS带宽限制，可以：
- 等待下个月重置
- 联系项目维护者获取其他下载方式

## 📞 获取帮助

如果在获取数据文件时遇到问题，请：
1. 检查Git LFS是否正确安装
2. 确认网络连接正常
3. 在GitHub仓库中提交Issue

## 🔗 相关链接

- [Git LFS官方文档](https://git-lfs.github.io/)
- [GitHub LFS使用指南](https://docs.github.com/en/repositories/working-with-files/managing-large-files)
- [项目主页](https://github.com/15610135254/chess_aug)
