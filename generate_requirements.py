import os
import chardet
import subprocess

def read_file_with_encoding(file_path):
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise

def get_imports_from_directory(directory):
    imports = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                content = read_file_with_encoding(file_path)
                for line in content.splitlines():
                    if line.startswith('import') or line.startswith('from'):
                        imports.add(line.split()[1].split('.')[0])
    return imports

def get_conda_packages_with_versions(packages):
    try:
        installed_packages = subprocess.check_output(['conda', 'list', '--export']).decode('utf-8')
    except subprocess.CalledProcessError as e:
        print("Failed to get conda package list:", e)
        return {}
    
    package_versions = {}
    for package in installed_packages.splitlines():
        if not package.startswith('#'):
            parts = package.split()
            if len(parts) >= 2 and parts[0] in packages:
                package_versions[parts[0]] = parts[1]
    return package_versions

def write_requirements(package_versions, output_file):
    with open(output_file, 'w') as f:
        for name, version in sorted(package_versions.items()):
            f.write(f"{name}=={version}\n")

if __name__ == "__main__":
    project_directory = "D:/code/yolov9-main"
    output_file = "requirements.txt"
    imports = get_imports_from_directory(project_directory)
    package_versions = get_conda_packages_with_versions(imports)
    write_requirements(package_versions, output_file)
    print(f"Requirements written to {output_file}")
