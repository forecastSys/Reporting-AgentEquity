from functools import wraps
from typing import Callable, List
import pandas as pd

def apply_selection(data_getter_func: Callable):
    """Decorator to standardize quarterly/yearly selection and validation."""
    @wraps(data_getter_func)
    def wrapper(self, **kwargs) -> pd.DataFrame:
        # Extract named arguments with defaults
        n_quarters = kwargs.get('n_quarters', None)
        n_years = kwargs.get('n_years', None)
        selected_columms = kwargs.get('selected_columms', None)

        # Choose the DataFrame
        df = data_getter_func(self, quarterly=(n_quarters is not None))

        # Extract available column names
        column_names = df.columns.tolist()

        # Validate input
        self.validate(
            n_quarters=n_quarters,
            n_years=n_years,
            selected_columms=selected_columms,
            column_names=column_names,
            class_name=self.__class__.__name__
        )

        # Slice and return
        period = n_quarters if n_quarters is not None else n_years
        df = df[-period:][selected_columms].dropna()
        df.columns = [f"{col}".replace(' ', '_').lower() for col in df.columns]
        return df

    return wrapper

def apply_selection_growth(data_getter_func: Callable):
    """Decorator to standardize quarterly/yearly selection and validation."""
    @wraps(data_getter_func)
    def wrapper(self, **kwargs) -> pd.DataFrame:
        # Extract named arguments with defaults
        n_quarters = kwargs.get('n_quarters', None)
        n_years = kwargs.get('n_years', None)
        selected_columms = kwargs.get('selected_columns', None)

        # Choose the DataFrame
        df = data_getter_func(self, quarterly=(n_quarters is not None))

        # Extract available column names
        column_names = df.columns.tolist()

        # Validate input
        self.validate(
            n_quarters=n_quarters,
            n_years=n_years,
            selected_columms=selected_columms,
            column_names=column_names,
            class_name=self.__class__.__name__
        )

        # Slice and return
        period = n_quarters if n_quarters is not None else n_years
        selcted_df = df[-period-1:][selected_columms].dropna()
        growth_df = selcted_df.astype(float).pct_change().dropna()
        growth_df.columns = [f"{col}_growth_rate".replace(' ', '_').lower() for col in growth_df.columns]
        return growth_df

    return wrapper