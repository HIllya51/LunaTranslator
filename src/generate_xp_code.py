import os, re
import ast


class TypeHintRemover_1(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        node.returns = None
        if node.args.args:
            for arg in node.args.args:
                arg.annotation = None
        return node


class TypeHintRemover_2(ast.NodeTransformer):
    def visit_AnnAssign(self, node):
        obj = ast.Assign([node.target], node.value)
        obj.lineno = node.lineno
        return obj


def typeHintRemover(source):
    parsed_source = ast.parse(source)
    transformed = TypeHintRemover_1().visit(parsed_source)
    transformed = TypeHintRemover_2().visit(transformed)
    return ast.unparse(transformed)


def parsecode(code: str):
    # PyQt
    code = code.replace("self.screen().geometry().height()", "99999")
    code = code.replace("self.parent().devicePixelRatioF()", "1")
    code = code.replace("self.devicePixelRatioF()", "1")
    code = re.sub(
        r"(Q[a-zA-Z0-9_]+)\.[a-zA-Z0-9_]+\.([a-zA-Z0-9_]+)([ \)\n,:])", r"\1.\2\3", code
    )
    code = typeHintRemover(code)
    return code


for _dir, _, _fs in os.walk("./LunaTranslator"):
    for _f in _fs:
        if not _f.endswith(".py"):
            continue
        path = os.path.normpath(os.path.abspath(os.path.join(_dir, _f)))
        with open(path, "r", encoding="utf8") as ff:
            code = ff.read()
        with open(path, "w", encoding="utf8") as ff:
            ff.write(parsecode(code))
