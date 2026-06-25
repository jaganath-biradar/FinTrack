from pydantic import BaseModel, ConfigDict


class BudgetBase(BaseModel):
    category: str
    monthly_limit: float
    month: int
    year: int


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BudgetBase):
    pass


class BudgetRead(BudgetBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
