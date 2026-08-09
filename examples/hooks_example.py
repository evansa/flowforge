"""Simple example demonstrating before_step and after_step hooks.

Run with: python examples/hooks_example.py
"""
from flowforge.core.pipeline import Pipeline

p = Pipeline("example")

@p.extract()
def extract():
    return [1, 2, 3]

@p.transform()
def transform(data):
    return [x * 2 for x in data]

@p.load()
def load(data):
    print("Loaded:", data)
    return data


def before(name, execution_id):
    print(f"[hook] before {name} ({execution_id})")


def after(name, execution_id, result=None, error=None):
    status = "error" if error else "ok"
    print(f"[hook] after {name} ({execution_id}) -> status={status}, result={result}")


# assign hook functions at runtime
p.before_step = before
p.after_step = after


if __name__ == "__main__":
    p.run()
