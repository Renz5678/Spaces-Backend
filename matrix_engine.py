"""
Matrix Engine - SymPy-based computation of the four fundamental subspaces.
"""

from sympy import Matrix, pretty, latex, Rational, nsimplify
from typing import List, Dict, Any, Tuple, Optional
from functools import lru_cache


@lru_cache(maxsize=256)
def sympy_to_python(obj):
    """
    Recursively convert SymPy objects to Python native types for JSON serialization.
    Cached for performance optimization.
    """
    if isinstance(obj, list):
        return [sympy_to_python(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(sympy_to_python(item) for item in obj)
    elif isinstance(obj, dict):
        return {k: sympy_to_python(v) for k, v in obj.items()}
    elif hasattr(obj, 'is_Integer') and obj.is_Integer:
        return int(obj)
    elif hasattr(obj, 'is_Float') or hasattr(obj, 'is_Rational'):
        return float(obj)
    elif hasattr(obj, 'is_number') and obj.is_number:
        return float(obj)
    elif hasattr(obj, '__float__'):
        try:
            return float(obj)
        except (TypeError, ValueError):
            return str(obj)
    else:
        return obj


class MatrixEngine:
    """
    Computes the four fundamental subspaces of linear algebra:
    - Column Space (Range)
    - Row Space
    - Null Space (Kernel)
    - Left Null Space
    """

    MAX_DIMENSION = 5

    def __init__(self, matrix_data: List[List[Any]]):
        """
        Initialize with a 2D list of numeric values.
        
        Args:
            matrix_data: 2D list representing the matrix
        """
        self.raw_data = matrix_data
        self.matrix: Optional[Matrix] = None
        self._validate_and_parse()

    def _validate_and_parse(self) -> None:
        """Validate input and create SymPy Matrix."""
        if not self.raw_data:
            raise ValueError("Matrix cannot be empty")

        if not isinstance(self.raw_data, list):
            raise ValueError("Matrix must be a 2D list")

        # Check row count
        m = len(self.raw_data)
        if m > self.MAX_DIMENSION:
            raise ValueError(f"Number of rows must be ≤ {self.MAX_DIMENSION}, got {m}")

        # Check all rows are lists and have consistent length
        if not all(isinstance(row, list) for row in self.raw_data):
            raise ValueError("Each row must be a list")

        if len(self.raw_data) == 0:
            raise ValueError("Matrix cannot be empty")

        n = len(self.raw_data[0])
        if n == 0:
            raise ValueError("Matrix cannot have zero columns")

        if n > self.MAX_DIMENSION:
            raise ValueError(f"Number of columns must be ≤ {self.MAX_DIMENSION}, got {n}")

        if not all(len(row) == n for row in self.raw_data):
            raise ValueError("All rows must have the same number of columns")

        # Parse values to SymPy-compatible types
        try:
            parsed_data = []
            for row in self.raw_data:
                parsed_row = []
                for val in row:
                    # Convert to Rational for exact arithmetic
                    if isinstance(val, float):
                        parsed_row.append(nsimplify(val, rational=True))
                    elif isinstance(val, (int, str)):
                        parsed_row.append(Rational(val))
                    else:
                        parsed_row.append(Rational(val))
                parsed_data.append(parsed_row)
            
            self.matrix = Matrix(parsed_data)
        except Exception as e:
            raise ValueError(f"Invalid numeric value in matrix: {e}")

    def get_dimensions(self) -> Tuple[int, int]:
        """Return (rows, cols) of the matrix."""
        return self.matrix.shape

    def get_rank(self) -> int:
        """Return the rank of the matrix."""
        return self.matrix.rank()

    def get_rref(self) -> Tuple[Matrix, Tuple[int, ...]]:
        """
        Return the Row-Reduced Echelon Form and pivot columns.
        
        Returns:
            Tuple of (RREF matrix, tuple of pivot column indices)
        """
        return self.matrix.rref()

    def compute_column_space(self) -> List[Matrix]:
        """
        Compute basis for the Column Space (Range).
        
        The column space is the span of the columns of A.
        """
        return self.matrix.columnspace()

    def compute_row_space(self) -> List[Matrix]:
        """
        Compute basis for the Row Space.
        
        The row space is the span of the rows of A.
        """
        return self.matrix.rowspace()

    def compute_null_space(self) -> List[Matrix]:
        """
        Compute basis for the Null Space (Kernel).
        
        The null space is {x : Ax = 0}.
        """
        return self.matrix.nullspace()

    def compute_left_null_space(self) -> List[Matrix]:
        """
        Compute basis for the Left Null Space.
        
        The left null space is {y : A^T y = 0} = {y : y^T A = 0}.
        """
        return self.matrix.T.nullspace()

    def compute_all_spaces(self) -> Dict[str, Any]:
        """
        Compute all four fundamental subspaces and return comprehensive results.
        
        Returns:
            Dictionary with all subspace information
        """
        m, n = self.get_dimensions()
        rank = self.get_rank()
        rref_matrix, pivots = self.get_rref()

        column_space = self.compute_column_space()
        row_space = self.compute_row_space()
        null_space = self.compute_null_space()
        left_null_space = self.compute_left_null_space()

        return {
            "matrix": {
                "data": sympy_to_python(self.matrix.tolist()),
                "rows": m,
                "cols": n,
                "latex": latex(self.matrix),
            },
            "rank": rank,
            "rref": {
                "matrix": sympy_to_python(rref_matrix.tolist()),
                "latex": latex(rref_matrix),
                "pivots": list(pivots),
            },
            "column_space": {
                "basis": sympy_to_python([v.tolist() for v in column_space]),
                "latex": [latex(v) for v in column_space],
                "dimension": len(column_space),
                "description": f"Subspace of R^{m}",
            },
            "row_space": {
                "basis": sympy_to_python([v.tolist() for v in row_space]),
                "latex": [latex(v) for v in row_space],
                "dimension": len(row_space),
                "description": f"Subspace of R^{n}",
            },
            "null_space": {
                "basis": sympy_to_python([v.tolist() for v in null_space]),
                "latex": [latex(v) for v in null_space],
                "dimension": len(null_space),
                "description": f"Subspace of R^{n}",
            },
            "left_null_space": {
                "basis": sympy_to_python([v.tolist() for v in left_null_space]),
                "latex": [latex(v) for v in left_null_space],
                "dimension": len(left_null_space),
                "description": f"Subspace of R^{m}",
            },
            "dimension_check": {
                "rank_plus_nullity": f"{rank} + {n - rank} = {n} (columns)",
                "rank_plus_left_nullity": f"{rank} + {m - rank} = {m} (rows)",
                "valid": (len(column_space) == rank and 
                         len(row_space) == rank and
                         len(null_space) == n - rank and
                         len(left_null_space) == m - rank),
            },
        }


def format_basis_vectors(basis: List[Matrix], space_name: str) -> str:
    """Format basis vectors for display."""
    if not basis:
        return f"{space_name}: {{0}} (trivial, only zero vector)"
    
    vectors = []
    for i, v in enumerate(basis, 1):
        vectors.append(f"  v{i} = {pretty(v)}")
    
    return f"{space_name} (dimension {len(basis)}):\n" + "\n".join(vectors)
