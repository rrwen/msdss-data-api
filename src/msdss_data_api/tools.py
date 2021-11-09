from msdss_base_database import Database

def create_data_db_func(db = Database()):
    async def out():
        yield db
    return out
