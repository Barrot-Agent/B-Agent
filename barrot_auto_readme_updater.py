import os
import json
import pkgutil
import importlib

# Function to scan directories and files

def scan_repository(root_directory):
    components = {"Python Files": [], "JSON Configs": [], "Data Files": [], "Documentation": [], "Shell Scripts": [], "Custom Formats": []}
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if filename.endswith('.py'):
                components["Python Files"].append(file_path)
            elif filename.endswith('.json'):
                components["JSON Configs"].append(file_path)
            elif filename.endswith('.txt') or filename.endswith('.csv'):
                components["Data Files"].append(file_path)
            elif filename.endswith('.md'):
                components["Documentation"].append(file_path)
            elif filename.endswith('.sh'):
                components["Shell Scripts"].append(file_path)
            elif filename.endswith('.chi'):
                components["Custom Formats"].append(file_path)
    return components

# Function to extract metadata from Python files

def extract_python_metadata(file_path):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    module = importlib.import_module(module_name)
    metadata = {
        "functions": [],
        "classes": []
    }
    for name, obj in vars(module).items():
        if callable(obj):
            metadata["functions"].append(name)
        if isinstance(obj, type):
            metadata["classes"].append(name)
    return metadata

# Function to catalog all components

def catalog_components(components):
    catalog = {}
    for component_type, files in components.items():
        catalog[component_type] = []
        for file_path in files:
            if component_type == "Python Files":
                metadata = extract_python_metadata(file_path)
                catalog[component_type].append({"file": file_path, "metadata": metadata})
            else:
                catalog[component_type].append(file_path)
    return catalog

# Function to build MCP resource manifest

def build_mcp_manifest(catalog):
    manifest = {
        "components": catalog,
        "total": sum(len(files) for files in catalog.values())
    }
    return manifest

# Function to generate README

def generate_readme(catalog):
    readme_content = "# B-Agent Repository\n\n"
    readme_content += "## Discovered Components\n"
    for component_type, files in catalog.items():
        readme_content += f"### {component_type}: {len(files)}\n"
        readme_content += "\n".join(f"- {f['file']}" if isinstance(f, dict) else f for f in files) + "\n\n"
    readme_content += "## Repository Statistics\n"
    readme_content += f"Total Components: {sum(len(files) for files in catalog.values())}\n"
    return readme_content

if __name__ == '__main__':
    root_dir = '.'  # Adjust as necessary
    components = scan_repository(root_dir)
    catalog = catalog_components(components)
    mcp_manifest = build_mcp_manifest(catalog)
    with open('mcp_manifest.json', 'w') as manifest_file:
        json.dump(mcp_manifest, manifest_file, indent=4)
    readme = generate_readme(catalog)
    with open('README.md', 'w') as readme_file:
        readme_file.write(readme)
    print("README.md and MCP Manifest updated successfully!")
