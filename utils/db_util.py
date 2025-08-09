from prisma import Prisma
from contextlib import asynccontextmanager

# Database instance
db = Prisma()


@asynccontextmanager
async def lifespan_manager():
    # Startup
    await db.connect()
    print("Connected to database")
    yield
    # Shutdown
    await db.disconnect()
    print("Disconnected from database")


def get_db():
    return db
