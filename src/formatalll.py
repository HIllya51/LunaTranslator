import os
from pathlib import Path
from tqdm import tqdm

os.chdir(os.path.dirname(__file__))


def format_py_files(directory):
    """遍历目录并用black格式化所有Python文件"""
    for py_file in tqdm(Path(directory).rglob("*.py")):
        if not any(x in py_file.parts for x in [".venv", "venv", "__pycache__"]):
            print(py_file)
            os.system(f'black "{py_file}"')


if __name__ == "__main__":
    format_py_files("./LunaTranslator")
