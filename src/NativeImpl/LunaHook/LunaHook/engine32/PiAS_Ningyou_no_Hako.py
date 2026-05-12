import struct
import os
from PIL import Image


def decode_font_data(data, width, height):
    """
    解码字体数据
    根据 sub_4183B0 的逻辑

    对于8x8, 16x16, 24x24: 每字节8像素，按行存储
    对于18x18: 特殊处理，有更复杂的布局
    """
    bytes_per_row = (width + 7) // 8
    total_bytes = bytes_per_row * height

    if len(data) < total_bytes:
        print(f"数据不足: 需要 {total_bytes} 字节, 实际 {len(data)} 字节")
        return None

    # 创建位图数组
    bitmap = [[0 for _ in range(width)] for _ in range(height)]

    byte_idx = 0
    for y in range(height):
        for byte_in_row in range(bytes_per_row):
            if byte_idx >= len(data):
                break
            byte_val = data[byte_idx]
            # 每个字节的8位，从高位到低位
            for bit in range(8):
                x = byte_in_row * 8 + bit
                if x >= width:
                    break
                if (byte_val >> (7 - bit)) & 1:
                    bitmap[y][x] = 1  # 前景色
                else:
                    bitmap[y][x] = 0  # 背景色
            byte_idx += 1

    return bitmap


def decode_font_data_18x18(data):
    """
    专门处理18x18字体
    根据 sub_4183B0 中对 size=18 的特殊处理
    """
    width, height = 18, 18

    # 18x18字体的存储方式不同
    bitmap = [[0 for _ in range(width)] for _ in range(height)]

    # 根据反编译代码，18x18字体按特殊顺序存储
    # 每2个字节对应一个像素行的一部分
    pos = 0
    for row in range(height):
        # 每行有多个字节
        for col in range(0, width, 8):
            if pos >= len(data):
                break
            byte_val = data[pos]
            for bit in range(8):
                x = col + bit
                if x >= width:
                    break
                if (byte_val >> (7 - bit)) & 1:
                    bitmap[row][x] = 1
            pos += 1

    return bitmap


def parse_font_dat(font_dat_path, output_dir="font_chars"):
    """
    解析font.dat文件
    格式: [1字节模式] + [压缩的字体数据]
    """

    with open(font_dat_path, "rb") as f:
        # 读取模式字节
        mode_byte = f.read(1)
        if not mode_byte:
            print("文件为空")
            return

        mode = mode_byte[0]
        print(f"字体模式字节: 0x{mode:02X}")

        # 读取字体数据
        font_data = f.read()

    # 根据模式确定字体参数
    # 从 sub_417B40 中的判断
    font_configs = {
        0x10: {"size": 16, "width": 16, "height": 16, "special": False},
        0x12: {"size": 18, "width": 18, "height": 18, "special": True},
        0x18: {"size": 24, "width": 24, "height": 24, "special": False},
        0x08: {"size": 8, "width": 8, "height": 8, "special": False},
    }

    if mode in font_configs:
        config = font_configs[mode]
        print(f"字体大小: {config['size']}x{config['size']}")
    else:
        print(f"未知模式 0x{mode:02X}，尝试自动检测...")
        # 尝试常见大小
        for size in [16, 18, 24, 32, 12, 8]:
            bytes_per_char = (size * size) // 8
            bytes_per_char_18 = (18 * 18 + 7) // 8  # 约41字节
            if len(font_data) % bytes_per_char == 0:
                config = {
                    "size": size,
                    "width": size,
                    "height": size,
                    "special": size == 18,
                }
                print(f"检测到字体大小: {size}x{size}")
                break
        else:
            raise ValueError(f"无法识别字体格式，数据长度: {len(font_data)}")

    char_width = config["width"]
    char_height = config["height"]

    if config["special"]:
        # 18x18字体特殊处理
        bytes_per_char = 41  # 近似值，需要精确计算
        char_size_bytes = (char_width * char_height + 7) // 8
    else:
        char_size_bytes = (char_width * char_height) // 8

    total_chars = len(font_data) // char_size_bytes
    print(f"每字符字节数: {char_size_bytes}")
    print(f"总字符数: {total_chars}")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 计算网格布局
    chars_per_row = 16  # 原代码中使用的值
    rows = (total_chars + chars_per_row - 1) // chars_per_row
    grid_width = chars_per_row * char_width
    grid_height = rows * char_height

    # 创建大图（灰度模式，0=黑色前景，255=白色背景）
    grid_image = Image.new("L", (grid_width, grid_height), color=255)

    # 提取每个字符
    for char_idx in range(total_chars):
        offset = char_idx * char_size_bytes
        char_data = font_data[offset : offset + char_size_bytes]

        # 解码位图
        if config["special"]:
            bitmap = decode_font_data_18x18(char_data)
        else:
            bitmap = decode_font_data(char_data, char_width, char_height)

        if bitmap is None:
            continue

        # 创建字符图片
        char_img = Image.new("L", (char_width, char_height), color=255)
        pixels = char_img.load()

        for y in range(char_height):
            for x in range(char_width):
                if y < len(bitmap) and x < len(bitmap[y]):
                    if bitmap[y][x] == 1:
                        pixels[x, y] = 0  # 黑色前景
                    else:
                        pixels[x, y] = 255  # 白色背景

        # 保存单个字符
        char_img.save(os.path.join(output_dir, f"char_{char_idx:04d}.png"))

        # 计算在大图中的位置
        row = char_idx // chars_per_row
        col = char_idx % chars_per_row
        x = col * char_width
        y = row * char_height

        # 粘贴到大图
        grid_image.paste(char_img, (x, y))

        if (char_idx + 1) % 100 == 0:
            print(f"已处理 {char_idx + 1}/{total_chars} 个字符")

    # 保存网格图
    grid_image.save(os.path.join(output_dir, "font_grid.png"))
    print(f"已保存网格图: font_grid.png")

    # 生成HTML预览
    generate_html_preview(
        output_dir, total_chars, char_width, char_height, chars_per_row
    )

    return config


def generate_html_preview(
    output_dir, total_chars, char_width, char_height, chars_per_row
):
    """生成HTML预览文件"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Font Character Preview</title>
    <style>
        .char-grid {{
            display: grid;
            grid-template-columns: repeat({chars_per_row}, 1fr);
            gap: 2px;
            font-family: monospace;
            max-width: {chars_per_row * (char_width + 10)}px;
        }}
        .char-cell {{
            text-align: center;
            border: 1px solid #ccc;
            padding: 5px;
            background: #fff;
        }}
        .char-cell img {{
            display: block;
            margin: 0 auto;
            image-rendering: crisp-edges;
            image-rendering: pixelated;
        }}
        .char-index {{
            font-size: 10px;
            color: #666;
            margin-top: 4px;
        }}
        body {{
            background: #f0f0f0;
            font-family: sans-serif;
        }}
        h1 {{
            text-align: center;
        }}
        .controls {{
            text-align: center;
            margin: 20px;
            position: sticky;
            top: 0;
            background: #f0f0f0;
            padding: 10px;
            z-index: 100;
        }}
        input {{
            padding: 5px 10px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>Font Characters Preview</h1>
    <div class="controls">
        <label>跳转到: <input type="number" id="gotoIndex" min="0" max="{total_chars-1}" placeholder="索引">
        </label>
        <button onclick="gotoChar()">跳转</button>
        <span id="status"></span>
    </div>
    <div class="char-grid" id="charGrid">
"""

    # 生成前500个字符的预览（避免页面过大）
    preview_limit = min(total_chars, 2000)
    for i in range(preview_limit):
        html_content += f"""
        <div class="char-cell" data-index="{i}">
            <img src="char_{i:04d}.png" width="{char_width}" height="{char_height}">
            <div class="char-index">{i:04x}</div>
        </div>
"""

    html_content += f"""
    </div>
    <script>
        function gotoChar() {{
            var idx = parseInt(document.getElementById('gotoIndex').value);
            if (isNaN(idx) || idx < 0 || idx >= {total_chars}) {{
                document.getElementById('status').innerText = '无效索引';
                return;
            }}
            var cell = document.querySelector(`.char-cell[data-index="${{idx}}"]`);
            if (cell) {{
                cell.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                cell.style.backgroundColor = '#ffffaa';
                setTimeout(() => {{ cell.style.backgroundColor = ''; }}, 1000);
                document.getElementById('status').innerHTML = `已跳转到索引 ${{idx}}`;
            }} else {{
                document.getElementById('status').innerHTML = `索引 ${{idx}} 不在预览范围内（最大{preview_limit-1}）`;
            }}
        }}
    </script>
</body>
</html>
"""

    with open(os.path.join(output_dir, "preview.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"已生成HTML预览: preview.html")


def analyze_font_file(font_dat_path):
    """详细分析字体文件结构"""

    with open(font_dat_path, "rb") as f:
        mode_byte = f.read(1)
        data = f.read()

    print("\n" + "=" * 50)
    print("字体文件分析")
    print("=" * 50)
    print(f"文件大小: {len(data) + 1} 字节")
    print(f"模式字节: 0x{mode_byte[0]:02X}")

    # 分析数据分布
    print(f"\n数据长度: {len(data)} 字节")

    # 统计字节值分布
    byte_counts = {}
    for b in data[: min(len(data), 10000)]:
        byte_counts[b] = byte_counts.get(b, 0) + 1

    print(f"\n前100个字节: {data[:100]}")

    # 尝试不同的字符大小
    print("\n尝试检测字符大小:")
    for size in [8, 12, 16, 18, 24, 32]:
        bytes_per_char = (size * size + 7) // 8  # 向上取整
        if len(data) % bytes_per_char == 0:
            char_count = len(data) // bytes_per_char
            print(
                f"  {size}x{size}: {bytes_per_char} 字节/字符, 共 {char_count} 个字符"
            )

    # 检查是否为原始位图数据（无压缩）
    print("\n检查像素模式:")
    # 查看是否有明显的重复模式
    unique_patterns = set()
    for i in range(0, min(len(data), 1000), 16):
        pattern = data[i : i + 16]
        unique_patterns.add(pattern)

    print(f"  前1000字节中的唯一16字节模式数: {len(unique_patterns)}")

    return mode_byte[0], len(data)


if __name__ == "__main__":
    import sys

    font_file = "font0.dat"
    if len(sys.argv) > 1:
        font_file = sys.argv[1]

    if not os.path.exists(font_file):
        print(f"文件 {font_file} 不存在！")
        print("用法: python extract_font.py <font.dat路径>")
        sys.exit(1)

    # 分析文件
    mode, data_len = analyze_font_file(font_file)

    # 解析提取
    try:
        config = parse_font_dat(font_file, "extracted_chars")
        print(f"\n✓ 提取完成！字符保存在 extracted_chars/ 目录")
        print(f"字体配置: {config}")
    except Exception as e:
        print(f"\n✗ 解析失败: {e}")

        # 尝试直接保存为原始位图
        print("\n尝试直接将数据作为位图保存...")
        with open(font_file, "rb") as f:
            f.read(1)  # 跳过模式字节
            data = f.read()

        # 尝试推断尺寸
        for size in [16, 18, 24, 32]:
            expected_bytes = size * size
            if len(data) % expected_bytes == 0:
                char_count = len(data) // expected_bytes
                print(f"检测到 {size}x{size} 位图，{char_count} 个字符")

                # 尝试提取
                os.makedirs("raw_output", exist_ok=True)
                for i in range(min(char_count, 100)):
                    offset = i * expected_bytes
                    raw_data = data[offset : offset + expected_bytes]
                    img = Image.new("L", (size, size))
                    img.putdata([(255 - val) for val in raw_data])
                    img.save(f"raw_output/char_{i:04d}.png")
                print("原始位图已保存到 raw_output/")
                break
