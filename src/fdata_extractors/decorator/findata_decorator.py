from functools import wraps
from typing import Callable, List, Optional
import pandas as pd
import inspect

def apply_selection(data_getter_func: Callable):
    """Decorator to standardize quarterly/yearly selection and validation."""
    @wraps(data_getter_func)
    def wrapper(self, **kwargs) -> pd.DataFrame:
        # # Extract named arguments with defaults
        n_quarters = kwargs.get('n_quarters', None)
        n_years = kwargs.get('n_years', None)
        selected_columns = kwargs.get('selected_columns', None)

        # Choose the DataFrame
        df = data_getter_func(self, n_years=n_years, n_quarters=n_quarters)
        df.columns = [f"{col}".replace(' ', '_').lower() for col in df.columns]
        caller_name = data_getter_func.__name__
        # Validate input
        self.validate(
            n_quarters=n_quarters,
            n_years=n_years,
            selected_columns=selected_columns,
            df=df,
            class_name=self.__class__.__name__,
            caller_name=data_getter_func.__name__,
        )
        if isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.DatetimeIndex(df.index.date).astype(str)
        else:
            df.index = df.index.astype(str)

        # Slice and return
        period = n_quarters if n_quarters is not None else n_years
        if selected_columns is not None:
            df = df[-period:][selected_columns].dropna()
        else:
            df = df[-period:]
        # df.columns = [f"{col}".replace(' ', '_').lower() for col in df.columns]
        return df

    return wrapper

def apply_selection_growth(data_getter_func: Callable):
    """Decorator to standardize quarterly/yearly selection and validation."""
    @wraps(data_getter_func)
    def wrapper(self, **kwargs) -> pd.DataFrame:
        # Extract named arguments with defaults
        n_quarters = kwargs.get('n_quarters', None)
        n_years = kwargs.get('n_years', None)
        selected_columns = kwargs.get('selected_columns', None)

        # Choose the DataFrame
        # df = data_getter_func(self, quarterly=(n_quarters is not None))
        df = data_getter_func(self, n_years=n_years, n_quarters=n_quarters)
        df.columns = [f"{col}".replace(' ', '_').lower() for col in df.columns]
        # Validate input
        self.validate(
            n_quarters=n_quarters,
            n_years=n_years,
            selected_columns=selected_columns,
            df=df,
            class_name=self.__class__.__name__,
            caller_name=data_getter_func.__name__
        )

        # Slice and return
        period = n_quarters if n_quarters is not None else n_years
        if isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.DatetimeIndex(df.index.date).astype(str)
        else:
            df.index = df.index.astype(str)

        if selected_columns is not None:
            selcted_df = df[-period-1:][selected_columns]
        else:
            selcted_df = df[-period-1:]

        growth_df = selcted_df.astype(float).pct_change(fill_method=None)[-period:]
        growth_df.columns = [f"{col}_growth" for col in growth_df.columns]
        return growth_df
    return wrapper