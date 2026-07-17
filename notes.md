# T003 Notes

## Multi-turn Conversation

Successfully tested a conversation with more than 15 turns.

The assistant correctly remembered information from earlier in the conversation because the complete message history was sent with every request.

i leanrt about stroinf history in LLM chat by creating a variable and storing all the chat .
it worked and also count all the tokens used.

# t4
in the core/tokens
the needtriming function use such logic it add all the tokens  , 1 token = 4 char and when the main chat history exceed 
6000 tokens it sends warning.


# t5 & t6

loop chat whenever we hit token limit the older chat is summarzized by the system promt stored in prompt.py into 150 words
