import pytest
from pytest_cookies.plugin import Cookies  # type: ignore

from tests.e2e.conftest import exec
from tests.utils import inside_dir


# Also check whether comments and their removal does not break something
@pytest.mark.parametrize("preserve_comments", ["yes", "no"])
def test_apolo_flow_live(cookies: Cookies, preserve_comments: str) -> None:
    result = cookies.bake(
        extra_context={
            "flow_dir": "test-flow",
            "flow_id": "awesome_flow",
            "preserve Apolo Flow template hints": preserve_comments,
        }
    )
    with inside_dir(str(result.project_path)):
        proc = exec("apolo-flow --show-traceback ps")
        assert "JOB" in proc.stdout, proc
        proc = exec("apolo-flow --show-traceback status train", assert_exit_code=False)
        assert "is not running" in proc.stdout, proc

        proc = exec("apolo-flow --show-traceback run --dry-run train")
        assert "apolo run" in proc.stdout, proc
        assert "--tag=project:awesome-flow" in proc.stdout, proc

        proc = exec("apolo-flow --show-traceback run --dry-run remote_debug")
        assert "apolo run" in proc.stdout, proc
        assert "--tag=project:awesome-flow" in proc.stdout, proc
