import inspect
from typing import List, Any
class YFinanceValidator:
    @staticmethod
    def validate(n_quarters: Any,
                 n_years: Any,
                 selected_columms: Any,
                 max_quarters: int = 4,
                 max_years: int = 4,
                 column_names: List = None,
                 class_name: str =""):
        # Check mutual exclusivity
        caller_name = inspect.stack()[1].function
        # --- Type checking ---
        if not isinstance(selected_columms, List):
            raise TypeError(
                f"[{class_name}.{caller_name}] `selected_columms` must be a list, "
                f"got {type(selected_columms).__name__} instead."
            )
        if n_quarters is not None and not isinstance(n_quarters, int):
            raise TypeError(
                f"[{class_name}.{caller_name}] `n_quarters` must be an int, "
                f"got {type(n_quarters).__name__} instead."
            )

        if n_years is not None and not isinstance(n_years, int):
            raise TypeError(
                f"[{class_name}.{caller_name}] `n_years` must be an int, "
                f"got {type(n_years).__name__} instead."
            )

        if selected_columms is None or len(selected_columms) == 0:
            available = "\n-" + "\n-".join(column_names)
            raise ValueError(
                f"[{class_name}.{caller_name}] Invalid arguments: selected_columms={selected_columms}. "
                f"You must specify at least one column from the following available options:\n{available}"
            )
        if (n_quarters is None and n_years is None) or (n_quarters is not None and n_years is not None):
            raise ValueError(
                f"[{class_name}.{caller_name}] Invalid arguments: n_quarters={n_quarters}, n_years={n_years}. "
                "You must specify exactly one of them."
            )

        # Check bounds
        if n_quarters is not None and n_quarters > max_quarters:
            raise ValueError(
                f"[{class_name}.{caller_name}] Invalid arguments: n_quarters ({n_quarters}) must be ≤ {max_quarters}."
            )

        if n_years is not None and n_years > max_years:
            raise ValueError(
                f"[{class_name}.{caller_name}] Invalid arguments: n_years ({n_years}) must be ≤ {max_years}."
            )