import sys
from io import StringIO

import flowforge.cli as cli
from flowforge.core.pipeline import Pipeline


def test_cli_history_and_info(tmp_path, monkeypatch, capsys):
    db = tmp_path / "ff.db"
    # prepare a pipeline run that uses the test db
    p = Pipeline("cli-test", database=str(db))

    @p.extract()
    def extract():
        return ["a"]

    @p.load()
    def load(data):
        return data

    run = p.run()

    # point CLI at our test database
    monkeypatch.setattr(cli, "DEFAULT_DATABASE", str(db))

    # call history
    rc = cli.main(["history"])
    assert rc == 0
    captured = capsys.readouterr()
    assert run.execution_id in captured.out

    # call info
    rc = cli.main(["info", run.execution_id])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Steps:" in captured.out
