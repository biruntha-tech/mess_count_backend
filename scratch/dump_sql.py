from sqlalchemy.schema import CreateTable
from database import engine
import models

with open("tables.sql", "w") as f:
    for table in models.Base.metadata.sorted_tables:
        sql = str(CreateTable(table).compile(engine))
        f.write(sql + ";\n\n")
