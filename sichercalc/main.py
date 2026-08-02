import ast
import operator
from decimal import Decimal, localcontext

def _parse_string(string: str):
    node_tree = ast.parse(string)
    # The main ast node tree.
    # For example, if string is "2+2", node_tree will
    # look similar to:
    # Module(
    # | > body=Expr(
    # | >> value=BinOp(
    # | >>> left=Ast.Constant(id=2),
    # | >>> op=(Ast.Add, Ast.Sub, Ast.Mult, etc),
    # | >>> right=Ast.Constant(id=2),
    # | >> )
    # | > )
    # | )

    # Recursively evaluates the input node and returns
    # a Decimal object
    def inspect_node(node) -> Decimal:
        def expr_node(): # ast.Expr
            return inspect_node(node.value)
        def binop_node(): # ast.BinOp
            # BinOp(left=(...), op=(...), right=(...))
            left = inspect_node(node.left) # The value of BinOp(...).left attribute after being evaluated by inspect_node()
            op = node.op # BinOp(...).op
            right = inspect_node(node.right) # Same with the left attribute, but now with BinOp(...).right

            # Map of allowed operators (+, -, *, /, and **)
            op_map = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
            }
            return op_map[type(op)](left, right)
        def name_node(): # ast.Name
            raise ValueError("variables not allowed")
        def constant_node(): # ast.Constant (positive numbers only)
            return Decimal(node.value)
        def unaryop_node(): # ast.UnaryOp (A unary operation, which is an operator that applied to only one value. (like negative numbers: -5, -2, -67, etc)
            op  = node.op
            operand = inspect_node(node.operand)
            if isinstance(op, ast.USub): # -x
                return -operand
            elif isinstance(op, ast.UAdd): # +x
                return operand
            else:
                raise ValueError(f"{type(op).__name__} operation not supported")
        def module_node(): # ast.Module
            return inspect_node(node.body)

        # Map of allowed node types
        node_map = {
            ast.Expr: expr_node,
            ast.BinOp: binop_node,
            ast.Name: name_node,
            ast.Constant: constant_node,
            ast.Module: module_node,
            ast.UnaryOp: unaryop_node,
        }

        try:
            if type(node) == list:
                node = node[0]
            return node_map[type(node)]()
        # Raises an exception if node type not in node_map
        except KeyError:
            raise ValueError(f"{type(node).__name__} object not allowed.")
    return inspect_node(node_tree)

def _eval_expression(expression: str) -> Decimal:
    expression = expression.replace("^", "**").replace("%", "/ 100").replace("×", "*").replace("÷", "/")
    result = _parse_string(expression)
    return result

class SafeEvaluator:
    def __init__(self):
        ...
    def evaluate_expression(self, string: str) -> Decimal:
        return _eval_expression(string)

def _main() -> None:
    se = SafeEvaluator()
    result = se.evaluate_expression("5*5")
    print(result)
    print(type(result))

if __name__ == "__main__":
    _main()
