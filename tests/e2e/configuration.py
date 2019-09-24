from .utils import unique_label


TIMEOUT_MAKE_SETUP = 6 * 60
TIMEOUT_MAKE_UPLOAD_CODE = 5
TIMEOUT_MAKE_CLEAN_CODE = 3
TIMEOUT_MAKE_UPLOAD_DATA = 500
TIMEOUT_MAKE_CLEAN_DATA = 50
TIMEOUT_MAKE_UPLOAD_NOTEBOOKS = TIMEOUT_MAKE_DOWNLOAD_NOTEBOOKS = 5
TIMEOUT_MAKE_CLEAN_NOTEBOOKS = 5

TIMEOUT_NEURO_LOGIN = 15
TIMEOUT_NEURO_RUN_CPU = 30
TIMEOUT_NEURO_RUN_GPU = 5 * 60
TIMEOUT_NEURO_RMDIR_CODE = 10
TIMEOUT_NEURO_RMDIR_DATA = 60
TIMEOUT_NEURO_RMDIR_NOTEBOOKS = 10
TIMEOUT_NEURO_LS = 10
TIMEOUT_NEURO_STATUS = 10
TIMEOUT_NEURO_KILL = 10


# all variables prefixed "MK_" are taken from Makefile (without prefix)
# Project name is defined in cookiecutter.yaml, from `project_name`
UNIQUE_PROJECT_NAME = f"Test Project {unique_label()}"
MK_PROJECT_NAME = UNIQUE_PROJECT_NAME.lower().replace(" ", "-").replace("_", " ")

MK_CODE_PATH = "modules"
MK_DATA_PATH = "data"
MK_NOTEBOOKS_PATH = "notebooks"
MK_REQUIREMENTS_PATH = "requirements"
MK_RESULTS_PATH = "results"
MK_PROJECT_PATH_STORAGE = f"storage:{MK_PROJECT_NAME}"
MK_CODE_PATH_STORAGE = f"{MK_PROJECT_PATH_STORAGE}/{MK_CODE_PATH}"
MK_DATA_PATH_STORAGE = f"{MK_PROJECT_PATH_STORAGE}/{MK_DATA_PATH}"
MK_NOTEBOOKS_PATH_STORAGE = f"{MK_PROJECT_PATH_STORAGE}/{MK_NOTEBOOKS_PATH}"
MK_REQUIREMENTS_PATH_STORAGE = f"{MK_PROJECT_PATH_STORAGE}/{MK_REQUIREMENTS_PATH}"
MK_RESULTS_PATH_STORAGE = f"{MK_PROJECT_PATH_STORAGE}/{MK_RESULTS_PATH}"

MK_PROJECT_PATH_ENV = "/project"
MK_CODE_PATH_ENV = f"{MK_PROJECT_PATH_ENV}/{MK_CODE_PATH}"
MK_DATA_PATH_ENV = f"{MK_PROJECT_PATH_ENV}/{MK_DATA_PATH}"
MK_NOTEBOOKS_PATH_ENV = f"{MK_PROJECT_PATH_ENV}/{MK_NOTEBOOKS_PATH}"
MK_REQUIREMENTS_PATH_ENV = f"{MK_PROJECT_PATH_ENV}/{MK_REQUIREMENTS_PATH}"
MK_RESULTS_PATH_ENV = f"{MK_PROJECT_PATH_ENV}/{MK_RESULTS_PATH}"

MK_SETUP_NAME = f"setup-{MK_PROJECT_NAME}"
MK_TRAINING_NAME = f"training-{MK_PROJECT_NAME}"
MK_JUPYTER_NAME = f"jupyter-{MK_PROJECT_NAME}"
MK_TENSORBOARD_NAME = f"tensorboard-{MK_PROJECT_NAME}"
MK_FILEBROWSER_NAME = f"filebrowser-{MK_PROJECT_NAME}"

MK_BASE_ENV_NAME = "neuromation/base"
MK_CUSTOM_ENV_NAME = f"image:neuromation-{MK_PROJECT_NAME}"


PROJECT_APT_FILE_NAME = "apt.txt"
PROJECT_PIP_FILE_NAME = "requirements.txt"

# note: apt package 'expect' requires user input during installation
PACKAGES_APT_CUSTOM = ["python", "expect", "figlet"]
PACKAGES_PIP_CUSTOM = ["aiohttp==3.6", "aiohttp_security", "neuromation==19.9.10"]

PROJECT_CODE_DIR_CONTENT = {"main.py"}
PROJECT_NOTEBOOKS_DIR_CONTENT = {"00_notebook_tutorial.ipynb", "__init__.py"}
