from datetime import date
from pydantic import BaseModel, ConfigDict


class ExpenseBase(BaseModel):
    expense_name: str
    amount: float
    expense_date: date
    category: str


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(ExpenseBase):
    pass


class ExpenseRead(ExpenseBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
