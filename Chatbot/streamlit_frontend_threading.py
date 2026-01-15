# adding a streamlit frontend to the basic chatbot along with streaming effect
# adding a resume chat feature to the UI  
from importlib import metadata
import streamlit as st
from basic_chatbot import workflow
from langchain_core.messages import HumanMessage
import uuid


# ************************************** Utility Functions **********************************************
def generate_thread_id():
    """Generate a Uniq ThreadID"""
    thread_id=uuid.uuid4()
    return str(thread_id)

def generate_title_from_message(message, max_length=20):
    """Generate a title from the first user message"""
    if isinstance(message, HumanMessage):
        title = message.content[:max_length]
        if len(message.content) > max_length:
            title += "..."
        return title
    return "New Chat"

def reset_chat():
    """Reset the chat when New Chat button was clicked-- 1.new uniq thread_id geneartion, 
        2.Append that thread_id back to session_state dictionary, 3.empty message_history as new chat is opened """
    thread_id = generate_thread_id()
    st.session_state['thread_id']=thread_id
    st.session_state['message_history']=[]
    st.session_state['thread_titles'][thread_id] = "New Chat"  # Default title, will update after first message

def add_thread_id(thread_id):
    """ thread_id neeeds to be addeded to session satte and a title needs to get genearted for it's chat history display on the side bar"""
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
    # Initialize title if not exists
    if thread_id not in st.session_state['thread_titles']:
        st.session_state['thread_titles'][thread_id] = "New Chat"

def load_conversation(thread_id):
    """ From LLM's response we can retrieve chat history tied with the particular thread_id like this"""
    state = workflow.get_state(config={'configurable':{'thread_id':str(thread_id)}})
    return state.values.get('messages',[])


# ************************************** Session setup ***************************************************
if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}  # Dictionary to map thread_id -> title

add_thread_id(st.session_state['thread_id'])

# ************************************** Sidebar UI ***************************************************
st.sidebar.title('ChatGPT mimic - Chatbot using Langgraph')
if st.sidebar.button('New Chat'):
    reset_chat()
st.sidebar.header('My conversations')

# Display conversations with titles
for thread_id in st.session_state['chat_threads'][::-1]:
    # Get title for this thread, fallback to truncated thread_id if no title
    title = st.session_state['thread_titles'].get(thread_id, f"Chat {str(thread_id)[:8]}")
    
    if st.sidebar.button(title, key=f"thread_{thread_id}"):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages=[]

        for msg in messages:
            if isinstance(msg, HumanMessage): 
                role='user'
            else:
                role= 'assistant'
            temp_messages.append({'role':role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages
        st.rerun()  # Refresh to show the selected conversation


# *************************************** Main UI  *****************************************************
# first load conversation history and display till then's data
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# take user input
user_input=st.chat_input('Type Here')

# append 
if user_input:
    # Update title if this is the first message in a new chat
    if st.session_state['thread_id'] not in st.session_state['thread_titles'] or \
       st.session_state['thread_titles'][st.session_state['thread_id']] == "New Chat":
        # Generate title from first message
        st.session_state['thread_titles'][st.session_state['thread_id']] = generate_title_from_message(
            HumanMessage(content=user_input)
        )

    #  frist add the msg to msseage_history
    st.session_state['message_history'].append({'role': 'user' , 'content':user_input})
    with st.chat_message('user'):
        st.text(user_input)


    # add the msg to message_history
    CONFIG={'configurable': {'thread_id': str(st.session_state['thread_id'])}}
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
           message_chunk.content for message_chunk, metadata in workflow.stream(
                {'messages': [HumanMessage(content=user_input)]}, 
                config = CONFIG,
                stream_mode ='messages'
            )
        )
    st.session_state['message_history'].append({'role': 'assistant' , 'content':ai_message})