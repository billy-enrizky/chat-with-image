import streamlit as st
import base64
import requests
from PIL import Image

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
    
    response = requests.post(url=auth_url,data=data, headers=headers, verify=False)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Failed to get authentication token")
    
def main():
    st.title("Chat With Images")
    
# Add an "ABOUT" section using st.expander
    with st.expander("ABOUT", expanded=False):
        st.info("""
            This app allows users to upload an image, convert it to a base64 string, and interact with a chat interface.
            - **Upload an Image**: Choose an image file (jpg, jpeg, png) to upload.
            - **Chat Interface**: Type your message and interact with the assistant.
            - **IBM API**: The app uses IBM's API to process chat messages.
        """)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = False
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = False
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        with st.chat_message("user"):
            st.image(image, caption="Uploaded Image", use_container_width=True)
            base64_image = convert_image_to_base64(uploaded_file=uploaded_file)
            if not st.session_state.uploaded_file:
                st.session_state.messages.append({"role": "user", 
                                                  "content":[{
                                                      "type": "image_url", 
                                                      "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                                                      }]})
            else:
                pass
    for msg in st.session_state.messages[1:]:
        if msg['role'] == "user":
            with st.chat_message("user"):
                if msg['content'][0]['type'] == "text":
                    st.write(msg['content'][0]['text'])
        else:
            st.chat_message("assistant").write(msg["content"])
    
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        message = {"role": "user",
                   "content": [{"type":"text",
                                "text": user_input}]}
        st.session_state.messages.append(message)
        st.chat_message(message['role']).write(user_input)
        
        url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
        
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
                model_messages.append({"role": msg["role"], "content": [{"type": "text", "text": msg["content"]}] if isinstance(msg["content"], str) else msg["content"]})
        
        body = {
        "messages": [model_messages[-1]],
        "project_id": "fd71bef7-88db-45c9-a4b7-7e1ef83bc58b",
        "model_id": "meta-llama/llama-3-2-90b-vision-instruct",
        "decoding_method": "greedy",
        "repetition_penalty": 1,
        "max_tokens": 900
        }
        
        YOUR_ACCESS_TOKEN = get_ibm_auth_token(api_key)
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {YOUR_ACCESS_TOKEN}"
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=body
        )
        
        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()
        res_content = data['choices'][0]['message']['content']
        print(res_content)
        
        st.session_state.messages.append({"role": "assistant", "content": res_content})
        with st.chat_message("assistant"):
            st.write(res_content)
            
if __name__ == "__main__":
    main()