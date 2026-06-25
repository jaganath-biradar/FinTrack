from datetime import date
from pydantic import BaseModel, ConfigDict


class InvestmentBase(BaseModel):
    investment_type: str
    amount: float
    investment_date: date
    expected_return: float | None = None


class InvestmentCreate(InvestmentBase):
    pass


class InvestmentUpdate(InvestmentBase):
    pass


class InvestmentRead(InvestmentBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
