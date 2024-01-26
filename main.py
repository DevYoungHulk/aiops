import os
from pathlib import Path
from llama_index.llms import OpenAI
from llama_index import download_loader
from llama_hub.github_repo import GithubClient
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.node_parser import SentenceSplitter
from llama_index import ServiceContext, VectorStoreIndex, set_global_service_context, global_service_context
from llama_index.agent import OpenAIAgent
from llama_index import SimpleDirectoryReader
from llama_index.callbacks import CallbackManager, TokenCountingHandler
import tiktoken

model = "gpt-3.5-turbo"
llm = OpenAI(temperature=0, model=model)
token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model(model).encode,
    verbose=True
)
callback_manager = CallbackManager([token_counter])
service_context = ServiceContext.from_defaults(llm=llm)
node_parser = SentenceSplitter()
set_global_service_context(service_context)


def buildGithubEngineTool() -> QueryEngineTool:
    GithubRepositoryReader = download_loader("GithubRepositoryReader")
    github_client = GithubClient(os.getenv("GITHUB_TOKEN"))
    loader = GithubRepositoryReader(
        github_client,
        owner="DevYoungHulk",
        repo="spring-demo",
        filter_directories=(
            ["src"], GithubRepositoryReader.FilterType.INCLUDE),
        filter_file_extensions=(
            [".java"], GithubRepositoryReader.FilterType.INCLUDE),
        verbose=True,
        concurrent_requests=10,
        timeout=5,
    )

    docs = loader.load_data(branch="main")
    nodes = node_parser.get_nodes_from_documents(docs)
    print("code nodes size -> "+str(len(nodes)))
    vector_index = VectorStoreIndex(
        nodes=nodes, service_context=global_service_context)
    vector_index.storage_context.persist('./cache/github')
    vector_query_engine = vector_index .as_query_engine()

    return QueryEngineTool(
        query_engine=vector_query_engine,
        metadata=ToolMetadata(
            name="code_vector_tool",
            description=(
                "Vector Index for querying source code of java system. When you want to locate the error code you can read all the code here."
            ),
        ),
    )


def buildLogEngineTool() -> QueryEngineTool:
    UnstructuredReader = download_loader('UnstructuredReader')
    dir_reader = SimpleDirectoryReader('./data/log', file_extractor={
        ".log": UnstructuredReader(), })
    documents = dir_reader.load_data()

    nodes = node_parser.get_nodes_from_documents(documents)
    print("log nodes size -> "+str(len(nodes)))
    vector_index = VectorStoreIndex(
        nodes=nodes, service_context=global_service_context)
    vector_index.storage_context.persist('./cache/logs')
    vector_query_engine = vector_index .as_query_engine()

    return QueryEngineTool(
        query_engine=vector_query_engine,
        metadata=ToolMetadata(
            name="log_vector_tool",
            description=(
                "Vector Index for querying log messages of java system. You can use this tool to look up error messages when you need to."
            ),
        ),
    )


def init_agent() -> OpenAIAgent:
    function_llm = OpenAI(callback_manager=callback_manager)
    return OpenAIAgent.from_tools(
        [buildGithubEngineTool(),
         buildLogEngineTool(),],
        llm=function_llm,
        verbose=True,
        system_prompt=f"""\
        You are an automated ops bot that helps developers query the specific code that is having problems and provide solutions.
        You need to query logs with log_vector_tool and then find the reated code with code_vector_tool.
        You must ALWAYS use tools provided when answering a question; do NOT rely on prior knowledge.\
        """,
    )


if __name__ == "__main__":
    agent = init_agent()
    while 1:
        question = input('Input Question：')
        if question == 'exit':
            break
        elif question == 'clear':
            agent.chat_history.clear()
            round = 0
            print('Chat history have been cleared')
        response = agent.chat(question)
        print(response)
