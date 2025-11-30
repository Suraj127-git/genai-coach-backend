from sqlalchemy.orm import Session
from typing import Any

class DataAgent:
    def __init__(self, llm: Any, db: Session):
        self.llm = llm
        self.db = db

    def query(self, instruction: str) -> list[dict]:
        try:
            from langchain_community.utilities.sql_database import SQLDatabase
            from langchain_community.agent_toolkits import create_sql_agent
            sql_db = SQLDatabase(self.db.get_bind())
            agent = create_sql_agent(llm=self.llm.client or self.llm, db=sql_db, verbose=False)
            out = agent.invoke({"input": instruction})
            return [{"result": str(out)}]
        except Exception:
            return []
