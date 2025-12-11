import ast
import os

def generate_minimal_requirements(original_requirements, files_to_check):
    """
    original_requirements -> string content of requirements.txt (system wide)
    Given a full requirements.txt and a list of Python scripts,
    prints the minimal requirements needed for only those scripts.
    """

    imported_modules = set()
    for path in files_to_check:
        if not os.path.exists(path):
            print(f"Warning: {path} not found, skipping.")
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_modules.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_modules.add(node.module.split('.')[0])

    req_lines = original_requirements.split("\n")

    requirements = {}
    for line in req_lines:
        pkg = line.strip().split("==")[0].split("@")[0].split(" ")[0].strip()
        if pkg:
            requirements[pkg.lower()] = line.strip()

    #print(requirements)

    manual_mapping = {
        "cv2": "opencv-contrib-python",
        "PIL": "pillow",
        "whisper_timestamped": "openai-whisper",
        "sklearn": "scikit-learn",
        "bs4": "beautifulsoup4",
    }

    stdlib_modules = {
        "sys", "os", "json", "re", "math", "ctypes", "time", "random", "shutil",
        "subprocess", "copy", "tkinter", "pathlib", "glob", "itertools", "string",
        "threading", "multiprocessing", "queue", "tempfile", "argparse", "typing"
    }

    required_packages = set()
    for mod in imported_modules:
        if mod in stdlib_modules:
            continue
        pkg_name = manual_mapping.get(mod, mod)
        if pkg_name and pkg_name.lower() in requirements:
            required_packages.add(requirements[pkg_name.lower()])

    minimal_reqs = sorted(required_packages)
    #print("\n".join(minimal_reqs))
    return "\n".join(minimal_reqs)


if __name__ == "__main__":
    import subprocess

    current_file = os.path.abspath(__file__)
    py_files = []

    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                if full_path != current_file:
                    py_files.append(full_path)

    print("Found: ", end="")
    print([x.split("\\")[-1] for x in py_files])
    print("\n\n")

    pip_freeze = subprocess.run("pip freeze", shell=True, capture_output=True, text=True)    
    minimal_reqs = generate_minimal_requirements(str(pip_freeze.stdout), py_files)

    if os.path.exists("requirements.txt"):
        print("requirements.txt already exists! Delete to generate a new one. Here it the output though: ")
        print(minimal_reqs)
    else:
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(minimal_reqs)
        print("Saved to requirements.txt")

