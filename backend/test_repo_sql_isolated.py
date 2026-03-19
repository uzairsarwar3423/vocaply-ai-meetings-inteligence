from sqlalchemy import select, func, Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ActionItem(Base):
    __tablename__ = "action_items"
    id = Column(String, primary_key=True)
    company_id = Column(String)

async def main():
    company_id = "test-company"
    count_stmt = select(ActionItem).where(ActionItem.company_id == company_id)
    # Testing both ways
    print(f"Way 1: {count_stmt.with_only_columns(func.count()).select_from(ActionItem)}")
    print(f"Way 2: {select(func.count()).select_from(count_stmt.subquery())}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
