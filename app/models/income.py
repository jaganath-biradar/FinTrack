from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source = Column(String(120), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    income_date = Column(Date, nullable=False)
    category = Column(String(80), nullable=False)

    user = relationship("User", back_populates="incomes")
