import toml
import os

def parse_requirements(file_path):
    """Parse requirements.txt into a dictionary."""
    requirements = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                package, _, version = line.partition('==')
                requirements[package] = version
    return requirements

def parse_poetry(file_path):
    """Parse pyproject.toml dependencies into a dictionary."""
    with open(file_path, 'r') as f:
        poetry_data = toml.load(f)
    return poetry_data['tool']['poetry']['dependencies']

def update_requirements(requirements, poetry_deps):
    """Update requirements.txt based on pyproject.toml dependencies."""
    updated = []
    for package, version in poetry_deps.items():
        if isinstance(version, str):  # Ignore Python version constraints
            updated.append(f"{package}=={version}")
    return updated

def write_requirements(file_path, updated_reqs):
    """Write updated requirements to requirements.txt."""
    with open(file_path, 'w') as f:
        f.write("\n".join(updated_reqs))

def main():
    requirements_path = 'requirements.txt'
    poetry_path = 'pyproject.toml'

    if not os.path.exists(requirements_path):
        print(f"{requirements_path} not found.")
        return

    if not os.path.exists(poetry_path):
        print(f"{poetry_path} not found.")
        return

    requirements = parse_requirements(requirements_path)
    poetry_deps = parse_poetry(poetry_path)

    updated_reqs = update_requirements(requirements, poetry_deps)
    write_requirements(requirements_path, updated_reqs)

    print(f"Updated {requirements_path} based on {poetry_path}.")

if __name__ == "__main__":
    main()
