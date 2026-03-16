import os
from PIL import Image
import base64
from io import BytesIO


def extract_font(file_path, output_dir="font_chars"):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    char_size_bytes = 72
    width, height = 24, 24
    bytes_per_row = 3  # 24 bits = 3 bytes

    with open(file_path, "rb") as f:
        data = f.read()

    total_chars = len(data) // char_size_bytes
    print(f"Total characters found: {total_chars}")

    # 保存每个字符为单独的图片
    char_files = []
    for i in range(total_chars):
        char_data = data[i * char_size_bytes : (i + 1) * char_size_bytes]
        
        # 创建单个字符的图片
        char_img = Image.new("1", (width, height), 0)

        # 解析 72 字节的位图数据
        for y in range(height):
            # 每行 3 字节
            row_bytes = char_data[y * bytes_per_row : (y + 1) * bytes_per_row]
            
            # 将字节转为 24 个像素位
            bits = bin(int.from_bytes(row_bytes, byteorder='big'))[2:].zfill(24)
            
            for x in range(width):
                if bits[x] == '1':
                    char_img.putpixel((x, y), 1)

        # 保存字符图片
        char_filename = f"char_{i:04d}.png"
        char_filepath = os.path.join(output_dir, char_filename)
        char_img.save(char_filepath)
        char_files.append(char_filename)

    # 生成Markdown文件
    markdown_content = generate_markdown(char_files, output_dir, chars_per_row=16)
    
    # 保存Markdown文件
    markdown_file = "PiAS.md"
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"Success: Extracted {total_chars} characters to '{output_dir}' directory")
    print(f"Success: Created preview '{markdown_file}'")

def generate_markdown(char_files, output_dir, chars_per_row=16):
    
    content = ""
    
    # 按行生成图片
    for i in range(0, len(char_files), chars_per_row):
        # 添加行分隔符（可选）
        content += f"\n### 行 {i//chars_per_row + 1}\n\n"
        
        # 获取当前行的图片文件
        row_files = char_files[i:i + chars_per_row]
        
        # 添加图片行
        for char_file in row_files:
            # 使用相对路径引用图片
            content += f"![{char_file}]({output_dir}/{char_file}) "
        
        content += "\n\n"
        
        # 添加索引行（方便查找）
        for j, char_file in enumerate(row_files):
            idx = i + j
            content+=f'0x{idx:04x}'
        
        content += "\n\n"  # 添加分隔线
    
    return content

if __name__ == "__main__":
    if 0:
        extract_font("font.dat")
    if 1:
        with open('PiAS.md', 'r', encoding='utf8') as ff:
            md=ff.read()
        collect=""
        for l in md.splitlines():
            if l.startswith('![') or l.startswith('###'):
                continue
            if not l:
                continue
            collect+=l
        
            print(len(l), len(collect))
            print(l)
        with open('PiAS.txt', 'w', encoding='utf8') as ff:
            ff.write(collect)