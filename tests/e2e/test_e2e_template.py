from pathlib import Path
from typing import Any, List

import pytest

from tests.e2e.configuration import (
    EXISTING_PROJECT_SLUG,
    GCP_KEY_JSON,
    JOB_ID_PATTERN,
    MK_BASE_ENV_NAME,
    MK_CODE_DIR,
    MK_CONFIG_DIR,
    MK_DATA_DIR,
    MK_DEVELOP_JOB,
    MK_FILEBROWSER_JOB,
    MK_JUPYTER_JOB,
    MK_NOTEBOOKS_DIR,
    MK_PROJECT_DIRS,
    MK_PROJECT_FILES,
    MK_PROJECT_PATH_ENV,
    MK_PROJECT_PATH_STORAGE,
    MK_PROJECT_SLUG,
    MK_SETUP_JOB,
    MK_TENSORBOARD_JOB,
    MK_TRAINING_JOB,
    N_FILES,
    PACKAGES_APT_CUSTOM,
    PACKAGES_PIP_CUSTOM,
    PROJECT_CODE_DIR_CONTENT,
    PROJECT_CONFIG_DIR_CONTENT,
    PROJECT_HIDDEN_FILES,
    PROJECT_NOTEBOOKS_DIR_CONTENT,
    TIMEOUT_MAKE_CLEAN_DATA,
    TIMEOUT_MAKE_CLEAN_NOTEBOOKS,
    TIMEOUT_MAKE_DOWNLOAD_NOTEBOOKS,
    TIMEOUT_MAKE_SETUP,
    TIMEOUT_MAKE_UPLOAD_CODE,
    TIMEOUT_MAKE_UPLOAD_CONFIG,
    TIMEOUT_MAKE_UPLOAD_DATA,
    TIMEOUT_MAKE_UPLOAD_NOTEBOOKS,
    TIMEOUT_NEURO_EXEC,
    TIMEOUT_NEURO_KILL,
    TIMEOUT_NEURO_LOGS,
    TIMEOUT_NEURO_PORT_FORWARD,
    TIMEOUT_NEURO_RMDIR_CODE,
    TIMEOUT_NEURO_RMDIR_CONFIG,
    TIMEOUT_NEURO_RMDIR_DATA,
    TIMEOUT_NEURO_RMDIR_NOTEBOOKS,
    TIMEOUT_NEURO_RUN_CPU,
    _get_pattern_pip_installing,
    _get_pattern_status_running,
    _get_pattern_status_succeeded_or_running,
    _pattern_copy_file_finished,
    _pattern_copy_file_started,
    _pattern_upload_dir,
)
from tests.e2e.helpers.runners import (
    ls_dirs,
    ls_files,
    neuro_ls,
    neuro_rm_dir,
    parse_job_id,
    parse_job_url,
    repeat_until_success,
    run,
    try_except_finally,
    wait_job_change_status_to,
)
from tests.e2e.helpers.utils import cleanup_local_dirs, measure_time, timeout


STEP_PRE_SETUP = 0
STEP_SETUP = 3
STEP_POST_SETUP = 7
STEP_UPLOAD = 10
STEP_DOWNLOAD = 20
STEP_RUN = 30
STEP_KILL = 90
STEP_CLEANUP = 100
STEP_LOCAL = 200


@pytest.mark.run(order=STEP_PRE_SETUP)
def test_project_structure() -> None:
    assert ls_dirs(".") == MK_PROJECT_DIRS
    assert ls_files(".") == {"Makefile", "README.md", ".gitignore", *MK_PROJECT_FILES}


@pytest.mark.run(order=STEP_PRE_SETUP)
@try_except_finally()
def test_make_help_works() -> None:
    out = run("make help", verbose=True)
    assert "setup" in out, f"not found in output: `{out}`"


@pytest.mark.run(order=STEP_PRE_SETUP)
@try_except_finally()
def test_make_setup_required() -> None:
    run(
        "make jupyter",
        expect_patterns=["Please run 'make setup' first", "Error"],
        assert_exit_code=False,
    )


@pytest.mark.run(order=STEP_PRE_SETUP)
def test_make_gcloud_check_auth_failure() -> None:
    key = Path(MK_CONFIG_DIR) / GCP_KEY_JSON
    if key.exists():
        key.unlink()  # key must not exist in this test

    make_cmd = "make gcloud-check-auth"
    run(
        make_cmd,
        expect_patterns=["ERROR: Not found Google Cloud service account key file"],
        assert_exit_code=False,
    )


@pytest.mark.run(order=STEP_PRE_SETUP + 1)
def test_make_gcloud_check_auth_success(decrypt_gcp_key: None) -> None:
    key = Path(MK_CONFIG_DIR) / GCP_KEY_JSON
    assert key.exists(), f"{key.absolute()} must exist"

    make_cmd = "make gcloud-check-auth"
    run(
        make_cmd,
        expect_patterns=[
            "Google Cloud will be authenticated via service account key file"
        ],
        assert_exit_code=False,
    )


@pytest.mark.run(order=STEP_SETUP)
@pytest.mark.skipif(
    condition=EXISTING_PROJECT_SLUG is not None and len(EXISTING_PROJECT_SLUG) > 0,
    reason="Reusing existing project, no need to run setup",
)
def test_make_setup() -> None:
    try:
        _run_make_setup_test()
    except Exception:
        pytest.exit(f"Test on `make setup` failed, aborting the whole test suite.")
        raise


@try_except_finally(f"neuro kill {MK_SETUP_JOB}")
def _run_make_setup_test() -> None:
    project_files_messages = []
    for file in MK_PROJECT_FILES:
        project_files_messages.append(_pattern_copy_file_started(file))
        project_files_messages.append(_pattern_copy_file_finished(file))
    # TODO: test also pre-installed APT packages
    apt_deps_messages = [
        f"Selecting previously unselected package {entry}"
        for entry in PACKAGES_APT_CUSTOM
    ]
    # TODO: test also pre-installed PIP packages
    pip_deps = sorted(
        [entry.replace("==", "-").replace("_", "-") for entry in PACKAGES_PIP_CUSTOM]
    )
    pip_deps_message = r"Successfully installed [^\n]*" + r"[^\n]*".join(pip_deps)

    expected_patterns = [
        # run
        _get_pattern_status_running(),
        # apt-get install
        *apt_deps_messages,
        # pip install
        # (pip works either with stupid progress bars, or completely silently)
        pip_deps_message,
        # neuro save
        r"Saving .+ \->",
        r"Creating image",
        r"Image created",
        r"Pushing image .+ => .+",
        r"image://.*",
        # neuro kill
        r"neuro[\w\- ]* kill ",
        r"job\-[^\n]+",
    ]

    make_cmd = "make setup"
    with measure_time(make_cmd):
        run(
            make_cmd,
            verbose=True,
            timeout_s=TIMEOUT_MAKE_SETUP,
            expect_patterns=expected_patterns,
            # TODO: add specific error patterns
        )

    assert ".setup_done" in ls_files(".")


@pytest.mark.run(order=STEP_POST_SETUP)
@try_except_finally(f"neuro kill {MK_SETUP_JOB}")
def test_make_kill_setup() -> None:
    cmd = "sleep 1h"
    run(
        f"neuro run -s cpu-small --detach -n {MK_SETUP_JOB} {MK_BASE_ENV_NAME} '{cmd}'",
        expect_patterns=[_get_pattern_status_running()],
        detect_new_jobs=True,
        assert_exit_code=False,
    )
    cmd = "make kill-setup"
    with measure_time(cmd):
        run(cmd, detect_new_jobs=False)


@pytest.mark.run(order=STEP_RUN)
@pytest.mark.skip(reason="Flaky but not crucially important test, see issue #190")
def test_import_code_in_notebooks() -> None:
    _run_import_code_in_notebooks_test()


@try_except_finally(f"neuro kill {MK_JUPYTER_JOB}")
def _run_import_code_in_notebooks_test() -> None:
    out = run(
        "make jupyter HTTP_AUTH=--no-http-auth PRESET=cpu-small",
        verbose=True,
        expect_patterns=[_get_pattern_status_running()],
        timeout_s=TIMEOUT_NEURO_RUN_CPU,
        assert_exit_code=False,
    )
    job_id = parse_job_id(out)

    expected_string = "----\r\nHello World!\r\n----"

    out_file = f"/tmp/out-nbconvert-{MK_PROJECT_SLUG}"
    jupyter_nbconvert_cmd = "jupyter nbconvert --execute --no-prompt --no-input"
    notebook_path = f"{MK_PROJECT_PATH_ENV}/{MK_NOTEBOOKS_DIR}/Untitled.ipynb"
    cmd = (
        f"{jupyter_nbconvert_cmd} --to=asciidoc --output={out_file} {notebook_path} &&"
        f"cat {out_file}.asciidoc"
    )
    run(
        f"neuro exec --no-key-check --no-tty {job_id} 'bash -c \"{cmd}\"'",
        verbose=True,
        expect_patterns=[fr"Writing \d+ bytes to {out_file}", expected_string],
        error_patterns=["Error: ", "CRITICAL"],
        detect_new_jobs=False,
        assert_exit_code=False,
    )

    cmd = "make kill-jupyter"
    with measure_time(cmd):
        run(cmd, detect_new_jobs=False)


@pytest.mark.run(order=STEP_UPLOAD)
@try_except_finally()
def test_make_upload_code() -> None:
    assert ls_files(MK_CODE_DIR) == PROJECT_CODE_DIR_CONTENT
    neuro_rm_dir(
        f"{MK_PROJECT_PATH_STORAGE}/{MK_CODE_DIR}", timeout_s=TIMEOUT_NEURO_RMDIR_CODE
    )

    # Upload:
    make_cmd = "make upload-code"
    with measure_time(make_cmd):
        run(
            make_cmd,
            verbose=True,
            timeout_s=TIMEOUT_MAKE_UPLOAD_CODE,
            expect_patterns=[_pattern_upload_dir(MK_PROJECT_SLUG, MK_CODE_DIR)],
            # TODO: add upload-specific error patterns
        )
    actual = neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_CODE_DIR}")
    assert actual == PROJECT_CODE_DIR_CONTENT


@pytest.mark.run(order=STEP_UPLOAD)
@try_except_finally()
def test_make_upload_data() -> None:
    assert len(ls_files(MK_DATA_DIR)) == N_FILES
    neuro_rm_dir(
        f"{MK_PROJECT_PATH_STORAGE}/{MK_DATA_DIR}", timeout_s=TIMEOUT_NEURO_RMDIR_DATA
    )

    # Upload:
    make_cmd = "make upload-data"
    with measure_time(make_cmd):
        run(
            make_cmd,
            verbose=True,
            timeout_s=TIMEOUT_MAKE_UPLOAD_DATA,
            expect_patterns=[_pattern_upload_dir(MK_PROJECT_SLUG, MK_DATA_DIR)],
            # TODO: add upload-specific error patterns
        )
    actual = neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_DATA_DIR}")
    assert len(actual) == N_FILES
    assert all(name.endswith(".tmp") for name in actual)


@pytest.mark.run(order=STEP_UPLOAD)
def test_make_upload_config(decrypt_gcp_key: None) -> None:
    assert ls_files(MK_CONFIG_DIR) == PROJECT_CONFIG_DIR_CONTENT
    neuro_rm_dir(
        f"{MK_PROJECT_PATH_STORAGE}/{MK_CONFIG_DIR}",
        timeout_s=TIMEOUT_NEURO_RMDIR_CONFIG,
    )

    # Upload:
    make_cmd = "make upload-config"
    with measure_time(make_cmd):
        run(
            make_cmd,
            verbose=True,
            timeout_s=TIMEOUT_MAKE_UPLOAD_CONFIG,
            expect_patterns=[_pattern_upload_dir(MK_PROJECT_SLUG, MK_CONFIG_DIR)],
            # TODO: add upload-specific error patterns
        )
    actual = neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_CONFIG_DIR}")
    assert actual == PROJECT_CONFIG_DIR_CONTENT


@pytest.mark.run(order=STEP_UPLOAD)
@try_except_finally()
def test_make_upload_notebooks() -> None:
    assert ls_files(MK_NOTEBOOKS_DIR) == PROJECT_NOTEBOOKS_DIR_CONTENT
    neuro_rm_dir(
        f"{MK_PROJECT_PATH_STORAGE}/{MK_NOTEBOOKS_DIR}",
        timeout_s=TIMEOUT_NEURO_RMDIR_NOTEBOOKS,
    )

    make_cmd = "make upload-notebooks"
    with measure_time(make_cmd):
        run(
            make_cmd,
            verbose=True,
            timeout_s=TIMEOUT_MAKE_UPLOAD_NOTEBOOKS,
            expect_patterns=[_pattern_upload_dir(MK_PROJECT_SLUG, MK_NOTEBOOKS_DIR)],
            # TODO: add upload-specific error patterns
        )
    actual_remote = neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_NOTEBOOKS_DIR}")
    assert actual_remote == PROJECT_NOTEBOOKS_DIR_CONTENT


@pytest.mark.run(order=STEP_UPLOAD)
@try_except_finally()
def test_make_upload_all() -> None:
    # just check exit code
    cmd = "make upload-all"
    run(cmd, verbose=True, detect_new_jobs=False)


@pytest.mark.run(order=STEP_DOWNLOAD)
@try_except_finally()
def test_make_download_noteboooks() -> None:
    actual_remote = neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_NOTEBOOKS_DIR}")
    assert actual_remote == PROJECT_NOTEBOOKS_DIR_CONTENT

    # Download:
    make_cmd = "make download-notebooks"
    cleanup_local_dirs(MK_NOTEBOOKS_DIR)
    with measure_time(make_cmd):
        run(
            make_cmd,
            verbose=True,
            timeout_s=TIMEOUT_MAKE_DOWNLOAD_NOTEBOOKS,
            expect_patterns=[_pattern_upload_dir(MK_PROJECT_SLUG, MK_NOTEBOOKS_DIR)],
            # TODO: add upload-specific error patterns
        )
    actual_local = {
        path.name
        for path in Path(MK_NOTEBOOKS_DIR).iterdir()
        if path.name not in PROJECT_HIDDEN_FILES
    }
    assert actual_local == PROJECT_NOTEBOOKS_DIR_CONTENT


@pytest.mark.run(order=STEP_RUN)
def test_make_train_default_command(env_neuro_run_timeout: int) -> None:
    expect_patterns = [
        _get_pattern_status_succeeded_or_running(),
        "Replace this placeholder with a training script execution",
    ]
    _run_make_train_test(env_neuro_run_timeout, expect_patterns=expect_patterns)


@pytest.mark.run(order=STEP_RUN)
def test_make_train_custom_command(
    monkeypatch: Any, env_neuro_run_timeout: int, env_py_command_check_gpu: str
) -> None:
    cmd = env_py_command_check_gpu
    cmd = cmd.replace('"', r"\"")
    cmd = f"'python -W ignore -c \"{cmd}\"'"
    monkeypatch.setenv("TRAINING_COMMAND", cmd)
    # TODO: tensorflow outputs a lot of debug info even with `python -W ignore`.
    #  To disable this, export env var `TF_CPP_MIN_LOG_LEVEL=3`
    #  (note: currently, `make train` doesn't allow us to set custom env vars, see #227)
    _run_make_train_test(env_neuro_run_timeout, expect_patterns=[])


@try_except_finally(f"neuro kill {MK_TRAINING_JOB}")
def _run_make_train_test(neuro_run_timeout: int, expect_patterns: List[str]) -> None:
    cmd = "make train"
    with measure_time(cmd):
        run(
            cmd,
            timeout_s=neuro_run_timeout,
            expect_patterns=expect_patterns,
            verbose=True,
            detect_new_jobs=True,
        )


@pytest.mark.run(order=STEP_RUN)
def test_make_run_jupyter(env_neuro_run_timeout: int) -> None:
    _run_make_run_jupyter_test(env_neuro_run_timeout)


@try_except_finally(f"neuro kill {MK_JUPYTER_JOB}")
def _run_make_run_jupyter_test(neuro_run_timeout: int) -> None:
    _test_make_run_something_useful("jupyter", "/tree", neuro_run_timeout)


@pytest.mark.run(order=STEP_RUN)
@try_except_finally(f"neuro kill {MK_TENSORBOARD_JOB}")
def test_make_run_tensorboard() -> None:
    _test_make_run_something_useful("tensorboard", "/", TIMEOUT_NEURO_RUN_CPU)


@pytest.mark.run(order=STEP_RUN)
@try_except_finally(f"neuro kill {MK_FILEBROWSER_JOB}")
def test_make_run_filebrowser() -> None:
    _test_make_run_something_useful(
        "filebrowser", "/files/requirements.txt", TIMEOUT_NEURO_RUN_CPU
    )


def _test_make_run_something_useful(target: str, path: str, timeout_run: int) -> None:
    # Can't test web UI with HTTP auth
    make_cmd = f"make {target} HTTP_AUTH=--no-http-auth"
    with measure_time(make_cmd):
        out = run(
            make_cmd,
            verbose=True,
            timeout_s=timeout_run,
            expect_patterns=[_get_pattern_status_running()],
            assert_exit_code=False,
        )
    job_id = parse_job_id(out)
    url = parse_job_url(out)

    cmd = "make ps"
    with measure_time(cmd):
        out = run(cmd, verbose=True, detect_new_jobs=False)
    assert job_id in out, f"Not found job '{job_id}' in neuro-ps output: '{out}'"

    with timeout(2 * 60):
        repeat_until_success(
            f"curl --fail {url}{path}",
            job_id,
            expect_patterns=[r"<[^>]*html.*>"],
            error_patterns=["curl: .+"],
            verbose=False,
            assert_exit_code=False,
        )

    make_cmd = f"make kill-{target}"
    with measure_time(make_cmd):
        run(make_cmd, verbose=True, timeout_s=TIMEOUT_NEURO_KILL)
    wait_job_change_status_to(job_id, "succeeded")


@pytest.mark.run(order=STEP_RUN)
def test_make_develop_all(env_neuro_run_timeout: int) -> None:
    _run_make_develop_all_test(env_neuro_run_timeout)


@try_except_finally(f"neuro kill {MK_DEVELOP_JOB}")
def _run_make_develop_all_test(neuro_run_timeout: int) -> None:
    cmd = "make develop"
    with measure_time(cmd):
        run(
            cmd,
            verbose=True,
            expect_patterns=[r"Status:[^\n]+running"],
            timeout_s=neuro_run_timeout,
        )

    cmd = "make connect-develop"
    with measure_time(cmd):
        run(
            cmd,
            verbose=True,
            expect_patterns=[rf"root@{JOB_ID_PATTERN}:/#"],
            timeout_s=TIMEOUT_NEURO_EXEC,
            assert_exit_code=False,
        )
    # TODO: improve this test by sending command `echo 123`
    #  and then reading it via `make logs-develop` (needs improvements of runners)

    cmd = "make logs-develop"
    with measure_time(cmd):
        run(
            cmd,
            verbose=True,
            expect_patterns=["Starting SSH server"],
            timeout_s=TIMEOUT_NEURO_LOGS,
            assert_exit_code=False,
        )

    cmd = "make port-forward-develop"
    with measure_time(cmd):
        run(
            cmd,
            verbose=True,
            expect_patterns=[r"Press \^C to stop forwarding"],
            timeout_s=TIMEOUT_NEURO_PORT_FORWARD,
            assert_exit_code=False,
        )

    cmd = "make kill-develop"
    with measure_time(cmd):
        run(cmd, detect_new_jobs=False)


@pytest.mark.run(order=STEP_RUN)
def test_make_develop_connect_gsutil(decrypt_gcp_key: Any) -> None:
    _test_make_develop_connect_gsutil()


@try_except_finally(f"neuro kill {MK_DEVELOP_JOB}")
def _test_make_develop_connect_gsutil() -> None:
    cmd = "make develop  PRESET=cpu-small"
    _test_make_run_job_connect_gsutil(cmd)


@pytest.mark.run(order=STEP_RUN)
def test_make_train_connect_gsutil(decrypt_gcp_key: Any) -> None:
    _test_make_train_connect_gsutil()


@try_except_finally(f"neuro kill {MK_DEVELOP_JOB}")
def _test_make_train_connect_gsutil() -> None:
    cmd = "make develop  PRESET=cpu-small TRAINING_COMMAND='sleep 1h'"
    _test_make_run_job_connect_gsutil(cmd)


@pytest.mark.run(order=STEP_RUN)
def test_make_jupyter_connect_gsutil(decrypt_gcp_key: Any) -> None:
    _test_make_jupyter_connect_gsutil()


@try_except_finally(f"neuro kill {MK_DEVELOP_JOB}")
def _test_make_jupyter_connect_gsutil() -> None:
    cmd = "make jupyter  PRESET=cpu-small"
    _test_make_run_job_connect_gsutil(cmd)


def _test_make_run_job_connect_gsutil(run_job_cmd: str) -> None:
    with measure_time(run_job_cmd):
        out = run(
            run_job_cmd,
            verbose=True,
            expect_patterns=[r"Status:[^\n]+running"],
            timeout_s=TIMEOUT_NEURO_RUN_CPU,
            assert_exit_code=False,
        )
        job_id = parse_job_id(out)

    bash_cmd = "gsutil cat gs://cookiecutter-e2e/hello.txt"
    cmd = f"neuro exec -T --no-key-check {job_id} '{bash_cmd}'"
    with measure_time(cmd):
        run(
            cmd,
            verbose=True,
            expect_patterns=["Hello world!"],
            timeout_s=TIMEOUT_NEURO_EXEC,
        )

    py_cmd_list = [
        "from google.cloud import storage",
        'bucket = storage.Client().get_bucket("cookiecutter-e2e")',
        'text = bucket.get_blob("hello.txt").download_as_string()',
        "print(text)",
        'assert "Hello world" in text.decode()',
    ]
    py_cmd = "; ".join(py_cmd_list)
    py_cmd = py_cmd.replace('"', r"\"")
    cmd = f"neuro exec -T --no-key-check {job_id} 'python -c \"{py_cmd}\"'"
    with measure_time(cmd):
        run(
            cmd,
            verbose=True,
            expect_patterns=["Hello world!"],
            error_patterns=["AssertionError"],
            timeout_s=TIMEOUT_NEURO_EXEC,
        )


@pytest.mark.run(order=STEP_KILL)
@try_except_finally(f"neuro kill {MK_TRAINING_JOB}")
def test_make_connect_train_kill_train() -> None:
    cmd = "make train PRESET=cpu-small TRAINING_COMMAND='sleep 3h'"
    with measure_time(cmd):
        run(
            cmd,
            verbose=True,
            detect_new_jobs=True,
            expect_patterns=[_get_pattern_status_running()],
            assert_exit_code=False,
        )

    cmd = "make connect-train"
    with measure_time(cmd):
        run(
            cmd,
            verbose=True,
            detect_new_jobs=False,
            expect_patterns=[fr"root@{JOB_ID_PATTERN}:/#"],
            assert_exit_code=False,
        )

    cmd = "make kill-train"
    with measure_time(cmd):
        run(cmd, detect_new_jobs=False)


@pytest.mark.run(order=STEP_KILL)
@try_except_finally()
def test_make_kill_all() -> None:
    # just check exit code
    cmd = f"make kill-all"
    with measure_time(cmd):
        run(cmd, verbose=True, detect_new_jobs=False)


@pytest.mark.run(order=STEP_CLEANUP)
@try_except_finally()
def test_make_clean_code() -> None:
    actual = neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_CODE_DIR}")
    assert actual == PROJECT_CODE_DIR_CONTENT

    make_cmd = "make clean-code"
    with measure_time(make_cmd):
        run(
            make_cmd,
            verbose=True,
            timeout_s=TIMEOUT_MAKE_UPLOAD_CODE,
            # TODO: add clean-specific error patterns
        )
    assert not neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_CODE_DIR}")


@pytest.mark.run(order=STEP_CLEANUP)
@try_except_finally()
def test_make_clean_config() -> None:
    actual = neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_CONFIG_DIR}")
    assert actual == PROJECT_CONFIG_DIR_CONTENT

    make_cmd = "make clean-config"
    with measure_time(make_cmd):
        run(
            make_cmd,
            verbose=True,
            timeout_s=TIMEOUT_MAKE_UPLOAD_CONFIG,
            # TODO: add clean-specific error patterns
        )
    assert not neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_CONFIG_DIR}")


@pytest.mark.run(order=STEP_CLEANUP)
@try_except_finally()
def test_make_clean_data() -> None:
    actual = neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_DATA_DIR}")
    assert len(actual) == N_FILES
    assert all(name.endswith(".tmp") for name in actual)

    make_cmd = "make clean-data"
    with measure_time(make_cmd):
        run(
            make_cmd,
            verbose=True,
            timeout_s=TIMEOUT_MAKE_CLEAN_DATA,
            # TODO: add clean-specific error patterns
        )
    assert not neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_DATA_DIR}")


@pytest.mark.run(order=STEP_CLEANUP)
@try_except_finally()
def test_make_clean_notebooks() -> None:
    actual_remote = neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_NOTEBOOKS_DIR}")
    assert actual_remote == PROJECT_NOTEBOOKS_DIR_CONTENT

    make_cmd = "make clean-notebooks"
    with measure_time(make_cmd):
        run(
            make_cmd,
            verbose=True,
            timeout_s=TIMEOUT_MAKE_CLEAN_NOTEBOOKS,
            # TODO: add clean-specific error patterns
        )
    assert not neuro_ls(f"{MK_PROJECT_PATH_STORAGE}/{MK_NOTEBOOKS_DIR}")


@pytest.mark.run(order=STEP_CLEANUP)
@try_except_finally()
def test_make_clean_all() -> None:
    # just check exit code
    cmd = "make clean-all"
    run(cmd, verbose=True, detect_new_jobs=False)


@pytest.mark.run(order=STEP_LOCAL)
@try_except_finally()
def test_make_setup_local() -> None:
    # just check exit code
    cmd = "make setup-local"
    run(
        cmd,
        expect_patterns=[
            _get_pattern_pip_installing(pip) for pip in PACKAGES_PIP_CUSTOM
        ],
        verbose=True,
        detect_new_jobs=False,
    )


@pytest.mark.run(order=STEP_LOCAL)
@try_except_finally()
def test_make_lint() -> None:
    # just check exit code
    cmd = "make lint"
    run(cmd, verbose=True, detect_new_jobs=False)
