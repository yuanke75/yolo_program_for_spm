import os
import re
from collections import defaultdict

def get_imports_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except (UnicodeDecodeError, IOError) as e:
        print(f"Error reading file {file_path}: {e}")
        return []
    
    import_statements = re.findall(r'^\s*(import|from)\s+([^\s]+)', content, re.MULTILINE)
    imports = [statement[1].split('.')[0] for statement in import_statements]
    return imports

def get_all_imports(directory):
    all_imports = defaultdict(set)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                imports = get_imports_from_file(file_path)
                for imp in imports:
                    all_imports[imp].add(file_path)
    return all_imports

def write_imports_to_file(imports, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for imp, files in imports.items():
            file.write(f'Library: {imp}\n')
            # for file_path in files:
            #     file.write(f'  Found in: {file_path}\n')
            file.write('\n')

def main():
    directory = 'D:/code/yolov9-main'  # 修改为你的工作目录
    output_file = 'imported_libraries.txt'
    imports = get_all_imports(directory)
    write_imports_to_file(imports, output_file)
    print(f'Results have been written to {output_file}')

if __name__ == '__main__':
    main()
