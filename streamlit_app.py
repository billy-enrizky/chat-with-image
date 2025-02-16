import streamlit as st
import base64
import requests
from PIL import Image
import datetime

# Retrieve IBM API key from Streamlit secrets
api_key = st.secrets["IBM_API_KEY"]

def convert_image_to_base64(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    base64_image = base64.b64encode(bytes_data).decode()
    return base64_image

def get_ibm_auth_token(api_key):
    auth_url = "https://iam.cloud.ibm.com/identity/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    
    response = requests.post(url=auth_url, data=data, headers=headers, verify=False)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Failed to get authentication token")

def generate_conversation_text():
    conversation = ""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            for item in msg["content"]:
                if item["type"] == "text":
                    conversation += "User: " + item["text"] + "\n"
                elif item["type"] == "image_url":
                    conversation += "User: [Image Uploaded]\n"
        else:
            conversation += "Assistant: " + str(msg["content"]) + "\n"
    return conversation

def main():
    # Sidebar Settings
    st.sidebar.header("Settings")
    dark_mode = st.sidebar.checkbox("Dark Mode")
    max_tokens = st.sidebar.number_input("Max Tokens", min_value=100, max_value=2000, value=900, step=50)
    decoding_method = st.sidebar.selectbox("Decoding Method", options=["greedy", "beam_search", "sampling"], index=0)
    repetition_penalty = st.sidebar.slider("Repetition Penalty", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
    
    # Download conversation button
    if st.sidebar.button("Download Conversation"):
        conversation_text = generate_conversation_text()
        st.download_button(
            label="Download Chat as TXT",
            data=conversation_text,
            file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    # Clear chat button to reset conversation
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.uploaded_file = None
        st.rerun()
    
    # About section as an expander (expanded=False)
    with st.sidebar.expander("About", expanded=False):
        st.markdown(
            """
            This project allows you to have a conversation with an AI assistant that processes both images and text.
            
            **How it works:**
            - **Image Upload:** Upload an image file (jpg, jpeg, png) to be processed by the model.
            - **Image Conversion:** The image is converted into a base64-encoded string.
            - **Chat Interaction:** Engage in a chat where the assistant considers both the image and your text.
            - **Model Response:** The assistant responds via IBM's API using a vision-enabled language model.
            """
        )
    
    # Inject custom CSS styling (with dark mode support)
    if dark_mode:
        st.markdown(
            """
            <style>
            body {
                background-color: #121212;
                color: #e0e0e0;
            }
            .chat-title {
                font-size: 2.5rem;
                font-weight: bold;
                color: #BB86FC;
                text-align: center;
                margin-top: 20px;
            }
            .css-1d391kg, .css-1d391kg * {
                background-color: #1f1f1f;
                color: #e0e0e0;
            }
            </style>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            .chat-title {
                font-size: 2.5rem;
                font-weight: bold;
                color: #4A90E2;
                text-align: center;
                margin-top: 20px;
            }
            </style>
            """, unsafe_allow_html=True
        )
    
    st.markdown("<div class='chat-title'>Chat With Images</div>", unsafe_allow_html=True)
    
    # Initialize session state variables if not already set
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    
    # Main chat container
    with st.container():
        # Image uploader for image input
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
            except Exception as e:
                st.error("Error opening image file.")
            else:
                with st.chat_message("user"):
                    st.image(image, caption="Uploaded Image", use_container_width=True)
                    base64_image = convert_image_to_base64(uploaded_file)
                    if st.session_state.uploaded_file is None:
                        st.session_state.messages.append({
                            "role": "user", 
                            "content": [{
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                            }]
                        })
                        st.session_state.uploaded_file = True
        
        # Render previous chat messages
        for msg in st.session_state.messages[1:]:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    for item in msg["content"]:
                        if item["type"] == "text" and item["text"].strip():
                            st.write(item["text"])
                        elif item["type"] == "image_url":
                            url = item["image_url"]["url"]
                            st.image(url, caption="Uploaded Image", use_container_width=True)
            else:
                with st.chat_message("assistant"):
                    st.write(msg["content"])
        
        # Chat input field for user messages
        user_input = st.chat_input("Type your message here...", key="chat_input")
        if user_input and user_input.strip():
            message = {
                "role": "user",
                "content": [{"type": "text", "text": user_input}]
            }
            st.session_state.messages.append(message)
            with st.chat_message("user"):
                st.write(user_input)
            
            # Prepare payload for IBM API call
            api_url = "https://au-syd.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
            model_messages = []
            latest_image_url = None
            
            for msg in st.session_state.messages:
                if msg["role"] == "user" and isinstance(msg["content"], list):
                    content = []
                    for item in msg["content"]:
                        if item["type"] == "text":
                            content.append(item)
                        elif item["type"] == "image_url":
                            latest_image_url = item
                    if latest_image_url:
                        content.append(latest_image_url)
                    model_messages.append({"role": msg["role"], "content": content})
                else:
                    model_messages.append({
                        "role": msg["role"], 
                        "content": [{"type": "text", "text": msg["content"]}] if isinstance(msg["content"], str) else msg["content"]
                    })
            
            body = {
                "messages": [model_messages[-1]],
                "project_id": "904e9692-a04f-43c9-808c-879f27478057",
                "model_id": "meta-llama/llama-3-2-90b-vision-instruct",
                "decoding_method": decoding_method,
                "repetition_penalty": repetition_penalty,
                "max_tokens": max_tokens
            }
            
            try:
                access_token = get_ibm_auth_token(api_key)
            except Exception as e:
                st.error("Failed to get IBM authentication token.")
                return
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
            
            # Show spinner while waiting for the assistant's response
            with st.spinner("Waiting for assistant response..."):
                response = requests.post(api_url, headers=headers, json=body)
            
            if response.status_code != 200:
                st.error("Error from assistant: " + str(response.text))
                return
            
            data = response.json()
            res_content = data['choices'][0]['message']['content']
            
            st.session_state.messages.append({"role": "assistant", "content": res_content})
            with st.chat_message("assistant"):
                st.write(res_content)
                st.balloons()

if __name__ == "__main__":
    main()