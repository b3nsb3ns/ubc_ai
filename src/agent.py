from dotenv import load_dotenv
_ = load_dotenv()

from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
from prompts import *
from nodes import *

#memory = SqliteSaver.from_conn_string("sqlite:///:memory:")
import sqlite3
conn = sqlite3.connect(":memory:", check_same_thread=False)
memory = SqliteSaver(conn)

keyword_graph = StateGraph(AgentState)

keyword_graph.add_node("keywords", key_words_node)
keyword_graph.add_node("importance", importance_node)
keyword_graph.add_node("enrichment", enrichment_node)
keyword_graph.add_node("query", query_node)

keyword_graph.set_entry_point("keywords")

keyword_graph.add_conditional_edges(
    "importance", 
    should_continue_key_words, 
    {"query": "query", "enrichment": "enrichment"}
)

keyword_graph.add_edge("keywords", "importance")
keyword_graph.add_edge("enrichment", "importance")

graph = keyword_graph.compile(checkpointer=memory)

task = """cmd-f is a 24-hour hackathon focused on addressing gender inequality in technology. Our main purpose is to create a safe and dedicated space for historically excluded genders to hack together. We’re trying to create access for people who have faced systemic barriers to inclusion on the basis of gender. We encourage participation from women, trans, non-binary, Two-Spirit and gender diverse people. Thus, cmd-f is only open to individuals who identify as a member of an underrepresented gender in technology.

We’re aware that gender is not the only inequality in technology. We appreciate allyship and recognize it is important in the community. We invite allies to show their support by not hacking and instead contributing in other forms, such as volunteering or mentoring. Please make sure your participation in this event is aligned with the intentions of the event. We also ask all participants who attend to trust that everyone attending is meant to be here."""
thread = {"configurable": {"thread_id": "1"}}
for s in graph.stream({
    'task': task,
    "max_revisions": 2,
    "revision_number": 0,  # Ensure revision_number starts at 0
    "key_words": [],  # Initialize key_words as an empty list
    "content": [],  # Initialize content as an empty list to avoid KeyError
}, thread):
    print(s)