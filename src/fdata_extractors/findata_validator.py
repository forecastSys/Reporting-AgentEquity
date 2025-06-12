import inspect
from typing import List, Any
import pandas as pd
import warnings
class FinDataValidator:
    @staticmethod
    def validate(n_quarters: Any,
                 n_years: Any,
                 selected_columns: Any,
                 max_quarters: int = 4,
                 max_years: int = 4,
                 df: pd.DataFrame = None,
                 class_name: str ="",
                 caller_name: str =""):

        # def get_caller_name():
        #     for frame_info in inspect.stack():
        #         name = frame_info.function
        #         if name not in {"wrapper", "<module>", "validate"}:
        #             return name
        #     return "<unknown>"

        # caller_name = get_caller_name()

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

        ## check selected columns
        column_names = df.columns.tolist()

        # --- Type checking ---
        if selected_columns is not None:
            if not isinstance(selected_columns, List):
                raise TypeError(
                    f"[{class_name}.{caller_name}] `selected_columms` must be a list, "
                    f"got {type(selected_columns).__name__} instead."
                )

            # Check if all selected columns exist in DataFrame
            invalid_columns = [col for col in selected_columns if col not in column_names]
            if invalid_columns:
                raise ValueError(
                    f"[{class_name}.{caller_name}] Invalid selected_columns: {invalid_columns}. "
                    f"Available columns are:\n- " + "\n- ".join(column_names)
                )

        # ## warnings
        # if selected_columns is None or len(selected_columns) == 0:
        #     available = "\n-" + "\n-".join(column_names)
        #     warnings.warn(
        #         f"[{class_name}.{caller_name}] Unrecommend arguments: selected_columms={selected_columns}. "
        #         f"You are recommend to specify at least one column from the following available options:\n{available}"
        #     )