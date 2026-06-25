from datetime import date
from pydantic import BaseModel, ConfigDict


class IncomeBase(BaseModel):
    source: str
    amount: float
    income_date: date
    category: str


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(IncomeBase):
    pass


class IncomeRead(IncomeBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
