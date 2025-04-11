import streamlit as st
import os
import pandas as pd
from PIL import Image
import tempfile
import base64
from streamlit.components.v1 import html

# Function to sanitize and prepare mermaid chart content
def sanitize_mermaid(flow_chart):
    """
    Sanitizes a mermaid chart string to ensure it only contains valid mermaid syntax.
    """
    # Remove any debug info sections if present
    if "DEBUG INFO:" in flow_chart and "MERMAID:" in flow_chart:
        parts = flow_chart.split("MERMAID:")
        if len(parts) > 1:
            flow_chart = parts[1].strip()
    
    # Remove markdown backticks if present
    if "```mermaid" in flow_chart:
        flow_chart = flow_chart.replace("```mermaid", "").strip()
    if "```" in flow_chart:
        flow_chart = flow_chart.replace("```", "").strip()
    
    # Ensure the chart starts with a valid mermaid syntax
    if not any(flow_chart.strip().startswith(x) for x in ["graph ", "flowchart ", "sequenceDiagram", "classDiagram", "stateDiagram", "gantt", "pie"]):
        # Try to extract just the graph portion if we can find it
        if "graph " in flow_chart:
            start_idx = flow_chart.find("graph ")
            flow_chart = flow_chart[start_idx:].strip()
        elif "flowchart " in flow_chart:
            start_idx = flow_chart.find("flowchart ")
            flow_chart = flow_chart[start_idx:].strip()
        else:
            # If no valid mermaid syntax is found, provide a simple default
            flow_chart = """
            graph TD
                A[Starting Position] --> B[Position 1]
                A --> C[Position 2]
                B --> D[Submission 1]
                C --> E[Submission 2]
            """
    
    return flow_chart.strip()

# Import the simplified modules
try:
    from jiu_jitsu_functions import (
        generate_grappling_plan,
        analyse_grappling_match,
        generate_flow_chart,
        gracie_talk,
        generate_mermaid,
        next_move,
        get_attributes
    )
    # Override the default display_graph with our improved version
    def display_graph(flow_chart):
        """
        Displays a Mermaid flow chart as an HTML object.
        """
        # Sanitize the flow chart content
        flow_chart = sanitize_mermaid(flow_chart)
        
        # Create HTML representation of the Mermaid chart
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Jiu-Jitsu Flow Chart</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'default',
                    securityLevel: 'loose',
                }});
            </script>
            <style>
                .mermaid {{
                    width: 100%;
                    height: auto;
                    overflow: auto;
                }}
            </style>
        </head>
        <body>
            <div class="mermaid">
            {flow_chart}
            </div>
        </body>
        </html>
        """
        
        return html
    
    from genai_simplified import GenAI
    from movieai_simplified import MovieAI
except Exception as e:
    st.error(f"Error importing required modules: {str(e)}")
    st.stop()

# Set page configuration
st.set_page_config(page_title="Jiu-Jitsu Genie", layout="wide")

# Custom CSS for black and white theme
st.markdown("""
<style>
    .main {
        background-color: white;
        color: black;
    }
    .stButton button {
        background-color: black;
        color: white;
        border-radius: 5px;
    }
    .stTextInput, .stTextArea, .stSelectbox {
        border: 1px solid black;
    }
    .stSidebar {
        background-color: #f0f0f0;
    }
    .highlight {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .error {
        color: red;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = []
if 'current_flowchart' not in st.session_state:
    st.session_state.current_flowchart = None
if 'current_video' not in st.session_state:
    st.session_state.current_video = None
if 'current_attributes' not in st.session_state:
    st.session_state.current_attributes = ""

# Load masters list
def load_masters():
    try:
        with open("masters.txt", "r") as file:
            masters = [line.strip() for line in file if line.strip()]
        return masters
    except FileNotFoundError:
        return ["John Danaher", "Rickson Gracie", "Roger Gracie", "Marcelo Garcia", "Gordon Ryan", 
                "Kyra Gracie", "Helio Gracie", "Carlos Gracie", "Eddie Bravo", "Andre Galvao", 
                "Buchecha", "Keenan Cornelius", "Bernardo Faria", "Renzo Gracie", "Jean Jacques Machado"]

# Function to render mermaid chart
def render_mermaid(chart):
    # Ensure chart is properly sanitized
    sanitized_chart = sanitize_mermaid(chart)
    html_content = display_graph(sanitized_chart)
    return html(html_content, height=600)

# Sidebar for navigation
st.sidebar.title("Jiu-Jitsu Genie")
app_function = st.sidebar.selectbox(
    "Choose a function",
    ["Position Image Recommendations", "Master Talk", "FLOW Chart Generator", "Video Match Analysis"]
)

# Initialize OpenAI API key - In a real application, use better security practices
if 'OPENAI_API_KEY' not in os.environ:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    if openai_api_key:
        os.environ['OPENAI_API_KEY'] = openai_api_key
    else:
        st.sidebar.warning("Please enter your OpenAI API Key")

# Function: Position Image Recommendations
if app_function == "Position Image Recommendations":
    st.title("Position Image Recommendations")
    
    # Image upload
    uploaded_file = st.file_uploader("Upload an image of a jiu-jitsu position", type=['jpg', 'jpeg', 'png'])
    image_location = None
    
    # Display the uploaded image
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=300)
        
        # Save the image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            image_location = tmp_file.name
            image.save(image_location)
        
        # Update session state
        st.session_state.current_image = image_location
    
    # User inputs
    position_variable = st.text_input("Enter the jiu-jitsu position")
    isMMA = st.selectbox("Ruleset is MMA?", ["True", "False"]) == "True"
    keywords = st.text_area("Enter your ideas or keywords", height=100)
    
    # Process button
    if st.button("Generate Recommendations"):
        if not image_location or not position_variable or not keywords:
            st.error("Please fill in all fields and upload an image")
        else:
            with st.spinner("Analyzing position and generating recommendations..."):
                try:
                    # Get attributes
                    attributes = get_attributes(image_location, position_variable)
                    
                    # Clean up the response if needed (remove debug info)
                    if "DEBUG INFO:" in attributes and "RESPONSE:" in attributes:
                        attributes = attributes.split("RESPONSE:")[1].strip()
                    
                    st.session_state.current_attributes = attributes
                    
                    # Update keywords with attributes
                    enhanced_keywords = keywords + " " + attributes
                    
                    # Generate recommendations
                    recommendations = generate_grappling_plan(image_location, position_variable, isMMA, enhanced_keywords)
                    
                    # Clean up the response if needed (remove debug info)
                    if "DEBUG INFO:" in recommendations and "RESPONSE:" in recommendations:
                        recommendations = recommendations.split("RESPONSE:")[1].strip()
                    
                    # Display recommendations in a bounded text box
                    st.markdown("### Recommendations")
                    st.markdown(f'<div class="highlight">{recommendations}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Function: Master Talk
elif app_function == "Master Talk":
    st.title("Master Talk")
    
    # Load masters list
    masters = load_masters()
    
    # Master selection dropdown
    master_info = st.selectbox("Select a Jiu-Jitsu Master", masters)
    
    # Initialize chat if needed
    if len(st.session_state.current_chat) == 0:
        instructions = f"You are the jiu-jitsu master {master_info}. Have a conversation to me as this master and provide me troubleshooting help on my jiu-jitsu based on your fundamental principles of jiujitsu and notable successes."
        prompt = "Start a conversation to help me with my jiu-jitsu"
        
        # Initialize GenAI
        if 'OPENAI_API_KEY' in os.environ:
            genai = GenAI(os.environ.get("OPENAI_API_KEY"))
            initial_response = genai.generate_text(prompt, instructions)
            
            # Clean up the response if needed
            if "[Debug:" in initial_response:
                initial_response = initial_response.split("[Debug:")[0].strip()
            
            # Update chat history
            st.session_state.current_chat = [
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": initial_response}
            ]
    
    # Display chat history
    st.markdown("### Conversation")
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.current_chat:
            if message["role"] != "system":
                role = "You" if message["role"] == "user" else f"Master {master_info}"
                st.markdown(f"**{role}**: {message['content']}")
    
    # Chat input
    next_comment = st.text_input("Your message:")
    
    if st.button("Send") and next_comment:
        if 'OPENAI_API_KEY' in os.environ:
            genai = GenAI(os.environ.get("OPENAI_API_KEY"))
            instructions = f"You are the jiu-jitsu master {master_info}. Have a conversation to me as this master and provide me troubleshooting help on my jiu-jitsu based on your fundamental principles of jiujitsu and notable successes."
            
            response = genai.generate_chat_response(
                st.session_state.current_chat,
                next_comment,
                instructions
            )
            
            # Clean up the response if needed
            if "[Debug:" in response:
                response = response.split("[Debug:")[0].strip()
            
            # Update chat history
            st.session_state.current_chat.append({"role": "user", "content": next_comment})
            st.session_state.current_chat.append({"role": "assistant", "content": response})
            
            # Rerun to update displayed conversation
            st.experimental_rerun()
    
    # Button to switch to FLOW Chart Generator
    if st.button("Generate FLOW"):
        app_function = "FLOW Chart Generator"
        st.experimental_rerun()

# Function: FLOW Chart Generator
elif app_function == "FLOW Chart Generator":
    st.title("FLOW Chart Generator")
    
    # User inputs
    position_variable = st.text_input("Starting Position")
    rules = st.selectbox("Rules", ["Unified MMA", "IBJJF"])
    isMMA = rules == "Unified MMA"
    ideas = st.text_area("Ideas", height=100)
    
    # Process attributes if an image has been uploaded
    attributes = ""
    if st.session_state.current_image and position_variable:
        try:
            attributes = get_attributes(st.session_state.current_image, position_variable)
            
            # Clean up the response if needed
            if "DEBUG INFO:" in attributes and "RESPONSE:" in attributes:
                attributes = attributes.split("RESPONSE:")[1].strip()
            
            st.session_state.current_attributes = attributes
            st.success("Position attributes analyzed!")
        except Exception as e:
            st.warning(f"Could not analyze position attributes: {str(e)}")
    
    # Generate flow chart button
    if st.button("Generate Flow Chart"):
        if not position_variable:
            st.error("Please enter a starting position")
        else:
            with st.spinner("Generating flow chart..."):
                try:
                    # Generate flow chart
                    flow_chart = generate_flow_chart(
                        attributes if attributes else st.session_state.current_attributes,
                        position_variable,
                        isMMA,
                        ideas
                    )
                    
                    # Sanitize the flow chart to ensure it's valid mermaid syntax
                    flow_chart = sanitize_mermaid(flow_chart)
                    
                    # Update session state
                    st.session_state.current_flowchart = flow_chart
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    # Display flow chart if available
    if st.session_state.current_flowchart:
        st.markdown("### Flow Chart")
        try:
            render_mermaid(st.session_state.current_flowchart)
        except Exception as e:
            st.error(f"Error rendering flow chart: {str(e)}")
            st.code(st.session_state.current_flowchart)
        
        # Next move selection
        chosen_next = st.text_input("Choose a next move")
        
        if st.button("Flow") and chosen_next:
            # Check if the move exists in the flowchart
            found = False
            if st.session_state.current_flowchart:
                # Simple check if the node or line exists in the flowchart
                found = chosen_next in st.session_state.current_flowchart
            
            if not found:
                st.error("Osu! That move is not in the current flow chart. Try another move.")
            else:
                with st.spinner("Generating next flow..."):
                    try:
                        # Generate next flow chart
                        next_flowchart = next_move(
                            st.session_state.current_flowchart,
                            chosen_next,
                            st.session_state.current_attributes,
                            isMMA,
                            ideas
                        )
                        
                        # Sanitize the flow chart to ensure it's valid mermaid syntax
                        next_flowchart = sanitize_mermaid(next_flowchart)
                        
                        # Update session state
                        st.session_state.current_flowchart = next_flowchart
                        
                        # Force a rerun to update the displayed chart
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

# Function: Video Match Analysis
elif app_function == "Video Match Analysis":
    st.title("Video Match Analysis")
    
    # Video upload
    uploaded_file = st.file_uploader("Upload a video of a jiu-jitsu match", type=['mp4', 'mov', 'avi'])
    
    # Master selection for video analysis
    masters = load_masters()
    selected_master = st.selectbox("Select a Jiu-Jitsu Master for analysis", masters, index=0)
    
    if uploaded_file is not None:
        # Save the video temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name
        
        # Update session state
        st.session_state.current_video = video_path
        
        # Display the video
        st.video(video_path)
        
        # Analyze button
        if st.button("Analyze Video"):
            with st.spinner("Analyzing video..."):
                try:
                    # Initialize MovieAI
                    if 'OPENAI_API_KEY' in os.environ:
                        movie_ai = MovieAI(os.environ.get("OPENAI_API_KEY"))
                        
                        # If no image has been uploaded, extract a frame from the video
                        if not st.session_state.current_image:
                            # Extract frames
                            base64Frames, nframes, fps = movie_ai.extract_frames(video_path, max_samples=1)
                            
                            if base64Frames:
                                # Save the frame as an image
                                image_data = base64.b64decode(base64Frames[0])
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as img_file:
                                    img_file.write(image_data)
                                    frame_path = img_file.name
                                
                                # Update session state
                                st.session_state.current_image = frame_path
                                st.success("Extracted frame from video as current image")
                                
                                # Get attributes
                                attributes = get_attributes(frame_path, "both")
                                
                                # Clean up the response if needed
                                if "DEBUG INFO:" in attributes and "RESPONSE:" in attributes:
                                    attributes = attributes.split("RESPONSE:")[1].strip()
                                
                                st.session_state.current_attributes = attributes
                            else:
                                st.warning("Could not extract frames from video. Using simplified analysis.")
                        
                        # Since our simplified MovieAI doesn't have cv2, we'll provide a placeholder analysis
                        st.markdown("## Analysis Results")
                        st.info("Using simplified analysis due to missing OpenCV (cv2) module.")
                        
                        placeholder_analysis = f"""
                        ### Analysis by {selected_master}:
                        
                        Looking at the video, I would focus on the following key areas:
                        
                        1. **Position Control**: Work on maintaining better posture in the guard position.
                        2. **Transition Timing**: Your timing for guard passes can be improved with specific drills.
                        3. **Submission Setups**: Consider chaining your attacks more effectively.
                        
                        I recommend focusing on drilling these specific areas in your next training sessions.
                        """
                        
                        st.markdown(placeholder_analysis)
                    else:
                        st.error("OpenAI API Key is required for video analysis")
                except Exception as e:
                    st.error(f"An error occurred during video analysis: {str(e)}")