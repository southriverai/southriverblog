"""
Prompter module for parsing politician queries into StatementQuery objects using LangChain.
"""

import os
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from dutch_politics.index import StatementQuery

class Prompter:

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            self.api_key = api_key
        elif os.getenv("OPENAI_API_KEY"):
            self.api_key = os.getenv("OPENAI_API_KEY")
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that parses politician queries into StatementQuery objects."),
            ("user", "{query}")
        ])

    def parse_politician_query(query: str, api_key: Optional[str] = None) -> StatementQuery:
        """
        Parse a natural language query about a politician into a StatementQuery object.

        Args:
            query: A string asking about a politician (e.g., "What did Mark Rutte say about climate change?")
            api_key: OpenAI API key (if not provided, uses OPENAI_API_KEY env var)
        
        Returns:
            StatementQuery object containing the politician name and statement description
        """
        # Initialize LangChain ChatOpenAI
        llm_kwargs = {
            "model": "gpt-4o",
            "temperature": 0
        }
        if api_key:
            llm_kwargs["api_key"] = api_key
        elif os.getenv("OPENAI_API_KEY"):
            llm_kwargs["api_key"] = os.getenv("OPENAI_API_KEY")
        
        llm = ChatOpenAI(**llm_kwargs)
        
        # Create LLM with structured output
        structured_llm = llm.with_structured_output(StatementQuery)
        
        # Create prompt asking to extract politician and statement information
        prompt = f"""Parse the following query about a politician and extract:
    1. The name of the politician mentioned
    2. A description of what statement or topic is being asked about

    Query: {query}

    Extract the politician's name and a clear description of the statement or topic being queried.
    If the politician's name is not explicitly mentioned, try to infer it from context.
    If the statement description is vague, provide a clear description based on the query."""

        # Create message
        message = HumanMessage(content=prompt)
        
        # Get structured response from model
        statement_query = structured_llm.invoke([message])
        
        return statement_query

