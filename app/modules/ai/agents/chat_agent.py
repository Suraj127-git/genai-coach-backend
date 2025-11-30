from typing import Any
import logging
from opentelemetry import trace

class ChatAgent:
    def __init__(self, llm: Any):
        self.llm = llm
        self.logger = logging.getLogger("ai.agent.chat")
        self.tracer = trace.get_tracer("ai.agent.chat")

    def run(self, message: str) -> str:
        with self.tracer.start_as_current_span("agent.chat") as span:
            span.set_attribute("ai.input_length", len(message))
            self.logger.info(f"{{\"evt\":\"agent_chat\",\"len\":{len(message)}}}")
            try:
                from langchain.prompts import ChatPromptTemplate
                from langchain_core.output_parsers import StrOutputParser
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are an interview coach."),
                    ("human", "{input}")
                ])
                chain = prompt | self.llm.client | StrOutputParser()
                out = chain.invoke({"input": message})
            except Exception:
                out = self.llm.predict(message)
            span.set_attribute("ai.output_length", len(out))
            self.logger.info(f"{{\"evt\":\"agent_reply\",\"len\":{len(out)}}}")
            return out

