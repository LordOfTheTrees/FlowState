import os
import openai
import base64
import requests
import time
import traceback
import json

class GenAI:
    """
    A simplified version of the GenAI class without dependencies on cv2 and other libraries.
    Added debugging capabilities to trace API calls.
    """
    def __init__(self, openai_api_key):
        """
        Initializes the GenAI class with the provided OpenAI API key.
        """
        print(f"Initializing GenAI with API key: {openai_api_key[:5]}...")
        self.openai_api_key = openai_api_key
        self.client = None
        try:
            self.client = openai.Client(api_key=openai_api_key)
            print("OpenAI client initialized successfully")
        except Exception as e:
            print(f"Error initializing OpenAI client: {str(e)}")
            traceback.print_exc()

    def generate_text(self, prompt, instructions='You are a helpful AI named Jarvis', model="gpt-4o-mini", output_type='text', temperature=1):
        """
        Generates a text completion using the OpenAI API.
        """
        debug_info = f"generate_text called with prompt: {prompt[:50]}...\n"
        debug_info += f"Model: {model}, Temp: {temperature}\n"
        
        try:
            if not self.client:
                self.client = openai.Client(api_key=self.openai_api_key)
                debug_info += "Created new OpenAI client\n"
            
            debug_info += "Calling OpenAI API...\n"
            print("Calling OpenAI API for text generation...")
            
            completion = self.client.chat.completions.create(
                model=model,
                temperature=temperature,
                response_format={"type": output_type},
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt}
                ]
            )
            
            response = completion.choices[0].message.content
            debug_info += f"Received response from API (length: {len(response)})\n"
            print(f"Received response from API (length: {len(response)})")
            
            response = response.replace("```html", "")
            response = response.replace("```", "")
            return f"{response}\n\n[Debug: {debug_info}]"
        
        except Exception as e:
            tb = traceback.format_exc()
            err_msg = f"Error generating text: {str(e)}\n{tb}\n{debug_info}"
            print(err_msg)
            return err_msg

    def generate_chat_response(self, chat_history, user_message, instructions, model="gpt-4o-mini", output_type='text'):
        """
        Generates a chatbot-like response based on the conversation history.
        """
        debug_info = f"generate_chat_response called with message: {user_message[:50]}...\n"
        debug_info += f"Chat history length: {len(chat_history)}\n"
        
        try:
            if not self.client:
                self.client = openai.Client(api_key=self.openai_api_key)
                debug_info += "Created new OpenAI client\n"
            
            # Add the latest user message to the chat history
            chat_history.append({"role": "user", "content": user_message})
            
            debug_info += "Calling OpenAI API...\n"
            print("Calling OpenAI API for chat response...")
            
            # Call the OpenAI API to get a response
            completion = self.client.chat.completions.create(
                model=model,
                response_format={"type": output_type},
                messages=[
                    {"role": "system", "content": instructions},  # Add system instructions
                    *chat_history  # Unpack the chat history to include all previous messages
                ]
            )
            
            # Extract the bot's response from the API completion
            bot_response = completion.choices[0].message.content
            debug_info += f"Received response from API (length: {len(bot_response)})\n"
            print(f"Received response from API (length: {len(bot_response)})")
            
            # Add the bot's response to the chat history
            chat_history.append({"role": "assistant", "content": bot_response})
            
            return bot_response
        
        except Exception as e:
            tb = traceback.format_exc()
            err_msg = f"Error generating chat response: {str(e)}\n{tb}\n{debug_info}"
            print(err_msg)
            return err_msg

    def encode_image(self, image_path):
        """
        Encodes an image file into a base64 string.
        """
        debug_info = f"encode_image called with path: {image_path}\n"
        
        try:
            print(f"Opening image file: {image_path}")
            with open(image_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                debug_info += f"Image encoded successfully (length: {len(encoded)})\n"
                print(f"Image encoded successfully (length: {len(encoded)})")
                return encoded
        except Exception as e:
            tb = traceback.format_exc()
            err_msg = f"Error encoding image: {str(e)}\n{tb}\n{debug_info}"
            print(err_msg)
            return None

    def generate_image_description(self, image_paths, instructions, model='gpt-4o-mini'):
        """
        Generates a description for one or more images using OpenAI's vision capabilities.
        """
        debug_info = f"generate_image_description called with instructions: {instructions[:50]}...\n"
        
        try:
            if isinstance(image_paths, str):
                image_paths = [image_paths]
                
            debug_info += f"Number of images: {len(image_paths)}\n"
            print(f"Processing {len(image_paths)} images")
            
            if not self.client:
                self.client = openai.Client(api_key=self.openai_api_key)
                debug_info += "Created new OpenAI client\n"
            
            image_urls = []
            for idx, image_path in enumerate(image_paths):
                print(f"Encoding image {idx+1}: {image_path}")
                encoded_image = self.encode_image(image_path)
                if encoded_image:
                    image_url = f"data:image/jpeg;base64,{encoded_image}"
                    image_urls.append(image_url)
                    debug_info += f"Image {idx+1} encoded successfully\n"
                else:
                    err_msg = f"Error encoding image {idx+1}: {image_path}"
                    debug_info += f"{err_msg}\n"
                    print(err_msg)
                    return f"Error: {err_msg}\n{debug_info}"
            
            # Prepare the message content with both text and images
            content = [{"type": "text", "text": instructions}]
            for url in image_urls:
                content.append({"type": "image_url", "image_url": {"url": url}})
            
            PROMPT_MESSAGES = [
                {
                    "role": "user",
                    "content": content
                }
            ]
            
            debug_info += f"Prepared prompt with {len(image_urls)} images\n"
            debug_info += "Calling OpenAI API...\n"
            print("Calling OpenAI API for image description...")
            
            params = {
                "model": model,
                "messages": PROMPT_MESSAGES,
                "max_tokens": 1000,
            }
            
            completion = self.client.chat.completions.create(**params)
            
            response = completion.choices[0].message.content
            debug_info += f"Received response from API (length: {len(response)})\n"
            print(f"Received response from API (length: {len(response)})")
            
            response = response.replace("```html", "")
            response = response.replace("```", "")
            return response
        
        except Exception as e:
            tb = traceback.format_exc()
            err_msg = f"Error generating image description: {str(e)}\n{tb}\n{debug_info}"
            print(err_msg)
            return err_msg

    def extract_frames(self, fname_video, max_samples=15):
        """
        Simplified version that returns empty data since cv2 is not available
        """
        print(f"extract_frames called for {fname_video} (simplified version without cv2)")
        return [], 0, 0

    def generate_video_description(self, fname_video, instructions, max_samples=15, model='gpt-4o-mini'):
        """
        Simplified version that returns a placeholder message since video processing requires cv2
        """
        print(f"generate_video_description called for {fname_video} (simplified version without cv2)")
        return f"Video analysis from {fname_video}: (Simplified version - cv2 not available)"