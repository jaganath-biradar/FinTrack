from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    investment_type = Column(String(120), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    investment_date = Column(Date, nullable=False)
    expected_return = Column(Numeric(12, 2), nullable=True)

    user = relationship("User", back_populates="investments")
