import asyncio
from app.db.session import AsyncSessionLocal
from app.repositories.action_item_repository import ActionItemRepository
from app.models.action_item import ActionItem
from sqlalchemy import select, func

async def main():
    repo = ActionItemRepository(None) # Won't use session for query building check
    # Let's see the SQL
    company_id = "test-company"
    count_stmt = select(ActionItem).where(ActionItem.company_id == company_id)
    count_total_stmt = count_stmt.with_only_columns(func.count()).select_from(ActionItem)
    print(f"Query: {count_total_stmt}")

if __name__ == "__main__":
    asyncio.run(main())
