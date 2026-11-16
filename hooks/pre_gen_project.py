import re
import sys
from pathlib import Path

FLOW_DIR = "{{ cookiecutter.flow_dir }}"

FULL_FLOW_DIR = Path(".").resolve().with_name(FLOW_DIR)
FORBIDDEN_CHARS = r'<>:"\/|?*'

forbidden_chars_in_dir_name = set(FLOW_DIR) & set(FORBIDDEN_CHARS)

if forbidden_chars_in_dir_name:
    print(f"ERROR: '{FLOW_DIR}' contains forbidden chars ({FORBIDDEN_CHARS})")
    sys.exit(1)
elif not FULL_FLOW_DIR.exists():
    try:
        FULL_FLOW_DIR.mkdir(parents=True)
        FULL_FLOW_DIR.rmdir()
    except Exception:
        print(
            f"ERROR: '{FULL_FLOW_DIR}' is not a valid flow directory name "
            "since OS cannot create it."
        )
        sys.exit(1)

flow_id = "{{ cookiecutter.flow_id }}"
if not flow_id.isidentifier():
    print(
        f"ERROR: '{flow_id}' is not a valid flow identifier. "
        "It can only contain alphanumeric letters (a-zA-Z0-9), or underscores (_), "
        "and cannot start with a number, or contain any spaces."
    )
    sys.exit(1)


MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"
module_name = "{{ cookiecutter.code_directory }}"

if not re.match(MODULE_REGEX, module_name):
    print(
        "ERROR: %s is not a valid Python module name. Module name can only contain "
        "letters, digits, and underscores." % module_name
    )
    sys.exit(1)
