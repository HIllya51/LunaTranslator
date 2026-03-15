import os
from PIL import Image

def extract_font(file_path, output_image="font_atlas.png"):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    char_size_bytes = 72
    width, height = 24, 24
    bytes_per_row = 3  # 24 bits = 3 bytes

    with open(file_path, "rb") as f:
        data = f.read()

    total_chars = len(data) // char_size_bytes
    print(f"Total characters found: {total_chars}")

    # 设定每行显示多少个字符
    chars_per_row = 40
    num_rows = (total_chars + chars_per_row - 1) // chars_per_row

    # 创建一张巨大的空白图片 (黑底)
    atlas_w = chars_per_row * width
    atlas_h = num_rows * height
    atlas_img = Image.new("1", (atlas_w, atlas_h), 0)

    for i in range(total_chars):
        char_data = data[i * char_size_bytes : (i + 1) * char_size_bytes]
        
        # 计算在 Atlas 中的位置
        char_x = (i % chars_per_row) * width
        char_y = (i // chars_per_row) * height

        # 解析 72 字节的位图数据
        for y in range(height):
            # 每行 3 字节
            row_bytes = char_data[y * bytes_per_row : (y + 1) * bytes_per_row]
            
            # 将字节转为 24 个像素位
            bits = bin(int.from_bytes(row_bytes, byteorder='big'))[2:].zfill(24)
            
            for x in range(width):
                if bits[x] == '1':
                    atlas_img.putpixel((char_x + x, char_y + y), 1)

    # 保存结果
    atlas_img.save(output_image)
    print(f"Success: Saved {total_chars} characters to {output_image}")

def extract_individual_chars(file_path, output_dir="extracted_font"):
    if not os.path.exists(file_path):
        print(f"错误: 找不到 {file_path}")
        return

    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    char_size_bytes = 72  # 每个字 72 字节
    width, height = 24, 24
    bytes_per_row = 3     # 每行 3 字节 (24 bits)

    with open(file_path, "rb") as f:
        data = f.read()

    total_chars = len(data) // char_size_bytes
    print(f"检测到字库大小: {len(data)} 字节")
    print(f"预计字符总数: {total_chars}")

    for i in range(total_chars):
        # 提取当前字符的 72 字节数据
        char_data = data[i * char_size_bytes : (i + 1) * char_size_bytes]
        
        # 创建 1-bit (单色) 图像
        # "1" 模式：0 为黑，1 为白。为了方便查看，我们将背景设为黑，文字设为白。
        img = Image.new("1", (width, height), 0)

        for y in range(height):
            # 获取当前行的 3 个字节
            row_bytes = char_data[y * bytes_per_row : (y + 1) * bytes_per_row]
            
            # 将 3 字节转换为一个 24 位的整数
            # 使用 big 字节序，因为通常最高位 bit 代表最左边的像素
            row_int = int.from_bytes(row_bytes, byteorder='big')
            
            for x in range(width):
                # 检查 row_int 从左数第 x 位是否为 1
                # 23-x 是因为最高位 (第 23 位) 在最左边
                if (row_int >> (23 - x)) & 1:
                    img.putpixel((x, y), 1)

        # 文件命名使用 4 位十六进制（例如 0x0001.png, 0x012A.png）
        # 这与反编译代码中的 v11 索引对应
        char_code = f"0x{i:04X}"
        output_path = os.path.join(output_dir, f"{char_code}.png")
        
        img.save(output_path)

        if i % 500 == 0:
            print(f"已处理: {i}/{total_chars}")

    print(f"\n提取完成！所有图片已保存至: {output_dir}")


import os
import base64
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

MAX_THREADS = 10        # 并发线程数，根据你的 API 限制调整
MAX_RETRIES = 5         # 最大重试次数
api_key=""
base_url=""
MODEL = "gpt-5.2-codex"
# ----------------

client = OpenAI(api_key=api_key, base_url=base_url)

def encode_image(image_path):
    """编码图片为 base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_single_image(image_path):
    """处理单张图片的函数"""
    base_name = os.path.splitext(image_path)[0]
    txt_path = f"{base_name}.txt"

    # 1. 检查是否已经存在对应的 txt 文件
    if os.path.exists(txt_path):
        return f"跳过: {os.path.basename(image_path)} (已存在)"

    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        return f"错误: 无法读取文件 {image_path}, {e}"

    # 2. 带有重试机制的识别逻辑
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "图片中仅有一个文字，请识别它。仅输出该字符本身，不要有任何其他解释或标点。"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=10,
                temperature=0.1, # 降低随机性
            )

            result = response.choices[0].message.content.strip()

            # 3. 校验结果：是否为单字符
            if len(result) == 1:
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(result)
                return f"成功: {os.path.basename(image_path)} -> {result}"
            else:
                print(f"重试: {os.path.basename(image_path)} 识别结果非单字 ('{result}'), 第 {attempt} 次重试...")
        
        except Exception as e:
            print(f"网络/API错误: {os.path.basename(image_path)} 第 {attempt} 次尝试失败: {e}")
        
        # 如果不是最后一次尝试，稍微等待一下
        if attempt < MAX_RETRIES:
            time.sleep(1)

    return f"失败: {os.path.basename(image_path)} 在 {MAX_RETRIES} 次尝试后仍未获得有效单字"


def extract_font_to_sheet(input_file, output_image="font_sheet.png", cols=64):
    # 核心参数（根据 C 代码推断）
    CHAR_WIDTH = 24
    CHAR_HEIGHT = 24
    BYTES_PER_ROW = 3  # 24位 / 8 = 3字节
    BYTES_PER_CHAR = CHAR_HEIGHT * BYTES_PER_ROW # 24 * 3 = 72 字节

    if not os.path.exists(input_file):
        print(f"错误: 找不到文件 {input_file}")
        return

    # 读取原始数据
    with open(input_file, "rb") as f:
        data = f.read()

    num_chars = len(data) // BYTES_PER_CHAR
    if num_chars == 0:
        print("文件大小不足以解析出一个字符。")
        return

    print(f"检测到字符数: {num_chars}")

    # 计算大图的尺寸
    rows = (num_chars + cols - 1) // cols
    # 包含 1 像素的边框/间隙，方便观察
    sheet_width = cols * (CHAR_WIDTH + 1)
    sheet_height = rows * (CHAR_HEIGHT + 1)

    # 创建黑色背景的图像 ('L' 模式为 8位灰度，'1' 为 1位黑白)
    # 这里用 'L' 配合白色文字 (255) 视觉效果更好
    sheet = Image.new('L', (sheet_width, sheet_height), 0)
    
    for i in range(num_chars):
        # 获取当前字符的 72 字节数据
        char_offset = i * BYTES_PER_CHAR
        char_data = data[char_offset : char_offset + BYTES_PER_CHAR]
        
        # 计算在总图上的位置
        grid_x = i % cols
        grid_y = i // cols
        start_x = grid_x * (CHAR_WIDTH + 1)
        start_y = grid_y * (CHAR_HEIGHT + 1)

        # 解析 24x24 位图
        for y in range(CHAR_HEIGHT):
            # 每一行 3 字节
            row_bytes = char_data[y * BYTES_PER_ROW : (y + 1) * BYTES_PER_ROW]
            
            for byte_idx, b in enumerate(row_bytes):
                for bit_idx in range(8):
                    # C 代码逻辑: if ( (v16 & 0x80) != 0 ) -> 1
                    # 意味着从字节的高位(MSB)开始读取
                    if (b << bit_idx) & 0x80:
                        pixel_x = start_x + (byte_idx * 8 + bit_idx)
                        pixel_y = start_y + y
                        # 在画布上画一个白点 (255)
                        if pixel_x < sheet_width and pixel_y < sheet_height:
                            sheet.putpixel((pixel_x, pixel_y), 255)

        if i % 500 == 0:
            print(f"正在处理第 {i} 个字符...")

    # 保存结果
    sheet.save(output_image)
    print("-" * 30)
    print(f"成功! 所有文字已保存至: {output_image}")
    print(f"总计行数: {rows}, 总尺寸: {sheet_width}x{sheet_height}")

def extract_font2(file_path, output_dir="extracted_font2"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    char_size_bytes = 72
    width, height = 24, 24
    
    with open(file_path, "rb") as f:
        file_size = os.path.getsize(f.name)
        num_chars = file_size // char_size_bytes
        
        print(f"检测到文件大小: {file_size} 字节")
        print(f"预计包含字符数: {num_chars}")

        for i in range(num_chars):
            # 每个字符 72 字节
            char_data = f.read(char_size_bytes)
            if not char_data:
                break
            
            # 创建 24x24 的单色图像 (mode '1' 为黑白，每像素1bit)
            # 或者使用 'L' 模式方便观察
            img = Image.new('1', (width, height), 0)
            pixels = img.load()

            for y in range(height):
                # 每一行占 3 字节
                row_bytes = char_data[y*3 : y*3 + 3]
                
                for byte_idx in range(3):
                    current_byte = row_bytes[byte_idx]
                    for bit_idx in range(8):
                        # 从高位到低位提取像素
                        # 如果 (v16 & 0x80) != 0，说明该点有值
                        if (current_byte << bit_idx) & 0x80:
                            x = byte_idx * 8 + bit_idx
                            pixels[x, y] = 1 # 设置为白色

            # 保存图片，以索引命名
            img_path = os.path.join(output_dir, f"char_{i:04d}.png")
            img.save(img_path)
            
            if i % 100 == 0:
                print(f"已处理 {i}/{num_chars}...")

    print(f"提取完成，保存在: {output_dir}")

if __name__ == "__main__":
    if 1:
        extract_font("font.dat")
    if 0:
        extract_individual_chars("font.dat")
    if 0:
    
        png_files = [
            os.path.join('./extracted_font', f) 
            for f in os.listdir('./extracted_font') 
            if f.lower().endswith('.png')
        ]

        print(f"找到 {len(png_files)} 个图片文件。开始识别（并发线程数：{MAX_THREADS}）...")

        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            # 提交所有任务
            future_to_img = {executor.submit(process_single_image, img): img for img in png_files}
            
            for future in as_completed(future_to_img):
                res = future.result()
                print(res)
    if 0:
        lst=[' ']*0x2000
        for f in os.listdir('./extracted_font'):
            if f.lower().endswith('.png'):
                base_name = os.path.splitext(f)[0]
                txt_path = f"extracted_font/{base_name}.txt"
                with open(txt_path, "r", encoding="utf-8") as ff: 
                    lst[int(f[2:6], 16)]=ff.read()
                if len(lst[int(f[2:6], 16)].encode('utf-16-le'))!=2:
                    print(f, lst[int(f[2:6], 16)])
                    lst[int(f[2:6], 16)]="?"
        with open('PiAS.txt', 'w', encoding='utf8') as ff:
            ff.write(''.join(lst))