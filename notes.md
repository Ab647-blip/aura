Aura is a personal AI assistant that builds a living understanding of a user's life by connecting their emails, calendar, notes, tasks, documents, memories, goals, and other personal information into a unified knowledge system.
Unlike traditional chatbots that only respond to questions, Aura continuously remembers, organizes, prioritizes, and reasons over a user's information to provide proactive guidance, personalized recommendations, intelligent reminders, and daily planning.
The goal is to create an AI that acts like a trusted Chief of Staff—someone who knows what matters, what is pending, what should be prioritized, and helps the user make better decisions and manage their life more effectively.

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
