
from ai_dev_assistant.rag.memory import init_conversation, append_turn, needs_summarization

def test_memory_summarization_trigger():
    state = init_conversation()
    for i in range(10):
        append_turn(state, "user", f"msg {i}")
    assert needs_summarization(state)
