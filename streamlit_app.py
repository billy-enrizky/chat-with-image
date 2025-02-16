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
    
    with st.sidebar.expander("About", expanded=False):
        st.markdown(
            """
            # Chat With Images

            This project allows you to have a conversation with an AI assistant that can process both images and text.

            **How it works:**
            - **Image Upload:** Upload an image file (jpg, jpeg, png) that will be processed by the model.
            - **Image Conversion:** The image is converted to a base64-encoded string for integration into the chat.
            - **Chat Interaction:** Engage in a chat by typing your message. The assistant will consider the image along with your text input.
            - **Model Response:** The assistant responds using IBM's API, leveraging a vision-enabled language model.
            """
        )

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
                if msg['content'][0]['type'] == "text" and msg['content'][0]['text'].strip():
                    st.write(msg['content'][0]['text'])
        else:
            st.chat_message("assistant").write(msg["content"])
    
    user_input = st.chat_input("Type your message here...")
    
    if user_input and user_input.strip():
        message = {"role": "user",
                   "content": [{"type":"text",
                                "text": user_input}]}
        st.session_state.messages.append(message)
        st.chat_message(message['role']).write(user_input)
        
        url = "https://au-syd.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
        
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
        "project_id": "904e9692-a04f-43c9-808c-879f27478057",
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
        
        st.session_state.messages.append({"role": "assistant", "content": res_content})
        with st.chat_message("assistant"):
            st.write(res_content)
            
if __name__ == "__main__":
    main()