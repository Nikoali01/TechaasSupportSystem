import streamlit as st

# Initialize session state if not already done
if 'input_visible' not in st.session_state:
    st.session_state.input_visible = True


# Define a callback function to hide the chat input
def hide_input():
    st.session_state.input_visible = False


# Display the chat input if it is visible
if st.session_state.input_visible:
    chat_input = st.chat_input("Enter your message:")

    # Add a button to submit the message
    if st.button("Submit"):
        st.write(f"You submitted: {chat_input}")
        hide_input()  # Hide the input after submission

# Optionally, you can provide a way to make the input visible again
if not st.session_state.input_visible:
    if st.button("Show Input"):
        st.session_state.input_visible = True
