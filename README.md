# Chat With Images - AI Assistant

## Overview
This project allows users to have a conversation with an AI assistant that can process both text and images using IBM's AI API. The assistant can analyze uploaded images and provide responses based on user interactions.

## Features
- **Image Upload:** Users can upload images (JPG, JPEG, PNG) for processing.
- **Chat Interface:** Engages in text-based conversations.
- **Image Processing:** Converts images into base64 format for analysis.
- **IBM AI Integration:** Utilizes IBM's AI API for intelligent responses.
- **Customization Options:** Includes adjustable max tokens, decoding methods, and repetition penalties.
- **Dark Mode Support:** Optional dark mode for better UI experience.
- **Download Chat History:** Save conversations as a text file.
- **Clear Chat:** Reset the chat session.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository/chat-with-images.git
   cd chat-with-images
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `secrets.toml` file inside the `.streamlit` folder and add your IBM API key:
   ```toml
   [secrets]
   IBM_API_KEY = "your_ibm_api_key"
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage
1. Open the Streamlit app in your browser.
2. Upload an image and/or enter text messages.
3. The AI assistant will process the input and generate responses.
4. Customize settings via the sidebar.
5. Download chat history if needed.

## Technologies Used
- **Python**
- **Streamlit**
- **IBM AI API**
- **PIL (Pillow)**
- **Base64 Encoding**
- **Requests Library**

## Future Improvements
- Support for multiple image uploads.
- Enhanced UI with more front-end features.
- Additional AI models for better image and text understanding.

## License
This project is licensed under the MIT License.
