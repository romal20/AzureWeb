from fastapi import FastAPI, status
import sqlalchemy
import databases
import os
import urllib

host_server = os.environ.get('host_server', 'localhost')
db_server_port = str(os.environ.get('db_server_port', '5432'))
database_name = os.environ.get('database_name', 'fastapi')
db_username = str(os.environ.get('db_username', 'postgres'))
db_password = str(os.environ.get('db_password', 'secret'))
ssl_mode = str(os.environ.get('ssl_mode','prefer'))
DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server, db_server_port, database_name, ssl_mode)

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()


app = FastAPI()


notes = sqlalchemy.Table(
    "todo",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("completed", sqlalchemy.Boolean),
)
engine = sqlalchemy.create_engine(
    #DATABASE_URL, connect_args={"check_same_thread": False}
    DATABASE_URL, pool_size=3, max_overflow=0
)

metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/home")
def home():
    print("")
    return {"message":"Hello World", "DB_URL": DATABASE_URL}


@app.get("/insert-sample-data")
async def insert():
    query = notes.insert().values(text="Sample notes", completed=False)
    last_record_id = await database.execute(query)
    return {"success":True, "id": last_record_id}


@app.get("/notes/", status_code = status.HTTP_200_OK)
async def read_notes(skip: int = 0, take: int = 20):
    query = notes.select().offset(skip).limit(take)
    return await database.fetch_all(query)