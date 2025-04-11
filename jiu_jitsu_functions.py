import os
import sys
import traceback

# Add current directory to path to help with imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import GenAI safely
try:
    from genai import GenAI
except ImportError as e:
    print(f"Error importing GenAI: {e}")
    # Create a simplified placeholder if genai is not available
    class GenAI:
        def __init__(self, api_key):
            self.api_key = api_key
            
        def generate_image_description(self, image, prompt):
            return f"Image analysis from {image} with prompt: {prompt}"
            
        def generate_text(self, prompt):
            return f"Generated text for prompt: {prompt}"
            
        def generate_chat_response(self, chat_history, user_message, prompt):
            return f"Response to: {user_message}"
            
        def generate_video_description(self, video, prompt):
            return f"Video analysis from {video} with prompt: {prompt}"

def generate_grappling_plan(image, player_variable, isMMA=True, keywords=""):
    """
    Analyzes a still frame from a grappling match and generates recommended next moves.
    
    Parameters:
    -----------
    image : str
        Path to the image file showing a grappling position
    player_variable : str
        Which player to analyze ('top', 'bottom', or 'both')
    isMMA : bool, optional
        Whether the match is MMA (True) or pure Jiu-jitsu (False)
    keywords : str, optional
        Additional keywords to focus the analysis
        
    Returns:
    --------
    str
        Recommendations for the next immediate steps
    """
    # Debug information
    debug_info = f"Function called with:\nimage: {image}\nplayer_variable: {player_variable}\nisMMA: {isMMA}\nkeywords: {keywords}\n"
    debug_info += f"API Key set in environment: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}\n"
    
    try:
        # Get GenAI instance with explicit error handling
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return "Error: OpenAI API Key not found in environment variables"
        
        debug_info += f"Creating GenAI instance with API key: {api_key[:5]}...\n"
        genai = GenAI(api_key)
        
        # Create the prompt for image analysis
        match_type = "MMA" if isMMA else "Jiu-jitsu"
        prompt = f"The image is a still frame from a grappling match. The match has {match_type} rules. "
        prompt += f"I want you to analyze: {player_variable}, and provide three options for the next immediate steps "
        prompt += f"towards grappling moves that would work best for them given their current position. "
        prompt += f"I want these steps to be listed in quick bullet format like ex: \"1) <<step>> : towards <<move>>, 2) ...\". "
        prompt += f"Base the recommendations on historical MMA and Jiu-jitsu match performance. "
        
        if keywords:
            prompt += f"I want you to also take special note of the following keywords for your image and recommendation analysis: {keywords}"
        
        debug_info += f"Created prompt: {prompt[:100]}...\n"
        
        # Check if image file exists
        if not os.path.exists(image):
            return f"Error: Image file not found at {image}"
        
        debug_info += f"Image file exists: {image}\n"
        
        # Generate image description with recommendations
        debug_info += "Calling generate_image_description...\n"
        response = genai.generate_image_description(image, prompt)
        debug_info += f"Response received from API: {response[:100]}...\n"
        
        # Return both debug info and response for debugging
        return f"DEBUG INFO:\n{debug_info}\n\nRESPONSE:\n{response}"
    
    except Exception as e:
        tb = traceback.format_exc()
        return f"Error generating recommendations:\n{debug_info}\n\nException: {str(e)}\n\nTraceback:\n{tb}"


def analyse_grappling_match(video, player_variable, isMMA=True, keywords="", start_time=None, end_time=None):
    """
    Analyzes a video of a grappling match and provides feedback and recommendations.
    """
    # Get GenAI instance (with error handling)
    try:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return "Error: OpenAI API Key not found in environment variables"
        
        genai = GenAI(api_key)
    except Exception as e:
        return f"Error initializing GenAI: {str(e)}"
    
    # Create the prompt for video analysis
    match_type = "MMA" if isMMA else "Jiu-jitsu"
    prompt = f"These images are frames from a grappling match. The match has {match_type} rules. "
    prompt += f"I want you to analyze: {player_variable}, and provide an analysis of what went right or wrong "
    prompt += f"during the match, along with some recommendations for the {player_variable} in their next match. "
    
    if keywords:
        prompt += f"I want you to also take special note of the following keywords for your analysis: {keywords}"
    
    # Generate video description with analysis
    try:
        response = genai.generate_video_description(video, prompt)
        return response
    except Exception as e:
        return f"Error analyzing grappling match: {str(e)}"


def generate_flow_chart(measurables, position_variable="both", isMMA=True, favorite_ideas=""):
    """
    Generates a Mermaid-based radial flow chart of jiu-jitsu moves.
    """
    # Debug information
    debug_info = f"Function called with:\nmeasurables: {measurables}\nposition_variable: {position_variable}\nisMMA: {isMMA}\nfavorite_ideas: {favorite_ideas}\n"
    debug_info += f"API Key set in environment: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}\n"
    
    try:
        # Get GenAI instance with explicit error handling
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return "Error: OpenAI API Key not found in environment variables"
        
        debug_info += f"Creating GenAI instance with API key: {api_key[:5]}...\n"
        genai = GenAI(api_key)
        
        # Create the prompt for flow chart generation
        match_type = "MMA" if isMMA else "Jiu-jitsu"
        prompt = f"I want you to generate a Mermaid based radial visual flow chart of jiu-jitsu moves that will have the greatest likelihood "
        prompt += f"of success for an athlete with the following measurables: {measurables}. "
        prompt += f"I want this chart to focus on {position_variable} under the {match_type} ruleset"
        
        if favorite_ideas:
            prompt += f", and take into account that the athlete has the following ideas: {favorite_ideas}"
        
        # Add specific instructions for the output format
        prompt += " of the athlete. Could you label the flow arrows in the diagram using a description of the primary movement required to get to that bubble. Only return the mermaid object, and not any shoulder text whatsoever"
        
        debug_info += f"Created prompt: {prompt[:100]}...\n"
        
        # Generate the mermaid object
        debug_info += "Calling generate_text...\n"
        mermaid_object = genai.generate_text(prompt)
        debug_info += f"Response received from API: {mermaid_object[:100]}...\n"
        
        # Return a sample flowchart if the response doesn't contain mermaid syntax
        if "graph" not in mermaid_object.lower():
            mermaid_object = """
            graph TD
                A[Side Control] -->|Apply pressure| B[Mount]
                A -->|Switch hips| C[North-South]
                A -->|Grab wrist| D[Kimura Grip]
                B -->|Isolate arm| E[Armbar]
                B -->|Control collar| F[Ezekiel Choke]
                C -->|Control neck| G[Darce Choke]
                D -->|Rotate| H[Back Take]
            """
            debug_info += "Generated default mermaid flowchart (API response didn't contain valid mermaid)\n"
        
        # Return both debug info and mermaid object during development
        return f"DEBUG INFO:\n{debug_info}\n\nMERMAID:\n{mermaid_object}"
    
    except Exception as e:
        tb = traceback.format_exc()
        return f"Error generating flow chart:\n{debug_info}\n\nException: {str(e)}\n\nTraceback:\n{tb}"


def gracie_talk(gracie_name, chat_history, user_message):
    """
    Simulates a conversation with a specified Gracie family member.
    """
    # Get GenAI instance (with error handling)
    try:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return "Error: OpenAI API Key not found in environment variables"
        
        genai = GenAI(api_key)
    except Exception as e:
        return f"Error initializing GenAI: {str(e)}"
    
    # Create the instructions for the chat
    prompt = f"You are the famous martial arts practitioner {gracie_name}. "
    prompt += f"I want you to have a conversation with the user based on that information, "
    prompt += f"and have the conversation focused around improving the user's grappling and self-defense. "
    
    # Generate chat response
    try:
        response = genai.generate_chat_response(chat_history, user_message, prompt)
        return response
    except Exception as e:
        return f"Error generating chat response: {str(e)}"
# Function to sanitize and prepare mermaid chart content
def sanitize_mermaid(flow_chart):
    """
    Sanitizes a mermaid chart string to ensure it only contains valid mermaid syntax.
    
    Parameters:
    -----------
    flow_chart : str
        The flow chart string that might contain debugging or other non-mermaid content
        
    Returns:
    --------
    str
        A clean mermaid chart string
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



def generate_mermaid(mermaid_object):
    """
    Cleans up a Mermaid object string for display.
    """
    # Clean up the mermaid object (remove markdown backticks if present)
    if "```mermaid" in mermaid_object:
        mermaid_object = mermaid_object.replace("```mermaid", "").replace("```", "").strip()
    
    return mermaid_object


def display_graph(flow_chart):
    """
    Displays a Mermaid flow chart as an HTML object.
    
    Parameters:
    -----------
    flow_chart : str
        The flow chart string to display
        
    Returns:
    --------
    str
        HTML content that renders the mermaid chart
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

# Function to render mermaid chart in Streamlit
def render_mermaid(chart):
    """
    Renders a mermaid chart in Streamlit using HTML component.
    
    Parameters:
    -----------
    chart : str
        The chart string to render
        
    Returns:
    --------
    html component
        Streamlit HTML component displaying the chart
    """
    from streamlit.components.v1 import html
    html_content = display_graph(chart)
    return html(html_content, height=600)


def next_move(flow_chart, move_text, measurables, isMMA=True, favorite_ideas=""):
    """
    Generates a new flow chart based on the selected move from an existing chart.
    """
    # Remove DEBUG INFO section if present
    if "DEBUG INFO:" in flow_chart and "MERMAID:" in flow_chart:
        parts = flow_chart.split("MERMAID:")
        if len(parts) > 1:
            flow_chart = parts[1].strip()
    
    # Parse the flow chart to find the next node
    lines = flow_chart.strip().split('\n')
    new_position = None
    
    for line in lines:
        if move_text in line and "-->" in line:
            parts = line.split("-->")
            if len(parts) >= 2:
                # Extract the target node (removing any labels)
                target = parts[1].strip()
                if "[" in target:
                    new_position = target.split("[")[0].strip()
                else:
                    new_position = target
                break
    
    # If no next node found, return the original chart
    if not new_position:
        return flow_chart
    
    # Generate a new flow chart with the found position as the center
    return generate_flow_chart(measurables, new_position, isMMA, favorite_ideas)


def get_attributes(image, player_variable):
    """
    Analyzes an image to estimate the physical attributes of an athlete.
    """
    # Debug information
    debug_info = f"Function called with:\nimage: {image}\nplayer_variable: {player_variable}\n"
    debug_info += f"API Key set in environment: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}\n"
    
    try:
        # Get GenAI instance with explicit error handling
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return "Error: OpenAI API Key not found in environment variables"
        
        debug_info += f"Creating GenAI instance with API key: {api_key[:5]}...\n"
        genai = GenAI(api_key)
        
        # Create the prompt for athlete measurement estimation
        prompt = f"Please analyze this grappling match image and provide an estimate of the {player_variable} athlete's "
        prompt += "height, weight, and build. Include details about their body type "
        prompt += "(such as endomorph, mesomorph, ectomorph), muscle mass distribution, limb length proportions, "
        prompt += "and any notable physical characteristics that might affect their performance in grappling."
        
        debug_info += f"Created prompt: {prompt[:100]}...\n"
        
        # Check if image file exists
        if not os.path.exists(image):
            return f"Error: Image file not found at {image}"
        
        debug_info += f"Image file exists: {image}\n"
        
        # Generate image description with physical measurements
        debug_info += "Calling generate_image_description...\n"
        response = genai.generate_image_description(image, prompt)
        debug_info += f"Response received from API: {response[:100]}...\n"
        
        # Return both debug info and response for debugging
        return f"DEBUG INFO:\n{debug_info}\n\nRESPONSE:\n{response}"
    
    except Exception as e:
        tb = traceback.format_exc()
        return f"Error analyzing attributes:\n{debug_info}\n\nException: {str(e)}\n\nTraceback:\n{tb}"