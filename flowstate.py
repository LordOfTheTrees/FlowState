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
        get_attributes,
        adversarial_game_plan,
        format_strategy_for_display,
        display_strategy_battle,
        get_image_base64,
        save_default_waiting_images,
        format_strategy_content,
        trim_video,
        get_video_duration,
        generate_video_thumbnail,     
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
    /* Force the full page background to have diagonal belt stripes */
    .stApp {
        background: repeating-linear-gradient(
            45deg,
            #ffffff 0px,  /* White belt */
            #ffffff 25px,
            #0052cc 25px, /* Blue belt - deeper royal blue */
            #0052cc 50px,
            #6200ee 50px, /* Purple belt - richer purple */
            #6200ee 75px,
            #8B4513 75px, /* Brown belt - improved more authentic brown */
            #8B4513 100px,
            #1a1a1a 100px, /* Black belt - improved darker black */
            #1a1a1a 125px,
            #ff0000 125px, /* Red belt - brighter red */
            #ff0000 150px
        ) !important;
        background-attachment: fixed !important;
    }
    
    /* Make main content area and widgets have semi-transparent backgrounds */
    .block-container, div.stButton, div.stTextInput, div.stTextArea, div.stSelectbox {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 5px;
        padding: 5px;
    }
    
    /* Apply to specific Streamlit components to ensure they're visible against the background */
    .stTextInput > div, .stTextArea > div, .stSelectbox > div {
        background-color: rgba(255, 255, 255, 0.95);
    }
    
    /* Ensure text remains readable */
    .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {
        text-shadow: 0px 0px 3px rgba(255, 255, 255, 0.8);
    }
    
    /* Create a container for the app content with some padding and opacity */
    .main .block-container {
        padding: 30px;
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Style the sidebar to match */
    .stSidebar .block-container {
        background-color: rgba(240, 240, 240, 0.9);
        padding: 20px;
    }
    
    /* Add a belt stripe to titles */
    h1, h2, h3 {
        position: relative;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    
    h1::after, h2::after, h3::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        height: 5px;
        width: 100%;
        background: linear-gradient(
            to right,
            #ffffff,   /* White belt */
            #0066cc,   /* Blue belt */
            #660099,   /* Purple belt */
            #993300,   /* Brown belt */
            #000000,   /* Black belt */
            #cc0000    /* Red belt */
        );
        border-radius: 2px;
    }
    
    /* The rest of your existing CSS styles */
    /* Base styles */
    .main {
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
    
    /* Highlight box for recommendations/strategies */
    .highlight {
        background-color: rgba(248, 248, 248, 0.9);
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        border-left: 5px solid #333;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Error styling */
    .error {
        color: red;
        font-weight: bold;
    }
    
    /* Section dividers */
    .section-divider {
        margin-top: 30px;
        margin-bottom: 20px;
        border-top: 1px solid #ddd;
    }
    
    /* Tab content padding */
    .tab-content {
        padding: 20px 0;
    }
    
    /* Jiu-Jitsu Belt Colors for Strategy Columns */
    /* White Belt (Initiator/Beginner) */
    .white-belt {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #dddddd;
        border-bottom: 3px solid #dddddd;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Blue Belt (Early Intermediate) - Updated color */
    .blue-belt {
        background-color: rgba(230, 242, 255, 0.9);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #0052cc;
        border-bottom: 3px solid #0052cc;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Purple Belt (Advanced Intermediate) - Updated color */
    .purple-belt {
        background-color: rgba(245, 230, 255, 0.9);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #6200ee;
        border-bottom: 3px solid #6200ee;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
            
    /* Brown Belt (Advanced) - Updated color */
    .brown-belt {
        background-color: rgba(255, 242, 230, 0.9);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #8B4513;
        border-bottom: 3px solid #8B4513;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Black Belt (Expert/Master) - Updated color */
    .black-belt {
        background-color: rgba(240, 240, 240, 0.9);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #1a1a1a;
        border-bottom: 3px solid #1a1a1a;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Red Belt (Grand Master) - Updated color */
    .red-belt {
        background-color: rgba(255, 230, 230, 0.9);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #ff0000;
        border-bottom: 3px solid #ff0000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Strategy Entry Styling */
    .strategy-entry {
        margin-bottom: 15px;
        padding: 10px;
        border-radius: 5px;
        background-color: rgba(255, 255, 255, 0.6);
    }
    
    /* Belt gradient for the column headers */
    .belt-header {
        background: linear-gradient(to right, #FFFFFF, #0066cc, #660099, #993300, #000000, #cc0000);
        color: white;
        padding: 10px;
        border-radius: 5px 5px 0 0;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
    }
    
    /* Strategy battle container */
    .strategy-battle {
        max-height: 600px;
        overflow-y: auto;
        padding: 15px;
        border: 1px solid #eee;
        border-radius: 8px;
        background-color: rgba(250, 250, 250, 0.8);
        margin-bottom: 20px;
    }
    
    /* Custom bullet points styled like belt stripes */
    ul.belt-bullets {
        list-style: none;
        padding-left: 5px;
    }
    
    ul.belt-bullets li {
        position: relative;
        padding-left: 20px;
        margin-bottom: 8px;
    }
    
    ul.belt-bullets li:before {
        content: "";
        position: absolute;
        left: 0;
        top: 8px;
        width: 12px;
        height: 3px;
        background-color: #333;
    }
    
    /* Button styling for the "But I thought of that..." buttons */
    .counter-button {
        width: 100%;
        background-color: rgba(248, 248, 248, 0.9) !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        padding: 8px 16px !important;
        text-align: center !important;
        text-decoration: none !important;
        display: inline-block !important;
        font-size: 14px !important;
        margin: 10px 0 !important;
        cursor: pointer !important;
        border-radius: 4px !important;
        transition: all 0.3s ease !important;
    }
    
    .counter-button:hover {
        background-color: rgba(224, 224, 224, 0.9) !important;
        border-color: #bbb !important;
    }
    
    /* Improve code block readability */
    pre {
        background-color: rgba(240, 240, 240, 0.95) !important;
        padding: 10px !important;
        border-radius: 5px !important;
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
if 'counter_flowchart' not in st.session_state:
    st.session_state.counter_flowchart = None
if 'current_video' not in st.session_state:
    st.session_state.current_video = None
if 'current_attributes' not in st.session_state:
    st.session_state.current_attributes = ""
if 'selected_master' not in st.session_state:
    st.session_state.selected_master = None
if 'flow_position' not in st.session_state:
    st.session_state.flow_position = None
if 'flow_ideas' not in st.session_state:
    st.session_state.flow_ideas = None
if 'current_master' not in st.session_state:
    st.session_state.current_master = None
if 'app_function' not in st.session_state:
    st.session_state.app_function = "Position Image Recommendations"

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

app_function_sidebar = st.sidebar.selectbox(
    "Choose a function",
    ["Position Image Recommendations", "Master Talk", "FLOW Chart Generator", "Video Match Analysis", "Anime OODA Analysis"],
    index=["Position Image Recommendations", "Master Talk", "FLOW Chart Generator", "Video Match Analysis", "Anime OODA Analysis"].index(st.session_state.app_function)
)

# Update session state when sidebar selection changes
if app_function_sidebar != st.session_state.app_function:
    st.session_state.app_function = app_function_sidebar
    st.rerun()

# Handle custom navigation links from session state
if st.session_state.flow_position == "FLOW Chart Generator":
    position_variable_default = st.session_state.flow_position
    ideas_default = st.session_state.flow_ideas
    # Reset after use
    st.session_state.flow_position = None
    st.session_state.flow_ideas = None
else:
    position_variable_default = ""
    ideas_default = ""

# Initialize OpenAI API key - In a real application, use better security practices
if 'OPENAI_API_KEY' not in os.environ:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    if openai_api_key:
        os.environ['OPENAI_API_KEY'] = openai_api_key
    else:
        st.sidebar.warning("Please enter your OpenAI API Key")

# Function: Position Image Recommendations
if st.session_state.app_function == "Position Image Recommendations":
    st.title("Position Image Recommendations")
    
    # Image upload
    uploaded_file = st.file_uploader("Upload an image of a jiu-jitsu position", 
                                type=['jpg', 'jpeg', 'png'],
                                key="position_image_uploader")
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
elif st.session_state.app_function == "Master Talk":
    st.title("Master Talk")
    
    # Load masters list
    masters = load_masters()
    
    # Use selected master from session state if available
    if st.session_state.selected_master in masters:
        default_index = masters.index(st.session_state.selected_master)
        st.session_state.selected_master = None  # Reset after use
    else:
        default_index = 0
    
    # Master selection dropdown
    master_info = st.selectbox("Select a Jiu-Jitsu Master", masters, index=default_index)
    
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
    
    if st.button("Send", key="send_chat") and next_comment:
        if 'OPENAI_API_KEY' in os.environ:
            genai = GenAI(os.environ.get("OPENAI_API_KEY"))
            instructions = f"You are the jiu-jitsu master {master_info}. Have a conversation to me as this master and provide me troubleshooting help on my jiu-jitsu based on your fundamental principles of jiujitsu and notable successes. Try to keep the analysis brief like a conversation."
            
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
            
            try:
                # Call the OpenAI API directly without using generate_chat_response
                if not genai.client:
                    import openai
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
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
    
    # Generate Adversarial Strategy section
    if len(st.session_state.current_chat) > 2:  # Check if there's a conversation to analyze
        st.markdown("### Generate Adversarial Strategy")
        st.markdown("Create a counter strategy to defeat the master's advice")
        
        # Extract the master's messages for analysis
        master_advice = "\n".join([msg["content"] for msg in st.session_state.current_chat 
                                  if msg["role"] == "assistant"])
        
        counter_ruleset = st.selectbox("Ruleset", ["IBJJF", "Unified MMA"], 
                                      key="text_counter_rules")
        
        if st.button("Generate Text Counter Strategy"):
            with st.spinner(f"Analyzing {master_info}'s advice and creating counter strategy..."):
                try:
                    # Call the adversarial_game_plan function with text input
                    counter_strategy = adversarial_game_plan(
                        master_advice,
                        ruleset=counter_ruleset,
                        position=""
                    )
                    
                    # Clean up the response if needed
                    if "DEBUG INFO:" in counter_strategy and "RESPONSE:" in counter_strategy:
                        counter_strategy = counter_strategy.split("RESPONSE:")[1].strip()
                    
                    # Display the counter strategy
                    st.markdown("### Counter Strategy")
                    st.markdown(f'<div class="highlight">{counter_strategy}</div>', 
                               unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Function: FLOW Chart Generator
elif st.session_state.app_function == "FLOW Chart Generator":
    st.title("FLOW Chart Generator")
    
    # User inputs
    position_variable = st.text_input("Starting Position", value=position_variable_default)
    rules = st.selectbox("Rules", ["Unified MMA", "IBJJF"])
    isMMA = rules == "Unified MMA"
    ideas = st.text_area("Ideas and Athlete Build", height=100, value=ideas_default)
    
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

    # Display the flow chart if it exists
    if st.session_state.current_flowchart:
        tab1, tab2 = st.tabs(["Main Flow Chart", "Counter Strategy"])
        
        with tab1:
            st.markdown("### Flow Chart")
            
            # Add debugging information in an expander
            with st.expander("Debug Flow Chart"):
                st.code(st.session_state.current_flowchart, language="mermaid")
                st.markdown("If the chart isn't displaying correctly, there might be a syntax issue with the Mermaid code.")
            
            chart_height = 800
            use_full_width = True
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
                
        # Counter Strategy Tab
        with tab2:
            st.markdown("### Adversarial Game Plan")
            st.markdown("Generate a counter strategy to defeat the current flow chart")
            
            # Input fields for the adversarial plan
            counter_rules = st.selectbox("Counter Rules", ["IBJJF", "Unified MMA"], key="counter_rules")
            counter_isMMA = counter_rules == "Unified MMA"
            
            counter_position = st.text_input("Starting Counter Position", 
                                        value = st.session_state.flow_position if st.session_state.flow_position else "",
                                        placeholder="e.g., Defensive Guard, Counter to Side Control")
            
            counter_attributes = st.text_area("Counter Athlete Attributes", 
                                         placeholder="Physical attributes of the counter athlete")
            
            counter_ideas = st.text_area("Counter Strategy Ideas", 
                                   placeholder="Specific concepts or techniques to include in the counter strategy")
            
            # Generate adversarial plan button
            if st.button("Generate Counter Strategy", key="gen_counter"):
                with st.spinner("Generating adversarial game plan..."):
                    try:
                        # Call the adversarial_game_plan function
                        counter_plan = adversarial_game_plan(
                            st.session_state.current_flowchart,
                            ruleset=counter_rules,
                            position=counter_position,
                            measurables=counter_attributes
                        )
                        
                        # Clean up the response if needed
                        if "DEBUG INFO:" in counter_plan and "RESPONSE:" in counter_plan:
                            counter_plan = counter_plan.split("RESPONSE:")[1].strip()
                        
                        # Update session state with the counter plan
                        st.session_state.counter_flowchart = counter_plan
                        
                        # Force a rerun to update the displayed chart
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            
            # Display the counter flow chart if it exists
            if 'counter_flowchart' in st.session_state and st.session_state.counter_flowchart:
                st.markdown("### Counter Strategy Flow Chart")
                
                # Add debugging information in an expander
                with st.expander("Debug Counter Flow Chart"):
                    st.code(st.session_state.counter_flowchart, language="mermaid")
                
                # Display the counter flow chart
                try:
                    # Render the counter chart with specified dimensions
                    render_mermaid(st.session_state.counter_flowchart, height=800)
                    
                    # Add download option
                    st.download_button(
                        label="💾 Download Counter Strategy",
                        data=st.session_state.counter_flowchart,
                        file_name="counter_strategy_flowchart.mmd",
                        mime="text/plain",
                    )
                except Exception as e:
                    st.error(f"Error rendering counter flow chart: {str(e)}")

# Replace the existing Video Match Analysis section with this enhanced version

# Function: Video Match Analysis
elif st.session_state.app_function == "Video Match Analysis":
    st.title("Video Match Analysis")
    
    # Video upload
    uploaded_file = st.file_uploader("Upload a video of a jiu-jitsu match", 
                               type=['mp4', 'mov', 'avi'],
                               key="video_match_uploader")
    
    if uploaded_file is not None:
        # Save the video temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name
        
        # Update session state
        st.session_state.current_video = video_path
        st.session_state.video_filename = uploaded_file.name
        
        # Get video duration for the slider
        video_duration = get_video_duration(video_path)
        if not video_duration:
            video_duration = 300.0  # Default to 5 minutes if duration can't be determined
        
        # Generate thumbnail
        thumbnail_path = video_path + ".jpg"
        thumbnail_generated = generate_video_thumbnail(video_path, thumbnail_path)
        
        # Display video details
        video_container = st.container()
        with video_container:
            # Create two columns - one for the video/thumbnail, one for trimming controls
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Display original video
                st.subheader("Original Video")
                st.video(video_path)
                
                if thumbnail_generated:
                    st.image(thumbnail_path, width=300, caption="Video Thumbnail")
            
            with col2:
                st.subheader("Trim Video")
                
                # Time selection sliders
                st.markdown("**Select portion to analyze:**")
                
                # Round up to nearest minute for max value display
                max_duration_minutes = int((video_duration + 59) // 60)
                
                # Initialize trim values in session state if not exist
                if 'trim_start' not in st.session_state:
                    st.session_state.trim_start = 0.0
                if 'trim_end' not in st.session_state:
                    st.session_state.trim_end = min(video_duration, 60.0)  # Default to first minute or full video
                
                # Format time as MM:SS for display
                def format_time(seconds):
                    minutes = int(seconds // 60)
                    secs = int(seconds % 60)
                    return f"{minutes:02d}:{secs:02d}"
                
                # Label with current time values
                st.markdown(f"**Current selection:** {format_time(st.session_state.trim_start)} to {format_time(st.session_state.trim_end)}")
                
                # Create sliders for selecting start and end times
                trim_start = st.slider(
                    "Start Time (seconds)", 
                    min_value=0.0, 
                    max_value=video_duration,
                    value=st.session_state.trim_start,
                    step=1.0,
                    format="%.1f s",
                    key="trim_start_slider"
                )
                
                trim_end = st.slider(
                    "End Time (seconds)", 
                    min_value=trim_start + 1.0,  # Ensure end time is after start time
                    max_value=video_duration,
                    value=max(trim_start + 1.0, st.session_state.trim_end),
                    step=1.0,
                    format="%.1f s",
                    key="trim_end_slider"
                )
                
                # Update session state
                st.session_state.trim_start = trim_start
                st.session_state.trim_end = trim_end
                
                # Display selected duration
                selected_duration = trim_end - trim_start
                st.info(f"Selected duration: {format_time(selected_duration)}")
                
                # Trim button
                if 'trimmed_video' not in st.session_state:
                    st.session_state.trimmed_video = None
                
                if st.button("Trim Video"):
                    with st.spinner("Trimming video..."):
                        # Create output path
                        trimmed_path = f"{video_path}_trimmed.mp4"
                        
                        # Call the trim function
                        success = trim_video(video_path, trimmed_path, trim_start, trim_end)
                        
                        if success:
                            st.session_state.trimmed_video = trimmed_path
                            st.success("Video trimmed successfully!")
                            st.rerun()  # Rerun to update UI
                        else:
                            st.error("Failed to trim video. Please check the logs for details.")
        
        # Display trimmed video if it exists
        if st.session_state.trimmed_video and os.path.exists(st.session_state.trimmed_video):
            st.subheader("Trimmed Video")
            st.video(st.session_state.trimmed_video)
            
            # Use this video for analysis
            analysis_video = st.session_state.trimmed_video
            st.success("Analysis will be performed on the trimmed video.")
        else:
            # Use original video for analysis
            analysis_video = video_path
            if 'trimmed_video' in st.session_state and st.session_state.trimmed_video:
                st.warning("Trimmed video not found. Analysis will be performed on the original video.")
                st.session_state.trimmed_video = None
        
        # Master selection for video analysis
        st.subheader("Analysis Configuration")
        masters = load_masters()
        selected_master = st.selectbox("Select a Jiu-Jitsu Master for analysis", masters, index=0)
        
        # Additional options
        col1, col2 = st.columns(2)
        with col1:
            max_frames = st.slider("Max frames to analyze", min_value=5, max_value=20, value=10, 
                                  help="Higher values provide more detailed analysis but may take longer")
        with col2:
            rules = st.selectbox("Ruleset", ["IBJJF (Sport Jiu-Jitsu)", "Unified MMA"])
            isMMA = "MMA" in rules
        
        # Custom perspective options
        st.markdown("### Analysis Focus")
        focus_options = ["Both competitors", "Top position fighter", "Bottom position fighter"]
        selected_focus = st.radio("Focus the analysis on:", focus_options, horizontal=True)
        
        # Map the selection to appropriate player_variable
        if selected_focus == focus_options[0]:
            player_variable = "both"
        elif selected_focus == focus_options[1]:
            player_variable = "top"
        else:
            player_variable = "bottom"
        
        # Additional context or specific points to focus on
        context = st.text_area("Additional context for analysis (techniques, positions, etc.)", 
                              placeholder="e.g., guard retention, submission defense, takedown entries...")
        
        # Find the "Analyze button" section in flowstate.py (around line ~1000)
# Replace the entire block with this improved version:

# Analyze button
if st.button("Analyze Video", key="analyze_video_button"):
    with st.spinner(f"Having Master {selected_master} analyze your video..."):
        try:
            # Initialize MovieAI
            if 'OPENAI_API_KEY' in os.environ:
                movie_ai = MovieAI(os.environ.get("OPENAI_API_KEY"))
                
                # Get either the trimmed video or the original for analysis
                analysis_video = None
                if st.session_state.trimmed_video and os.path.exists(st.session_state.trimmed_video):
                    analysis_video = st.session_state.trimmed_video
                    st.success("Analysis will be performed on the trimmed video.")
                else:
                    analysis_video = video_path
                    if 'trimmed_video' in st.session_state and st.session_state.trimmed_video:
                        st.warning("Trimmed video not available. Analysis will be performed on the original video.")
                    
                # Create a progress bar
                progress_bar = st.progress(0)
                st.info("Step 1/4: Extracting frames from video...")
                
                # Try to extract at least one frame for the athlete attributes
                base64Frames = []
                try:
                    base64Frames, nframes, fps = movie_ai.extract_frames(analysis_video, max_samples=1)
                    progress_bar.progress(25)
                except Exception as frame_err:
                    st.warning(f"Could not extract video frames, but continuing with analysis: {str(frame_err)}")
                
                # If we have frames, save one and try to get attributes
                if base64Frames:
                    st.info("Step 2/4: Analyzing athlete attributes...")
                    try:
                        # Save the frame as an image
                        image_data = base64.b64decode(base64Frames[0])
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as img_file:
                            img_file.write(image_data)
                            frame_path = img_file.name
                        
                        # Update session state
                        st.session_state.current_image = frame_path
                        
                        # Try to get attributes (catch exceptions to prevent stopping the analysis)
                        try:
                            attributes = get_attributes(frame_path, player_variable)
                            
                            # Clean up the response if needed
                            if "DEBUG INFO:" in attributes and "RESPONSE:" in attributes:
                                attributes = attributes.split("RESPONSE:")[1].strip()
                            
                            st.session_state.current_attributes = attributes
                        except Exception as attr_e:
                            st.warning(f"Could not analyze detailed attributes, using defaults: {str(attr_e)}")
                            st.session_state.current_attributes = "Experienced jiu-jitsu practitioner"
                    except Exception as img_e:
                        st.warning(f"Could not save extracted frame: {str(img_e)}")
                
                # Progress update
                progress_bar.progress(50)
                
                # Proceed with analysis regardless of whether we got frames or not
                st.info("Step 3/4: Creating analysis query...")
                
                # Build the analysis prompt for the video
                match_type = "MMA" if isMMA else "IBJJF sport jiu-jitsu"
                
                # Create a persona-specific prompt for the selected master
                master_prompt = f"You are {selected_master}, a renowned jiu-jitsu master. "
                master_prompt += f"Analyze this {match_type} match focusing on {player_variable}. "
                master_prompt += "Give specific, actionable feedback in your unique teaching style. "
                master_prompt += "Focus on technique details, strategic advice, and mistakes "
                
                if context:
                    master_prompt += f"Pay special attention to: {context}. "
                
                progress_bar.progress(75)
                st.info("Step 4/4: Generating analysis...")
                
                # IMPORTANT: This is the part that needs to always run
                # Make the call to OpenAI directly instead of using movie_ai.generate_video_description
                # This ensures we get a response even if video processing failed
                
                try:
                    # Try to use extracted frames if available
                    if base64Frames:
                        # Create a content array with the text prompt and frames
                        content = [{"type": "text", "text": master_prompt}]
                        
                        # Add up to 3 frames if we have them (to avoid token limits)
                        used_frames = base64Frames[:min(3, len(base64Frames))]
                        for frame in used_frames:
                            content.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{frame}"}
                            })
                        
                        # Use the OpenAI API
                        params = {
                            "model": "gpt-4o",
                            "messages": [{"role": "user", "content": content}],
                            "max_tokens": 1000
                        }
                        
                    else:
                        # No frames available, just use text prompt
                        alternate_prompt = master_prompt + "\n\n"
                        alternate_prompt += f"Note: I couldn't extract frames from the video for analysis, "
                        alternate_prompt += f"but please provide general advice for a {match_type} match "
                        alternate_prompt += f"focusing on {player_variable}. "
                        
                        if context:
                            alternate_prompt += f"Pay special attention to these aspects: {context}. "
                            
                        params = {
                            "model": "gpt-4o",
                            "messages": [{"role": "user", "content": alternate_prompt}],
                            "max_tokens": 1000
                        }
                    
                    # Make the API call
                    if 'OPENAI_API_KEY' in os.environ:
                        import openai
                        client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))
                        completion = client.chat.completions.create(**params)
                        analysis = completion.choices[0].message.content
                    else:
                        analysis = f"Error: OpenAI API Key not found. Master {selected_master} couldn't analyze the video."
                        
                except Exception as api_err:
                    st.error(f"Error calling OpenAI API: {str(api_err)}")
                    analysis = f"Master {selected_master} says: I apologize, but I encountered a technical issue while analyzing your video. Here are some general tips for {match_type} matches focusing on {player_variable} position:\n\n"
                    analysis += "1. Focus on maintaining proper posture and balance\n"
                    analysis += "2. Control key grips and points of contact\n"
                    analysis += "3. Always be aware of submission opportunities\n"
                    analysis += "4. Practice transitions between positions regularly"
                
                # Complete the progress bar
                progress_bar.progress(100)
                
                # Display analysis results
                st.markdown("## Master's Analysis")
                
                # Display video info
                video_info = "Original Video" if analysis_video == video_path else "Trimmed Video"
                if 'trim_start' in st.session_state and 'trim_end' in st.session_state and analysis_video != video_path:
                    start_time = format_time(st.session_state.trim_start)
                    end_time = format_time(st.session_state.trim_end)
                    video_info += f" ({start_time} - {end_time})"
                
                st.markdown(f"*Analysis based on: {video_info}*")
                
                # Format the analysis as coming from the selected master
                formatted_analysis = f"""
                ### Analysis by {selected_master}:
                
                {analysis}
                """
                
                st.markdown(formatted_analysis)
                        
            else:
                st.error("OpenAI API Key is required for video analysis")
                
        except Exception as e:
            st.error(f"An error occurred during video analysis. Try again with a shorter video or different format.")
            st.info("Technical details (for debugging):")
            with st.expander("View error details"):
                st.code(f"Error: {str(e)}")

# Updated Anime OODA Analysis section with larger waiting images that only appear after button press

elif st.session_state.app_function == "Anime OODA Analysis":
    st.title("Anime OODA Analysis")
    
    # Initialize conversation history if not exists
    if 'left_column_history' not in st.session_state:
        st.session_state.left_column_history = []
    if 'right_column_history' not in st.session_state:
        st.session_state.right_column_history = []
    
    # Track which side is waiting for a response
    if 'left_waiting' not in st.session_state:
        st.session_state.left_waiting = False
    if 'right_waiting' not in st.session_state:
        st.session_state.right_waiting = False
    
    # Initialize waiting images
    if 'waiting_images_initialized' not in st.session_state:
        save_default_waiting_images()
        st.session_state.waiting_images_initialized = True
    
    # User inputs for initial analysis
    position_variable = st.text_input("Enter the jiu-jitsu position")
    ruleset = st.selectbox("Ruleset", ["Unified MMA", "IBJJF"])
    isMMA = ruleset == "Unified MMA"
    keywords = st.text_area("Enter your strategy or initial ideas", height=100)
    st.session_state.current_attributes = st.text_input("Athlete relative build (AI content policies prevent auto-analyzing this)")
    
    # Process button for initial analysis
    if st.button("Generate Initial Strategy"):
        if not position_variable or not keywords:
            st.error("Please fill in all fields")
        else:
            with st.spinner("Analyzing position and generating initial strategy..."):
                try:
                    # Enhanced keywords with attributes
                    enhanced_keywords = keywords + " " + st.session_state.current_attributes
                    
                    # Generate initial strategy - simpler version that doesn't require an image
                    api_key = os.environ.get("OPENAI_API_KEY", "")
                    if not api_key:
                        st.error("OpenAI API Key not found in environment variables")
                        st.stop()
                    
                    genai = GenAI(api_key)
                    
                    # Create the prompt for the initial strategy
                    match_type = "MMA" if isMMA else "IBJJF jiu-jitsu"
                    prompt = f"Generate a detailed jiu-jitsu strategy for an athlete with the following attributes: {st.session_state.current_attributes}. "
                    prompt += f"The starting position is {position_variable} under {match_type} rules. "
                    prompt += f"Additional context: {keywords}. "
                    prompt += f"Format the response as a clear, concise strategy with 3-4 key points. no more than 6 bullets"
                    
                    # Generate the strategy
                    initial_strategy = genai.generate_text(prompt)
                    
                    # Clean up the response if needed
                    if "[Debug:" in initial_strategy:
                        initial_strategy = initial_strategy.split("[Debug:")[0].strip()
                    
                    # Display the initial strategy
                    st.markdown("### Initial Strategy")
                    st.markdown(f'<div class="highlight">{initial_strategy}</div>', unsafe_allow_html=True)
                    
                    # Add the strategy to the left column history
                    st.session_state.left_column_history.append({
                        "role": "initiator",
                        "content": initial_strategy,
                        "position": position_variable,
                        "ruleset": ruleset,
                        "athlete": st.session_state.current_attributes
                    })
                    
                    # Reset waiting states
                    st.session_state.left_waiting = False
                    st.session_state.right_waiting = False
                    
                    # Force a rerun to show the columns
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    # Display the strategy battle if we have an initial strategy
    if len(st.session_state.left_column_history) > 0:
        st.markdown("### Strategy Battle")
        
        # Create two columns for the headers
        header_col1, header_col2 = st.columns(2)
        
        with header_col1:
            st.markdown("#### Initiator Strategy")
        
        with header_col2:
            st.markdown("#### Defender Strategy")
        
        # Determine the maximum number of rows needed
        max_rows = max(len(st.session_state.left_column_history), len(st.session_state.right_column_history))
        
        # Add an extra row if waiting for a response on either side
        if st.session_state.left_waiting and len(st.session_state.left_column_history) == max_rows:
            max_rows += 1
        if st.session_state.right_waiting and len(st.session_state.right_column_history) == max_rows:
            max_rows += 1
        
        # Loop through each row and create boxes
        for i in range(max_rows):
            # Create color class based on row index (cycle through 5 colors)
            color_class = i % 5
            
            # Define background colors for different rows
            bg_colors = [
                "rgba(230, 242, 255, 0.7)",  # Light blue
                "rgba(248, 238, 255, 0.7)",  # Light purple
                "rgba(255, 242, 230, 0.7)",  # Light orange
                "rgba(230, 255, 242, 0.7)",  # Light green
                "rgba(255, 230, 230, 0.7)"   # Light red
            ]
            
            # Create columns for this row
            col1, col2 = st.columns(2)
            
            # Style for the boxes
            box_style = f"""
            <style>
            .strategy-box-{i} {{
                background-color: {bg_colors[color_class]};
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                min-height: 200px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }}
            .strategy-bullet {{
                list-style-type: disc;
                padding-left: 20px;
            }}
            .strategy-bullet li {{
                margin-bottom: 8px;
            }}
            .waiting-image {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 400px;
            }}
            .waiting-image img {{
                max-width: 90%;
                max-height: 400px;
                object-fit: contain;
            }}
            </style>
            """
            
            # Left column (Initiator)
            with col1:
                st.markdown(box_style, unsafe_allow_html=True)
                
                # Check if we have content for this row
                if i < len(st.session_state.left_column_history):
                    # Format the content properly
                    content = st.session_state.left_column_history[i]["content"]
                    
                    # Format bullet points if needed
                    formatted_content = format_strategy_content(content)
                    
                    st.markdown(f"<div class='strategy-box-{i}'>{formatted_content}</div>", unsafe_allow_html=True)
                # Show waiting image if we're on the next row after existing content and left_waiting is True
                elif i == len(st.session_state.left_column_history) and st.session_state.left_waiting:
                    # Display loading image
                    try:
                        hero_img_base64 = get_image_base64("hero_response.png")
                        if hero_img_base64:
                            hero_img_tag = f'<img src="data:image/png;base64,{hero_img_base64}" alt="Hero thinking...">'
                        else:
                            hero_img_tag = '<p style="text-align: center; font-size: 20px;">Hero thinking...</p>'
                    except:
                        hero_img_tag = '<p style="text-align: center; font-size: 20px;">Hero thinking...</p>'
                        
                    st.markdown(f"""
                    <div class='strategy-box-{i}'>
                        <div class='waiting-image'>{hero_img_tag}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Empty box for alignment
                    st.markdown(f"<div class='strategy-box-{i}'></div>", unsafe_allow_html=True)
            
            # Right column (Defender)
            with col2:
                # Check if we have content for this row
                if i < len(st.session_state.right_column_history):
                    # Format the content properly
                    content = st.session_state.right_column_history[i]["content"]
                    
                    # Format bullet points if needed
                    formatted_content = format_strategy_content(content)
                    
                    st.markdown(f"<div class='strategy-box-{i}'>{formatted_content}</div>", unsafe_allow_html=True)
                # Show waiting image if we're on the next row after existing content and right_waiting is True
                elif i == len(st.session_state.right_column_history) and st.session_state.right_waiting:
                    # Display loading image
                    try:
                        villain_img_base64 = get_image_base64("villain_response.png")
                        if villain_img_base64:
                            villain_img_tag = f'<img src="data:image/png;base64,{villain_img_base64}" alt="Villain thinking...">'
                        else:
                            villain_img_tag = '<p style="text-align: center; font-size: 20px;">Villain thinking...</p>'
                    except:
                        villain_img_tag = '<p style="text-align: center; font-size: 20px;">Villain thinking...</p>'
                        
                    st.markdown(f"""
                    <div class='strategy-box-{i}'>
                        <div class='waiting-image'>{villain_img_tag}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Empty box for alignment
                    st.markdown(f"<div class='strategy-box-{i}'></div>", unsafe_allow_html=True)
        
        # Add buttons for generating counter strategies
        button_col1, button_col2 = st.columns(2)
        
        # Left column button (Initiator)
        with button_col1:
            # Only show the button if there's a defender strategy to counter and not already waiting
            button_disabled = len(st.session_state.right_column_history) == 0 or st.session_state.left_waiting
            if st.button("But I thought of that...", key="left_counter", disabled=button_disabled):
                # Set waiting state immediately
                st.session_state.left_waiting = True
                st.rerun()  # Rerun to show the waiting image
        
        # Right column button (Defender)
        with button_col2:
            # Only enable if not already waiting
            button_disabled = st.session_state.right_waiting
            if st.button("But I thought of that...", key="right_counter", disabled=button_disabled):
                # Set waiting state immediately
                st.session_state.right_waiting = True
                st.rerun()  # Rerun to show the waiting image
        
        # Process the waiting states if needed
        if st.session_state.left_waiting:
            with st.spinner("Generating hero counter-strategy..."):
                try:
                    # Get the last move from the right column
                    last_right_move = st.session_state.right_column_history[-1]["content"]
                    
                    # Generate a counter using adversarial_game_plan
                    counter_plan = adversarial_game_plan(
                        last_right_move,
                        ruleset=ruleset,
                        position=position_variable,
                        measurables=st.session_state.current_attributes
                    )
                    
                    # Clean up the response if needed
                    if "DEBUG INFO:" in counter_plan and "RESPONSE:" in counter_plan:
                        counter_plan = counter_plan.split("RESPONSE:")[1].strip()
                    
                    # Format as bullet points
                    api_key = os.environ.get("OPENAI_API_KEY", "")
                    genai = GenAI(api_key)
                    
                    format_prompt = f"""
                    Format the following counter-strategy into 3 clear bullet points (using • bullet format).
                    Keep each bullet point concise and action-oriented.
                    Do not use asterisks (*) or dashes (-).
                    
                    Counter strategy to format:
                    {counter_plan}
                    """
                    
                    formatted_counter = genai.generate_text(format_prompt)
                    
                    if "[Debug:" in formatted_counter:
                        formatted_counter = formatted_counter.split("[Debug:")[0].strip()
                    
                    # Add to left column history
                    st.session_state.left_column_history.append({
                        "role": "initiator",
                        "content": formatted_counter,
                        "position": position_variable,
                        "ruleset": ruleset,
                        "athlete": st.session_state.current_attributes
                    })
                    
                    # Reset waiting state
                    st.session_state.left_waiting = False
                    
                    # Force a rerun to update the display
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    # Reset waiting state in case of error
                    st.session_state.left_waiting = False
        
        if st.session_state.right_waiting:
            with st.spinner("Generating villain counter-strategy..."):
                try:
                    # Get the last move from the left column
                    last_left_move = st.session_state.left_column_history[-1]["content"]
                    
                    # Generate a counter using adversarial_game_plan
                    counter_plan = adversarial_game_plan(
                        last_left_move,
                        ruleset=ruleset,
                        position=position_variable,
                        measurables="Opponent with similar build, but specialty in defensive techniques"
                    )
                    
                    # Clean up the response if needed
                    if "DEBUG INFO:" in counter_plan and "RESPONSE:" in counter_plan:
                        counter_plan = counter_plan.split("RESPONSE:")[1].strip()
                    
                    # Format as bullet points
                    api_key = os.environ.get("OPENAI_API_KEY", "")
                    genai = GenAI(api_key)
                    
                    format_prompt = f"""
                    Format the following counter-strategy into 3 clear bullet points (using • bullet format).
                    Keep each bullet point concise and action-oriented.
                    Do not use asterisks (*) or dashes (-).
                    
                    Counter strategy to format:
                    {counter_plan}
                    """
                    
                    formatted_counter = genai.generate_text(format_prompt)
                    
                    if "[Debug:" in formatted_counter:
                        formatted_counter = formatted_counter.split("[Debug:")[0].strip()
                    
                    # Add to right column history
                    st.session_state.right_column_history.append({
                        "role": "defender",
                        "content": formatted_counter,
                        "position": position_variable,
                        "ruleset": ruleset,
                        "athlete": "Opponent with similar build, but specialty in defensive techniques"
                    })
                    
                    # Reset waiting state
                    st.session_state.right_waiting = False
                    
                    # Force a rerun to update the display
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    # Reset waiting state in case of error
                    st.session_state.right_waiting = False
        
        # Add a reset button at the bottom
        if st.button("Reset Battle", key="reset_battle"):
            st.session_state.left_column_history = []
            st.session_state.right_column_history = []
            st.session_state.left_waiting = False
            st.session_state.right_waiting = False
            st.rerun()
# End of Anime OODA Analysis section