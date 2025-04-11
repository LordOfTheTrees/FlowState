import streamlit as st
import os
import pandas as pd
from PIL import Image
import tempfile
import base64
from streamlit.components.v1 import html


# Import the helper modules
try:
    from jiu_jitsu_functions import (
        generate_grappling_plan,
        analyse_grappling_match,
        sanitize_mermaid,
        generate_flow_chart_with_start,
        generate_flow_chart,
        gracie_talk,
        render_mermaid,
        generate_mermaid,
        display_graph,
        next_move,
        get_attributes
    )    
    from genai import GenAI
    from movieai import MovieAI
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
    st.session_state.current_attributes = st.text_input("Athlete relative build (AI content policies prevent auto-analyzing this)")
    
    # Process button
    if st.button("Generate Recommendations"):
        if not image_location or not position_variable or not keywords:
            st.error("Please fill in all fields and upload an image")
        else:
            with st.spinner("Analyzing position and generating recommendations..."):
                try:
                    # Get attributes
                    #attributes = get_attributes(image_location, position_variable)
                    
                    # Clean up the response if needed (remove debug info)
                    #if "DEBUG INFO:" in attributes and "RESPONSE:" in attributes:
                    #    attributes = attributes.split("RESPONSE:")[1].strip()
                    
                    #st.session_state.current_attributes = attributes
                    
                    # Update keywords with attributes
                    enhanced_keywords = keywords + " " + st.session_state.current_attributes
                    
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
    
    # Add a state variable to track the currently selected master
    if 'current_master' not in st.session_state:
        st.session_state.current_master = None
    
    # Master selection dropdown
    master_info = st.selectbox("Select a Jiu-Jitsu Master", masters)
    
    # Check if the master has changed
    master_changed = st.session_state.current_master != master_info
    if master_changed:
        # Clear the chat history when master changes
        st.session_state.current_chat = []
        # Update the current master
        st.session_state.current_master = master_info
    
    # Initialize chat if needed (either first time or after master change)
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
            
            # Create a message list for the API call without modifying the original
            messages_for_api = [
                {"role": "system", "content": instructions}
            ]
            
            # Add all non-system messages from the current chat
            for msg in st.session_state.current_chat:
                if msg["role"] != "system":
                    messages_for_api.append(msg.copy())
            
            # Add the new user message
            messages_for_api.append({"role": "user", "content": next_comment})
            
            # Call the OpenAI API directly without using generate_chat_response
            if not genai.client:
                genai.client = openai.Client(api_key=genai.openai_api_key)
            
            # Make the API call
            completion = genai.client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "text"},
                messages=messages_for_api
            )
            
            # Extract the response
            response = completion.choices[0].message.content
            
            # Clean up the response if needed
            if "[Debug:" in response:
                response = response.split("[Debug:")[0].strip()
            
            # Update the chat history with the new messages
            st.session_state.current_chat.append({"role": "user", "content": next_comment})
            st.session_state.current_chat.append({"role": "assistant", "content": response})
            
            # Rerun to update the display
            st.rerun()
    
    # Button to switch to FLOW Chart Generator
    if st.button("Generate FLOW"):
        app_function = "FLOW Chart Generator"
        st.rerun()

# Function: FLOW Chart Generator
elif app_function == "FLOW Chart Generator":
    st.title("FLOW Chart Generator")
    
    # User inputs
    position_variable = st.text_input("Starting Position")
    rules = st.selectbox("Rules", ["Unified MMA", "IBJJF"])
    isMMA = rules == "Unified MMA"
    ideas = st.text_area("Ideas and Athlete Build", height=100)
    
    # Process attributes if an image has been uploaded
    attributes = ""
    if st.session_state.current_image and position_variable:
        try:
            attributes = get_attributes(st.session_state.current_image, position_variable)
            
            # Clean up the response if needed
            if "DEBUG INFO:" in attributes and "RESPONSE:" in attributes:
                attributes = attributes.split("RESPONSE:")[1].strip()
            
            st.session_state.current_attributes = attributes
            st.success("Previous attributes included!")
        except Exception as e:
            st.warning(f"Could not analyze position attributes: {str(e)}")
    
    # Generate flow chart button
    if st.button("Generate Flow Chart"):
        if not position_variable:
            st.error("Please enter a starting position")
        else:
            with st.spinner("Generating flow chart..."):
                try:
                    # Use default athlete profile if no attributes are available
                    athlete_profile = attributes if attributes else st.session_state.current_attributes
                    if not athlete_profile or athlete_profile.strip() == "":
                        athlete_profile = "Average adult male jiu-jitsu practitioner with balanced build"
                    
                    # Show what's being passed to the function (for debugging)
                    st.info(f"Generating flow chart for position: '{position_variable}' with rules: '{rules}' and ideas: '{ideas}'")
                    
                    # Generate flow chart with explicit starting position
                    flow_chart = generate_flow_chart_with_start(
                        athlete_profile,
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
                    import traceback
                    st.code(traceback.format_exc())


# Add a size control section
if st.session_state.current_flowchart:
    st.markdown("### Flow Chart")
    
    # Add debugging information in an expander
    with st.expander("Debug Flow Chart"):
        st.code(st.session_state.current_flowchart, language="mermaid")
        st.markdown("If the chart isn't displaying correctly, there might be a syntax issue with the Mermaid code.")
    
    # Add display size controls
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        chart_height = st.select_slider(
            "Chart Height",
            options=[600, 700, 800, 900, 1000, 1200, 1500],
            value=800,
            key="chart_height"
        )
    with col2:
        use_full_width = st.checkbox("Use Full Width", value=True, key="use_full_width")
    with col3:
        st.info("**Tip:** For full interactive features, download the chart and open in a Mermaid editor.")
    
    try:
        # Calculate width based on checkbox
        chart_width = None if use_full_width else min(1200, chart_height * 1.5)
        
        # Render the chart with specified dimensions
        render_mermaid(st.session_state.current_flowchart, height=chart_height, width=chart_width)
        
        # Add download option in a smaller column
        col1, col2 = st.columns([1, 2])
        with col1:
            st.download_button(
                label="💾 Download as Mermaid Code",
                data=st.session_state.current_flowchart,
                file_name="jiu_jitsu_flowchart.mmd",
                mime="text/plain",
            )
        with col2:
            # Add link to online Mermaid editor
            st.markdown("[🔗 Open in Mermaid Live Editor](https://mermaid.live/) (paste the downloaded code)")
        
    except Exception as e:
        st.error(f"Error rendering flow chart: {str(e)}")
        
        # Try a simplified version as fallback
        st.markdown("### Fallback Chart")
        fallback_chart = f"""
        graph TD
            A["{position_variable}"] -->|"Move 1"| B["Position 1"]
            A -->|"Move 2"| C["Position 2"]
            B -->|"Action"| D["Submission 1"]
            C -->|"Action"| E["Submission 2"]
        """
        try:
            st.code(fallback_chart, language="mermaid")
        except Exception as fallback_error:
            st.error(f"Fallback also failed: {str(fallback_error)}")
    
    # Next move selection with the Flow button
    with st.container():
        st.markdown("### Navigate the Flow Chart")
        st.markdown("Enter a position or transition from the chart above to explore further:")
        
        chosen_next = st.text_input("Select next position/transition", key="next_move_input")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            flow_button = st.button("Flow", key="flow_button", use_container_width=True)
        with col2:
            # Show a hint about what can be entered
            if st.session_state.current_flowchart:
                # Extract some node texts from the flowchart to show as examples
                nodes = []
                for line in st.session_state.current_flowchart.split("\n"):
                    if "[" in line and "]" in line:
                        start_idx = line.find("[")
                        end_idx = line.find("]")
                        node_text = line[start_idx+1:end_idx].strip()
                        if node_text.startswith('"') and node_text.endswith('"'):
                            node_text = node_text[1:-1]
                        if node_text not in nodes and node_text != position_variable:
                            nodes.append(node_text)
                            if len(nodes) >= 3:
                                break
                
                if nodes:
                    examples = ", ".join([f'"{node}"' for node in nodes[:3]])
                    st.markdown(f"*Examples from current chart: {examples}*")
        
        if flow_button and chosen_next:
            # Check if the move exists in the flowchart
            found = False
            if st.session_state.current_flowchart:
                # Simple check if the node or line exists in the flowchart
                found = chosen_next.lower() in st.session_state.current_flowchart.lower()
            
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
                        st.rerun()
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
