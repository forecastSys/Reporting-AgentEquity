from pydantic import BaseModel
from typing import List, Tuple
from enum import Enum
from typing import Literal

class SummaryGenerated(BaseModel):
    signal: Literal['Buy', 'Sell', 'Hold']
    summary: str

class ReportGenerated(BaseModel):
    report: str