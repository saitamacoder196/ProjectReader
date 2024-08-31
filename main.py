# main.py
import os
import fnmatch
from settings import PROJECT_PATH
import chardet

def get_project_name():
    """Get the project name from the PROJECT_PATH."""
    normalized_path = os.path.normpath(PROJECT_PATH)
    if normalized_path == '.':
        # Get the current directory name if PROJECT_PATH is '.'
        return os.path.basename(os.getcwd())
    else:
        return os.path.basename(normalized_path)

def initialize_paths():
    """Initialize the paths for output and rules based on the project name."""
    project_name = get_project_name()
    base_path = os.path.join('output', project_name)
    markdown_path = os.path.join(base_path, 'project_structure.md')
    rules_path = os.path.join(base_path, 'rules.txt')
    return base_path, markdown_path, rules_path

def create_output_directory(base_path):
    """Ensure the output directory exists."""
    if not os.path.exists(base_path):
        os.makedirs(base_path)

def generate_default_rules(rules_path, start_path):
    """Generate a default rules.txt file if not exists."""
    if not os.path.isfile(rules_path):
        with open(rules_path, 'w', encoding='utf-8') as f:
            for root, dirs, files in os.walk(start_path):
                for dir in dirs:
                    f.write(f"{os.path.join(root, dir)}/\n")
                for file in files:
                    f.write(f"{os.path.join(root, file)}\n")

def load_rules(rules_path):
    """Load and parse rules from a given rules file."""
    if not os.path.isfile(rules_path):
        return None, None  # Indicates no rules file found
    include_patterns = []
    exclude_patterns = []
    with open(rules_path, 'r') as file:
        for line in file:
            clean_line = line.strip()
            if clean_line.startswith('!'):
                exclude_patterns.append(clean_line[1:])
            else:
                include_patterns.append(clean_line)
    return include_patterns, exclude_patterns

def should_include(path, include_patterns, exclude_patterns):
    """Determine if a file should be included based on the rules."""
    if exclude_patterns and any(fnmatch.fnmatch(path, pat) for pat in exclude_patterns):
        return False
    if include_patterns:
        return any(fnmatch.fnmatch(path, pat) for pat in include_patterns)
    return True  # No patterns provided, include everything

def generate_project_structure(start_path, include_patterns, exclude_patterns):
    """Generate the project structure and contents for the Markdown file."""
    markdown_content = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            file_path = os.path.join(root, file)
            if should_include(file_path, include_patterns, exclude_patterns):
                relative_path = os.path.relpath(file_path, start_path)
                markdown_content.append(f"### {relative_path}\n```")
                try:
                    with open(file_path, 'rb') as f:  # Open in binary mode to read raw bytes
                        raw_data = f.read()
                        encoding = chardet.detect(raw_data)['encoding']
                        file_content = raw_data.decode(encoding)
                    markdown_content.append(file_content)
                except Exception as e:
                    markdown_content.append(f"Error decoding file: {str(e)}")
                markdown_content.append("```\n")
    return markdown_content

def write_markdown(content, markdown_path):
    """Write content to a Markdown file."""
    with open(markdown_path, 'w', encoding='utf-8') as md_file:
        md_file.write("\n".join(content))

def main():
    OUTPUT_BASE_PATH, OUTPUT_MARKDOWN_PATH, RULES_FILE = initialize_paths()
    create_output_directory(OUTPUT_BASE_PATH)
    generate_default_rules(RULES_FILE, PROJECT_PATH)
    include_patterns, exclude_patterns = load_rules(RULES_FILE)
    content = generate_project_structure(PROJECT_PATH, include_patterns, exclude_patterns)
    write_markdown(content, OUTPUT_MARKDOWN_PATH)
    print(f"Markdown file has been created at {OUTPUT_MARKDOWN_PATH}")

if __name__ == "__main__":
    main()

