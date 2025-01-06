import logging
import re
import sys
from pathlib import Path

import pytest
import yaml
from cookiecutter.exceptions import FailedHookException
from pytest_cookies.plugin import Cookies  # type: ignore

from tests.utils import inside_dir


logger = logging.getLogger(__name__)


def test_flow_tree(cookies: Cookies) -> None:
    result = cookies.bake(extra_context={"flow_dir": "test-flow"})
    assert result.exception is None
    assert result.exit_code == 0
    assert result.project_path.name == "test-flow"


def test_flow_dir_hook(cookies: Cookies) -> None:
    result = cookies.bake(extra_context={"flow_dir": "myflow"})
    assert result.exit_code == 0
    result = cookies.bake(extra_context={"flow_dir": "my-flow"})
    assert result.exit_code == 0
    result = cookies.bake(extra_context={"flow_dir": "my?flow"})
    assert result.exit_code != 0
    if sys.platform == "win32":
        # Unfortunately, pre_gen hook is called before cookiecutter copies the template
        #  into the TMP dir for rendering.
        # This will not hurt the user,
        #  but the error message will also include a traceback
        assert isinstance(result.exception, OSError)
    else:
        assert isinstance(result.exception, FailedHookException)
    result = cookies.bake(extra_context={"flow_dir": "t" * 256})
    assert result.exit_code != 0


def test_flow_id_hook(cookies: Cookies) -> None:
    wrong_ids = [
        "qwe/qwe",
        "qwe?qwe",
        "qwe!qwe",
        "qwe.qwe",
        "qwe%qwe",
        "qwe-qwe",
        "-qwe",
        "qwe-",
        "qwe-qwe",
        "123",
        "1 23",
        "1qwe23",
    ]
    correct_ids = [
        "qwe",
        "q",
        "qwe_qwe",
        "_qwe",
        "qwe_",
        "qwe123",
        "qwe_123",
        "qwe" * 20,
    ]
    for id_ in wrong_ids:
        result = cookies.bake(extra_context={"flow_id": id_})
        assert result.exit_code != 0, id_
        assert isinstance(result.exception, FailedHookException)
    for id_ in correct_ids:
        result = cookies.bake(extra_context={"flow_id": id_})
        assert result.exit_code == 0, id_


@pytest.mark.parametrize("preserve_comments", ["yes", "no"])
def test_flow_config_with_comments(cookies: Cookies, preserve_comments: str) -> None:
    result = cookies.bake(
        extra_context={
            "flow_dir": "flow-with-comments",
            "preserve Apolo Flow template hints": preserve_comments,
        }
    )
    assert result.exit_code == 0
    comment_regex = re.compile(r"(\s*#(?! yaml-language-server).*)")
    with inside_dir(str(result.project_path)):
        live_file_content = Path(".apolo/live.yml").read_text()
        project_file_content = Path(".apolo/project.yml").read_text()

        l_com_exists = any(
            [
                comment_regex.match(line) is not None
                for line in live_file_content.splitlines()
            ]
        )
        p_com_exists = any(
            [
                comment_regex.match(line) is not None
                for line in project_file_content.splitlines()
            ]
        )
        if preserve_comments == "yes":
            assert l_com_exists, ".apolo/live.yml file does not contain comments"
            assert p_com_exists, ".apolo/project.yml file does not contain comments"
        elif preserve_comments == "no":
            assert not l_com_exists, ".apolo/live.yml file contains comments"
            assert not p_com_exists, ".apolo/project.yml file contains comments"
        else:
            raise RuntimeError(
                f"invalid value '{preserve_comments}' for 'preserve_comments' arg. "
                " Only 'yes' and 'no' are allowed."
            )


def test_flow_description(cookies: Cookies) -> None:
    descriptions = [
        # " ",
        "Descrition!",
        "123",
        "https://github.com/neuro-inc/flow-template/",
    ]
    for descr in descriptions:
        result = cookies.bake(extra_context={"flow_description": descr})
        assert result.exit_code == 0, descr
        with inside_dir(str(result.project_path)):
            readme_content = Path("README.md").read_text()
            if descr:
                assert "## Flow description" in readme_content
                assert descr in readme_content


def test_flow_name(cookies: Cookies) -> None:
    result = cookies.bake()

    assert result.exit_code == 0
    project_yml = result.project_path / ".apolo" / "project.yml"
    project_yml_content = yaml.safe_load(project_yml.read_text())

    assert "id" in project_yml_content
