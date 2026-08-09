from flowforge.core.pipeline import Pipeline


def test_before_after_hooks_called(tmp_path):
    db = tmp_path / "ff.db"
    p = Pipeline("hooks-test", database=str(db))

    calls = []

    @p.extract()
    def extract():
        calls.append(("extract",))
        return [1]

    @p.transform()
    def transform(data):
        calls.append(("transform", data))
        return [d + 1 for d in data]

    @p.load()
    def load(data):
        calls.append(("load", data))
        return data

    def before(name, execution_id):
        calls.append(("before", name))

    def after(name, execution_id, result=None, error=None):
        calls.append(("after", name, error is not None))

    p.before_step = before
    p.after_step = after

    run = p.run()

    # hooks and steps recorded in order
    names = [c[0] for c in calls]
    assert "before" in names
    assert "after" in names
    assert "extract" in names and "transform" in names and "load" in names
    assert run.status == "SUCCESS"
