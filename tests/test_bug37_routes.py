import ast, pathlib, pytest

APP = pathlib.Path('deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py')

EXPECTED = {
    '/config/tier':    {'GET'},
    '/anchor/set':     {'POST'},
    '/anchor/state':   {'GET'},
    '/anchor/clear':   {'POST'},
    '/anchor/dismiss': {'POST'},
    '/anchor/advice':  {'GET'},
    '/helm/mute':      {'POST'},
}

def _routes():
    """Return {rule: {methods}} for every @app.route in app.py."""
    tree = ast.parse(APP.read_text())
    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not (isinstance(dec, ast.Call) and getattr(dec.func, 'attr', '') == 'route'):
                continue
            rule = dec.args[0].value
            methods = {'GET'}
            for kw in dec.keywords:
                if kw.arg == 'methods':
                    methods = {e.value for e in kw.value.elts}
            found.setdefault(rule, set()).update(methods)
    return found

@pytest.mark.parametrize('rule,methods', EXPECTED.items())
def test_route_registered(rule, methods):
    found = _routes()
    assert rule in found, f'{rule} is not registered in app.py'
    assert methods <= found[rule], f'{rule} missing methods {methods - found[rule]}'

def test_existing_routes_survive():
    found = _routes()
    for rule in ('/', '/settings', '/anchor-watch', '/engine-monitor', '/manual'):
        assert rule in found, f'pre-existing route {rule} was removed'

def test_source_is_syntactically_valid():
    ast.parse(APP.read_text())      # raises SyntaxError if the port broke the file
