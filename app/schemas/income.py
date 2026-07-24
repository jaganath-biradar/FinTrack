from datetime import date
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class IncomeBase(BaseModel):
    source: str = Field(
        validation_alias=AliasChoices("source", "income_name"),
        serialization_alias="income_name",
    )
    amount: float
    income_date: date
    category: str

    model_config = ConfigDict(populate_by_name=True)


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(IncomeBase):
    pass


class IncomeRead(IncomeBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
