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



def generate_flow_chart_with_start(measurables, starting_position, isMMA=True, favorite_ideas=""):
    """
    Generates a detailed Mermaid-based flow chart of jiu-jitsu moves with complex branching
    starting from a specific position.
    
    Parameters:
    -----------
    measurables : str
        Physical attributes and characteristics of the athlete
    starting_position : str
        The specific jiu-jitsu position to start the flow chart from
    isMMA : bool, optional
        Whether to use MMA rules (True) or IBJJF rules (False)
    favorite_ideas : str, optional
        Additional ideas or preferences to consider
        
    Returns:
    --------
    str
        A detailed mermaid flow chart as a string
    """
    # Debug information
    debug_info = f"Function called with:\nmeasurables: {measurables}\nstarting_position: {starting_position}\nisMMA: {isMMA}\nfavorite_ideas: {favorite_ideas}\n"
    
    try:
        # Get GenAI instance with explicit error handling
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return "Error: OpenAI API Key not found in environment variables"
        
        genai = GenAI(api_key)
        
        # Create the prompt for flow chart generation
        match_type = "MMA" if isMMA else "IBJJF jiu-jitsu"
        
        # Simplified prompt that avoids providing a template example
        prompt = f"""Generate a detailed Mermaid flow chart for jiu-jitsu techniques starting from {starting_position}.

REQUIREMENTS:
1. Use "graph LR" for the layout
2. Node A must be: "{starting_position}"
3. Create at least 4-5 realistic transitions from the starting position
4. Each transition should have 2-3 follow-up moves
5. Include specific technical details for each transition
6. Use {match_type} rules
7. Do not use placeholder names like "Position 1" - use real jiu-jitsu positions and techniques
8. Wrap all node text and arrow labels in double quotes
9. ONLY return the Mermaid diagram code with no explanations
10. Maximum of 16-20 nodes total (use the full complexity allowed)

The athlete has these attributes: {measurables}

The flow chart should have the following structure:
- Position A (center/starting position) should branch out to 3-6 distinct intermediate positions before ending up at a main move or position
- Each intermediate position should have 2-3 follow-up options, including submissions that end the chart
- Include at least one detailed chain of 3-4 connected techniques
- Include at least one reaction-based branch (if opponent does X, do Y)
- Include specific grips and technical details in the transition labels, making sure that all setps are listed before reaching the main move or position

Example enhanced format, DO NOT USE THESE, JUST USE AS A REFERENCE:
```
graph LR
    A["{starting_position}"] -->|"Grip right lapel w/ left hand"| B["Deep half-guard control"]
    A -->|"Shift weight to right hip, grip ankle"| C["Single Leg X-guard entry"]
    A -->|"2-on-1 control of left arm"| D["Kimura trap position"]
    A -->|"Knee slice w/ lapel control"| E["Side control, nearside underhook"]
    
    B -->|"Drive head to outside hip"| F["Outside single leg sweep"]
    B -->|"Block far hip and bridge"| G["Sweep to top half-guard"]
    
    C -->|"Extend legs, control ankle"| H["Ankle lock position"]
    C -->|"Off-balance forward, control sleeve"| I["Technical stand-up to single leg"]
    
    D -->|"Rotate to back exposure"| J["Back take with seat belt grip"]
    D -->|"Step over head"| K["Far side armbar setup"]
    D -->|"Pull arm to hip, control wrist"| L["Top crucifix position"]
    
    E -->|"Drive shoulder to jaw"| M["Modified kata-gatame setup"]
    E -->|"Walk knees toward head, control far arm"| N["North-south kimura grip"]
    
    F -->|"Complete takedown, pass guard"| O["Knee slice pass sequence"]
    
    J -->|"Control with hooks in"| P["Back mount with harness grip"]
```

"""
        
        if favorite_ideas:
            prompt += f"\nIncorporate these techniques: {favorite_ideas}"
            
        if isMMA:
            prompt += "\nInclude at least one striking setup and one cage wrestling technique."
        else:
            prompt += "\nInclude only IBJJF-legal techniques with point-scoring positions."
            
        # Generate the mermaid object
        mermaid_object = genai.generate_text(prompt)
        
        # Clean up the response
        if "[Debug:" in mermaid_object:
            mermaid_object = mermaid_object.split("[Debug:")[0].strip()
        
        # Extract just the code if wrapped in backticks
        if "```" in mermaid_object:
            code_parts = mermaid_object.split("```")
            for part in code_parts:
                if "graph" in part:
                    mermaid_object = part.strip()
                    break
        
        # Check if the starting position is in the chart
        if starting_position not in mermaid_object:
            return f"Error: Generated flowchart doesn't contain the starting position: '{starting_position}'"
            
        # Check if it contains generic placeholders
        placeholders = ["Position 1", "Position 2", "Submission 1", "Submission 2", "Default Graph"]
        for term in placeholders:
            if term in mermaid_object:
                return f"Error: Generated flowchart contains generic placeholder: '{term}'"
        
        # Return the flowchart
        return f"DEBUG INFO:\n{debug_info}\n\nMERMAID:\n{mermaid_object}"
    
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return f"Error generating flow chart: {str(e)}"

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
        prompt += '''. Make the flow chart circular, with the choices radiating out from the center. 
        I want to each bubble to be focused on an intermediate stage on the way to a larger move that is a couple bubbles away.
        Label the flow arrows in the diagram using a description of the primary movement required to get to that intermediate step.
        I want the descriptions to be 3-4 words each, and provide clear consise directions on exactly to get to the next intermediate step. 
        Only return the circular mermaid object, and not any shoulder text whatsoever"        
        '''
        debug_info += f"Created prompt: {prompt[:100]}...\n"
        
        # Generate the mermaid object
        debug_info += "Calling generate_text...\n"
        mermaid_object = genai.generate_text(prompt)
        debug_info += f"Response received from API: {mermaid_object[:100]}...\n"
        
        # Return a sample flowchart if the response doesn't contain mermaid syntax
        if "graph" not in mermaid_object.lower():
            mermaid_object = """
            graph TD
                A[Default Graph - Side Control] -->|Apply pressure| B[Mount]
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
    """
    # Remove any debug info sections if present
    if "DEBUG INFO:" in flow_chart and "MERMAID:" in flow_chart:
        parts = flow_chart.split("MERMAID:")
        if len(parts) > 1:
            flow_chart = parts[1].strip()
    
    # Remove any debug info at the end (common with API responses)
    if "[Debug:" in flow_chart:
        flow_chart = flow_chart.split("[Debug:")[0].strip()
    
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
                A["Starting Position"] --> B["Position 1"]
                A --> C["Position 2"]
                B --> D["Submission 1"]
                C --> E["Submission 2"]
            """
    
    # Process each line of the flow chart
    lines = flow_chart.strip().split('\n')
    clean_lines = []
    
    # First line should be the graph declaration
    if lines and (lines[0].strip().startswith('graph ') or lines[0].strip().startswith('flowchart ')):
        clean_lines.append(lines[0].strip())
    else:
        # Add a default graph declaration if none exists
        clean_lines.append("graph TD")
    
    # Process node definitions and connections
    for line in lines[1:]:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip multiple graph declarations
        if line.startswith('graph ') or line.startswith('flowchart '):
            continue
        
        # Add proper indentation
        if not line.startswith('    '):
            line = '    ' + line
        
        # Quote node texts
        new_line = line
        
        # Fix node labels - find text inside square brackets and add quotes
        bracket_start = 0
        while '[' in new_line[bracket_start:]:
            bracket_start = new_line.find('[', bracket_start)
            if bracket_start == -1:
                break
                
            bracket_end = new_line.find(']', bracket_start)
            if bracket_end == -1:
                break
                
            # Extract and quote the label
            label = new_line[bracket_start+1:bracket_end]
            if not (label.startswith('"') and label.endswith('"')):
                quoted_label = f'"{label}"'
                new_line = new_line[:bracket_start+1] + quoted_label + new_line[bracket_end:]
                # Update bracket_end to account for added quotes
                bracket_end += 2
                
            bracket_start = bracket_end + 1
        
        # Fix arrow labels - find text inside arrow pipes and add quotes
        arrow_start = 0
        while '-->|' in new_line[arrow_start:]:
            arrow_start = new_line.find('-->|', arrow_start)
            if arrow_start == -1:
                break
                
            pipe_start = arrow_start + 4  # Skip past '-->|'
            pipe_end = new_line.find('|', pipe_start)
            if pipe_end == -1:
                break
                
            # Extract and quote the label
            label = new_line[pipe_start:pipe_end]
            if not (label.startswith('"') and label.endswith('"')):
                quoted_label = f'"{label}"'
                new_line = new_line[:pipe_start] + quoted_label + new_line[pipe_end:]
                # Update pipe_end to account for added quotes
                pipe_end += 2
                
            arrow_start = pipe_end + 1
        
        clean_lines.append(new_line)
    
    # Join the lines back together
    fixed_chart = '\n'.join(clean_lines)
    
    # Fix any other obvious formatting issues
    fixed_chart = fixed_chart.replace("[ ", "[")
    fixed_chart = fixed_chart.replace(" ]", "]")
    fixed_chart = fixed_chart.replace("-->| ", "-->|")
    fixed_chart = fixed_chart.replace(" |", "|")
    
    return fixed_chart

def generate_mermaid(mermaid_object):
    """
    Cleans up a Mermaid object string for display.
    """
    # Clean up the mermaid object (remove markdown backticks if present)
    if "```mermaid" in mermaid_object:
        mermaid_object = mermaid_object.replace("```mermaid", "").replace("```", "").strip()
    
    return mermaid_object


    """
    Displays a complex Mermaid flow chart as an HTML object with enhanced styling
    to better handle intricate jiu-jitsu technique branching.
    
    Parameters:
    -----------
    flow_chart : str
        The flow chart string to display
        
    Returns:
    --------
    str
        Enhanced HTML content that renders the mermaid chart
    """
    # Sanitize the flow chart content
    flow_chart = sanitize_mermaid(flow_chart)
    
    # Create HTML representation of the Mermaid chart with enhanced options
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jiu-Jitsu Flow Chart</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis',
                    diagramPadding: 10,
                    nodeSpacing: 80,
                    rankSpacing: 120,
                    layoutEngine: 'dagre'
                }},
                sequence: {{
                    diagramMarginX: 50,
                    diagramMarginY: 20,
                    actorMargin: 50,
                    width: 200,
                    height: 50
                }}
            }});
            
            document.addEventListener('DOMContentLoaded', function() {{
                try {{
                    mermaid.init(undefined, document.querySelector('.mermaid'));
                    console.log('Chart initialized successfully');
                    
                    // Apply styling after rendering
                    setTimeout(function() {{
                        // Find and style nodes
                        const nodes = document.querySelectorAll('.node');
                        const centralNode = document.querySelector('.node:nth-child(1)'); // Try to find central node
                        const edgePaths = document.querySelectorAll('.edgePath');
                        
                        // Style all nodes
                        nodes.forEach(node => {{
                            // Add hover effects
                            node.classList.add('node-interactive');
                            
                            // Check if this node contains a submission technique
                            const nodeText = node.textContent.toLowerCase();
                            if (nodeText.includes('submission') || 
                                nodeText.includes('choke') || 
                                nodeText.includes('lock') || 
                                nodeText.includes('triangle') || 
                                nodeText.includes('bar') ||
                                nodeText.includes('kimura') ||
                                nodeText.includes('guillotine')) {{
                                node.classList.add('submission-node');
                            }}
                            // Check if this node contains a sweep or transition
                            else if (nodeText.includes('sweep') || 
                                    nodeText.includes('transition') || 
                                    nodeText.includes('pass') ||
                                    nodeText.includes('entry')) {{
                                node.classList.add('transition-node');
                            }}
                            // Check if this node contains a position
                            else if (nodeText.includes('guard') || 
                                    nodeText.includes('mount') || 
                                    nodeText.includes('control') ||
                                    nodeText.includes('position')) {{
                                node.classList.add('position-node');
                            }}
                        }});
                        
                        // Style central node specially if found
                        if (centralNode) {{
                            centralNode.classList.add('central-node');
                        }}
                        
                        // Style the edge paths
                        edgePaths.forEach(edge => {{
                            edge.classList.add('edge-interactive');
                        }});
                        
                    }}, 1000);
                }} catch (e) {{
                    console.error('Mermaid error:', e);
                    document.querySelector('.error-message').textContent = 'Error rendering chart: ' + e.message;
                    document.querySelector('.error-message').style.display = 'block';
                }}
            }});
        </script>
        <style>
            .chart-container {{
                width: 100%;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: auto;
            }}
            .mermaid {{
                width: 100%;
                height: auto;
                overflow: auto;
                padding: 20px;
            }}
            .error-message {{
                color: red;
                font-weight: bold;
                display: none;
                margin: 10px;
                padding: 10px;
                border: 1px solid red;
                background-color: #ffeeee;
            }}
            /* Enhanced styling for jiu-jitsu flow chart */
            .node-interactive {{
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            .node-interactive:hover {{
                filter: brightness(1.1);
                transform: scale(1.05);
            }}
            .central-node rect {{
                fill: #e6f7ff !important;
                stroke: #0099ff !important;
                stroke-width: 3px !important;
                filter: drop-shadow(0px 0px 5px rgba(0, 153, 255, 0.5));
            }}
            .submission-node rect {{
                fill: #ffe6e6 !important;
                stroke: #ff6666 !important;
                stroke-width: 2px !important;
            }}
            .transition-node rect {{
                fill: #fff2e6 !important;
                stroke: #ff9933 !important;
                stroke-width: 2px !important;
            }}
            .position-node rect {{
                fill: #e6fff2 !important;
                stroke: #33cc99 !important;
                stroke-width: 2px !important;
            }}
            .node rect {{
                rx: 10;
                ry: 10;
                filter: drop-shadow(0px 2px 3px rgba(0, 0, 0, 0.2));
            }}
            .edgePath path {{
                stroke-width: 2px;
                transition: all 0.3s ease;
            }}
            .edge-interactive:hover path {{
                stroke-width: 3px;
                filter: drop-shadow(0px 0px 3px rgba(0, 0, 0, 0.3));
            }}
            /* Make technique text more readable */
            .edgeLabel {{
                background-color: rgba(255, 255, 255, 0.8) !important;
                padding: 3px !important;
                border-radius: 4px !important;
                font-weight: bold !important;
                filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.1));
                max-width: 150px !important;
                overflow-wrap: break-word !important;
            }}
        </style>
    </head>
    <body>
        <div class="chart-container">
            <div class="error-message"></div>
            <div class="mermaid">
{flow_chart}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def display_graph(flow_chart):
    """
    Displays a complex Mermaid flow chart as an HTML object with enhanced styling
    and interactive controls for zooming, panning, and fullscreen functionality.
    
    Parameters:
    -----------
    flow_chart : str
        The flow chart string to display
        
    Returns:
    --------
    str
        Enhanced HTML content that renders the mermaid chart
    """
    # Sanitize the flow chart content
    flow_chart = sanitize_mermaid(flow_chart)
    
    # Create HTML representation of the Mermaid chart with enhanced options
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jiu-Jitsu Flow Chart</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose',
                flowchart: {{
                    useMaxWidth: false,  // Allow the chart to expand beyond container
                    htmlLabels: true,
                    curve: 'basis',
                    diagramPadding: 20,
                    nodeSpacing: 80,
                    rankSpacing: 120,
                    layoutEngine: 'dagre'
                }}
            }});
            
            let svgPanZoom;
            let isFullscreen = false;
            
            function initializePanZoom() {{
                // Find the SVG element within our container
                const svgElement = document.querySelector('.mermaid svg');
                
                if (svgElement) {{
                    // Initialize pan-zoom on the SVG
                    svgPanZoom = svgPanZoom(svgElement, {{
                        zoomEnabled: true,
                        controlIconsEnabled: true,
                        fit: true,
                        center: true,
                        minZoom: 0.2,
                        maxZoom: 5,
                        zoomScaleSensitivity: 0.4
                    }});
                    
                    // Add event listeners for mouse wheel zoom
                    svgElement.addEventListener('wheel', function(event) {{
                        if (event.ctrlKey || event.metaKey) {{
                            event.preventDefault();
                            if (event.deltaY < 0) {{
                                svgPanZoom.zoomIn();
                            }} else {{
                                svgPanZoom.zoomOut();
                            }}
                        }}
                    }});
                    
                    console.log('Pan-zoom initialized successfully');
                }} else {{
                    console.error('SVG element not found');
                }}
            }}
            
            function toggleFullscreen() {{
                const container = document.getElementById('chart-container');
                isFullscreen = !isFullscreen;
                
                if (isFullscreen) {{
                    // Enter fullscreen
                    container.classList.add('fullscreen');
                    document.body.style.overflow = 'hidden';
                    
                    // Update the button text
                    document.getElementById('fullscreen-btn').innerText = 'Exit Full Screen';
                }} else {{
                    // Exit fullscreen
                    container.classList.remove('fullscreen');
                    document.body.style.overflow = 'auto';
                    
                    // Update the button text
                    document.getElementById('fullscreen-btn').innerText = 'Full Screen View';
                }}
                
                // Resize the pan-zoom after toggling fullscreen
                setTimeout(() => {{
                    if (svgPanZoom) {{
                        svgPanZoom.resize();
                        svgPanZoom.fit();
                        svgPanZoom.center();
                    }}
                }}, 300);
            }}
            
            function zoomIn() {{
                if (svgPanZoom) svgPanZoom.zoomIn();
            }}
            
            function zoomOut() {{
                if (svgPanZoom) svgPanZoom.zoomOut();
            }}
            
            function resetZoom() {{
                if (svgPanZoom) {{
                    svgPanZoom.reset();
                }}
            }}
            
            document.addEventListener('DOMContentLoaded', function() {{
                try {{
                    mermaid.init(undefined, document.querySelector('.mermaid'));
                    console.log('Chart initialized successfully');
                    
                    // Initialize pan-zoom after mermaid renders the chart
                    setTimeout(initializePanZoom, 1000);
                    
                    // Apply styling after rendering
                    setTimeout(function() {{
                        // Find and style nodes
                        const nodes = document.querySelectorAll('.node');
                        const centralNode = document.querySelector('.node:nth-child(1)'); // Try to find central node
                        const edgePaths = document.querySelectorAll('.edgePath');
                        
                        // Style all nodes
                        nodes.forEach(node => {{
                            // Add hover effects
                            node.classList.add('node-interactive');
                            
                            // Check if this node contains a submission technique
                            const nodeText = node.textContent.toLowerCase();
                            if (nodeText.includes('submission') || 
                                nodeText.includes('choke') || 
                                nodeText.includes('lock') || 
                                nodeText.includes('triangle') || 
                                nodeText.includes('bar') ||
                                nodeText.includes('kimura') ||
                                nodeText.includes('guillotine')) {{
                                node.classList.add('submission-node');
                            }}
                            // Check if this node contains a sweep or transition
                            else if (nodeText.includes('sweep') || 
                                    nodeText.includes('transition') || 
                                    nodeText.includes('pass') ||
                                    nodeText.includes('entry')) {{
                                node.classList.add('transition-node');
                            }}
                            // Check if this node contains a position
                            else if (nodeText.includes('guard') || 
                                    nodeText.includes('mount') || 
                                    nodeText.includes('control') ||
                                    nodeText.includes('position')) {{
                                node.classList.add('position-node');
                            }}
                        }});
                        
                        // Style central node specially if found
                        if (centralNode) {{
                            centralNode.classList.add('central-node');
                        }}
                        
                        // Style the edge paths
                        edgePaths.forEach(edge => {{
                            edge.classList.add('edge-interactive');
                        }});
                        
                    }}, 1000);
                }} catch (e) {{
                    console.error('Mermaid error:', e);
                    document.querySelector('.error-message').textContent = 'Error rendering chart: ' + e.message;
                    document.querySelector('.error-message').style.display = 'block';
                }}
            }});
        </script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }}
            
            #chart-container {{
                width: 100%;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                position: relative;
            }}
            
            #chart-container.fullscreen {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                z-index: 1000;
                border-radius: 0;
                padding: 30px;
                overflow: auto;
            }}
            
            .mermaid {{
                width: 100%;
                height: 100%;
                min-height: 500px;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            
            .mermaid svg {{
                width: 100%;
                height: 100%;
                min-height: 500px;
            }}
            
            .controls {{
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
                flex-wrap: wrap;
                align-items: center;
            }}
            
            .controls button {{
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                background-color: #f0f0f0;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.2s ease;
            }}
            
            .controls button:hover {{
                background-color: #ddd;
            }}
            
            #fullscreen-btn {{
                background-color: #000;
                color: white;
            }}
            
            .error-message {{
                color: red;
                font-weight: bold;
                display: none;
                margin: 10px;
                padding: 10px;
                border: 1px solid red;
                background-color: #ffeeee;
            }}
            
            /* Enhanced styling for jiu-jitsu flow chart */
            .node-interactive {{
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            
            .node-interactive:hover {{
                filter: brightness(1.1);
                transform: scale(1.05);
            }}
            
            .central-node rect {{
                fill: #e6f7ff !important;
                stroke: #0099ff !important;
                stroke-width: 3px !important;
                filter: drop-shadow(0px 0px 5px rgba(0, 153, 255, 0.5));
            }}
            
            .submission-node rect {{
                fill: #ffe6e6 !important;
                stroke: #ff6666 !important;
                stroke-width: 2px !important;
            }}
            
            .transition-node rect {{
                fill: #fff2e6 !important;
                stroke: #ff9933 !important;
                stroke-width: 2px !important;
            }}
            
            .position-node rect {{
                fill: #e6fff2 !important;
                stroke: #33cc99 !important;
                stroke-width: 2px !important;
            }}
            
            .node rect {{
                rx: 10;
                ry: 10;
                filter: drop-shadow(0px 2px 3px rgba(0, 0, 0, 0.2));
            }}
            
            .edgePath path {{
                stroke-width: 2px;
                transition: all 0.3s ease;
            }}
            
            .edge-interactive:hover path {{
                stroke-width: 3px;
                filter: drop-shadow(0px 0px 3px rgba(0, 0, 0, 0.3));
            }}
            
            .edgeLabel {{
                background-color: rgba(255, 255, 255, 0.8) !important;
                padding: 3px !important;
                border-radius: 4px !important;
                font-weight: bold !important;
                filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.1));
                max-width: 150px !important;
                overflow-wrap: break-word !important;
            }}
            
            /* Custom zoom controls */
            .zoom-controls {{
                position: absolute;
                top: 10px;
                right: 10px;
                display: flex;
                flex-direction: column;
                gap: 5px;
                z-index: 1001;
            }}
            
            .zoom-controls button {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-color: white;
                border: 1px solid #ddd;
                font-size: 20px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            
            .zoom-controls button:hover {{
                background-color: #f8f8f8;
            }}
            
            .instructions {{
                padding: 10px;
                margin-bottom: 15px;
                background-color: #f8f8f8;
                border-radius: 4px;
                font-size: 14px;
            }}
            
            /* SVG Pan Zoom control icons styling */
            .svg-pan-zoom-control {{
                transition: opacity 0.3s;
                opacity: 0.8;
            }}
            
            .svg-pan-zoom-control:hover {{
                opacity: 1;
            }}
        </style>
    </head>
    <body>
        <div id="chart-container">
            <div class="controls">
                <button id="fullscreen-btn" onclick="toggleFullscreen()">Full Screen View</button>
                <button onclick="resetZoom()">Reset View</button>
                <button onclick="zoomIn()">Zoom In</button>
                <button onclick="zoomOut()">Zoom Out</button>
            </div>
            
            <div class="instructions">
                <strong>Navigation:</strong> 
                Click and drag to pan • Use mouse wheel to scroll • 
                Ctrl/Cmd + mouse wheel to zoom • Use controls for fullscreen view
            </div>
            
            <div class="error-message"></div>
            <div class="mermaid">
{flow_chart}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

# Replace the render_mermaid function in jiu_jitsu_functions.py with this:
def render_mermaid(chart, height=800, width=None):
    """
    Renders a mermaid chart in Streamlit using HTML component.
    
    Parameters:
    -----------
    chart : str
        The chart string to render
    """
    from streamlit.components.v1 import html
    
    # Ensure the chart is properly sanitized
    chart = sanitize_mermaid(chart)
    
    # Simple and reliable HTML for Streamlit
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 5px;
                overflow: auto;
            }}
            .mermaid-container {{
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .mermaid {{
                width: 100%;
                height: 100%;
                overflow: scroll;
            }}
            /* Some basic styling for the nodes */
            .node rect {{
                rx: 10;
                ry: 10;
            }}
            .edgeLabel {{
                background-color: rgba(255, 255, 255, 0.8);
                padding: 3px;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="mermaid">
{chart}
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'default',
                    flowchart: {{
                        useMaxWidth: false,
                        htmlLabels: true,
                        curve: 'basis'
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    # Render the HTML, with sufficient height to display the chart
    html(html_content, height=height, width=width, scrolling=True)

def next_move(flow_chart, move_text, measurables, isMMA=True, favorite_ideas=""):
    """
    Generates a new detailed flow chart based on the selected move from an existing chart,
    maintaining the technical complexity and branching patterns.
    
    Parameters:
    -----------
    flow_chart : str
        The original flow chart string
    move_text : str
        The text of the move/position to focus on next
    measurables : str
        Physical attributes and characteristics of the athlete
    isMMA : bool, optional
        Whether to use MMA rules (True) or IBJJF rules (False)
    favorite_ideas : str, optional
        Additional ideas or preferences to consider
        
    Returns:
    --------
    str
        A new detailed mermaid flow chart focused on the selected move
    """
    # Remove DEBUG INFO section if present
    if "DEBUG INFO:" in flow_chart and "MERMAID:" in flow_chart:
        parts = flow_chart.split("MERMAID:")
        if len(parts) > 1:
            flow_chart = parts[1].strip()
    
    # Remove any debug info at the end
    if "[Debug:" in flow_chart:
        flow_chart = flow_chart.split("[Debug:")[0].strip()
    
    # Parse the flow chart to find the next node
    lines = flow_chart.strip().split('\n')
    new_position = None
    node_id = None
    context_nodes = []  # To store connected nodes for contextual information
    
    # First try to find if the text matches a node label
    for line in lines:
        if "[" in line and "]" in line:
            # Extract the node text
            start_idx = line.find("[")
            end_idx = line.find("]")
            node_text = line[start_idx+1:end_idx].strip()
            
            # Remove quotes if present
            if node_text.startswith('"') and node_text.endswith('"'):
                node_text = node_text[1:-1]
            
            # Check if this matches what user entered
            if move_text.lower() in node_text.lower():
                # Extract the node ID
                node_id = line[:start_idx].strip()
                new_position = node_text
                break
    
    # If no node found, try to find if the text matches a connection label
    if not new_position:
        for line in lines:
            if "-->|" in line and "|" in line[line.index("-->|")+4:]:
                # Extract the arrow label
                start_idx = line.index("-->|") + 4
                end_idx = line.index("|", start_idx)
                arrow_text = line[start_idx:end_idx].strip()
                
                # Remove quotes if present
                if arrow_text.startswith('"') and arrow_text.endswith('"'):
                    arrow_text = arrow_text[1:-1]
                
                # Check if this matches what user entered
                if move_text.lower() in arrow_text.lower():
                    # Find the target node
                    parts = line.split("|", 1)
                    if len(parts) > 1:
                        target_part = parts[1].split("|")[1] if "|" in parts[1] else parts[1]
                        
                        # Extract the node ID and text
                        if "[" in target_part and "]" in target_part:
                            start_idx = target_part.find("[")
                            end_idx = target_part.find("]")
                            node_text = target_part[start_idx+1:end_idx].strip()
                            
                            # Remove quotes if present
                            if node_text.startswith('"') and node_text.endswith('"'):
                                node_text = node_text[1:-1]
                            
                            node_id = target_part[:start_idx].strip()
                            new_position = node_text
                            break
    
    # If node found, collect connected nodes for context
    if node_id:
        for line in lines:
            # Check for outbound connections from our node
            if line.strip().startswith(node_id) and "-->|" in line:
                if "[" in line and "]" in line:
                    # Extract the target node text
                    parts = line.split("-->|", 1)[1].split("|", 1)[1]
                    start_idx = parts.find("[")
                    end_idx = parts.find("]")
                    if start_idx >= 0 and end_idx >= 0:
                        target_text = parts[start_idx+1:end_idx].strip()
                        # Remove quotes if present
                        if target_text.startswith('"') and target_text.endswith('"'):
                            target_text = target_text[1:-1]
                        context_nodes.append(target_text)
            
            # Check for inbound connections to our node
            elif "-->|" in line and node_id in line.split("-->|", 1)[1]:
                if "[" in line and "]" in line:
                    # Extract the source node text
                    parts = line.split("-->|", 1)[0]
                    start_idx = parts.find("[")
                    end_idx = parts.find("]")
                    if start_idx >= 0 and end_idx >= 0:
                        source_text = parts[start_idx+1:end_idx].strip()
                        # Remove quotes if present
                        if source_text.startswith('"') and source_text.endswith('"'):
                            source_text = source_text[1:-1]
                        context_nodes.append(source_text)
    
    # If no node found or no text, return the original chart
    if not new_position:
        return flow_chart
    
    print(f"Found position: {new_position} (node ID: {node_id})")
    print(f"Connected positions: {', '.join(context_nodes) if context_nodes else 'None'}")
    
    # Generate a new flow chart with the found position as the center
    # Add context information to favorite_ideas to maintain coherence
    context_info = ""
    if context_nodes:
        context_info = f"Connect to previously listed flow chart positions with the correct logical structure: {', '.join(context_nodes)}. "
    
    enhanced_ideas = context_info + favorite_ideas
    
    # Call the enhanced generate_flow_chart_with_start function
    return generate_flow_chart_with_start(measurables, new_position, isMMA, enhanced_ideas)
    """
    Generates a new flow chart based on the selected move from an existing chart.
    """
    # Remove DEBUG INFO section if present
    if "DEBUG INFO:" in flow_chart and "MERMAID:" in flow_chart:
        parts = flow_chart.split("MERMAID:")
        if len(parts) > 1:
            flow_chart = parts[1].strip()
    
    # Remove any debug info at the end
    if "[Debug:" in flow_chart:
        flow_chart = flow_chart.split("[Debug:")[0].strip()
    
    # Parse the flow chart to find the next node
    lines = flow_chart.strip().split('\n')
    new_position = None
    node_id = None
    
    # First try to find if the text matches a node label
    for line in lines:
        if "[" in line and "]" in line:
            # Extract the node text
            start_idx = line.find("[")
            end_idx = line.find("]")
            node_text = line[start_idx+1:end_idx].strip()
            
            # Remove quotes if present
            if node_text.startswith('"') and node_text.endswith('"'):
                node_text = node_text[1:-1]
            
            # Check if this matches what user entered
            if move_text.lower() in node_text.lower():
                # Extract the node ID
                node_id = line[:start_idx].strip()
                new_position = node_text
                break
    
    # If no node found, try to find if the text matches a connection label
    if not new_position:
        for line in lines:
            if "-->|" in line and "|" in line[line.index("-->|")+4:]:
                # Extract the arrow label
                start_idx = line.index("-->|") + 4
                end_idx = line.index("|", start_idx)
                arrow_text = line[start_idx:end_idx].strip()
                
                # Remove quotes if present
                if arrow_text.startswith('"') and arrow_text.endswith('"'):
                    arrow_text = arrow_text[1:-1]
                
                # Check if this matches what user entered
                if move_text.lower() in arrow_text.lower():
                    # Find the target node
                    parts = line.split("|", 1)
                    if len(parts) > 1:
                        target_part = parts[1].split("|")[1] if "|" in parts[1] else parts[1]
                        
                        # Extract the node ID and text
                        if "[" in target_part and "]" in target_part:
                            start_idx = target_part.find("[")
                            end_idx = target_part.find("]")
                            node_text = target_part[start_idx+1:end_idx].strip()
                            
                            # Remove quotes if present
                            if node_text.startswith('"') and node_text.endswith('"'):
                                node_text = node_text[1:-1]
                            
                            node_id = target_part[:start_idx].strip()
                            new_position = node_text
                            break
    
    # If no node found or no text, return the original chart
    if not new_position:
        return flow_chart
    
    print(f"Found position: {new_position} (node ID: {node_id})")
    
    # Generate a new flow chart with the found position as the center
    return generate_flow_chart_with_start(measurables, new_position, isMMA, favorite_ideas)

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
        prompt += "height and weight, plus any other grappling relevant attributes"
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
    
def adversarial_game_plan(original_plan, ruleset="IBJJF", position="", measurables="", api_key=None):
    """
    Generates an adversarial game plan to counter a jiu-jitsu strategy.
    
    Parameters:
    -----------
    original_plan : str
        The original game plan text or Mermaid flowchart to counter
    ruleset : str, optional
        The ruleset to use (e.g., "IBJJF", "MMA")
    position : str, optional
        The starting position for the counter strategy
    measurables : str, optional
        Physical attributes and characteristics of the athlete
    api_key : str, optional
        OpenAI API key (defaults to environment variable)
        
    Returns:
    --------
    str
        An adversarial game plan in the same format as the input (text or Mermaid)
    """
    # Debug information
    debug_info = f"Function called with:\nruleset: {ruleset}\nposition: {position}\nmeasurables: {measurables}\n"
    
    try:
        # Get API key from environment if not provided
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return "Error: OpenAI API Key not found in environment variables"
        
        # Initialize GenAI
        debug_info += f"Creating GenAI instance with API key: {api_key[:5]}...\n"
        genai = GenAI(api_key)
        
        # Determine input format (Mermaid chart or text)
        is_mermaid = "graph " in original_plan or "flowchart " in original_plan
        debug_info += f"Input format detected: {'Mermaid chart' if is_mermaid else 'Text'}\n"
        
        # Create prompt based on format
        if is_mermaid:
            # For Mermaid flowchart input
            prompt = f"""Generate an adversarial Jiu-Jitsu game plan to counter the following technique flowchart.

ORIGINAL FLOWCHART:
{original_plan}

INSTRUCTIONS:
1. Analyze the original flowchart and identify key vulnerabilities
2. Create a NEW Mermaid flowchart that shows specific counters to the techniques
3. Your flowchart must use the same format (graph LR/TD) as the original
4. Start with node A being the initial counter position: "{position if position else 'Counter Strategy'}"
5. Include specific technical details in your counter techniques
6. Ensure each counter addresses an actual technique from the original flowchart
7. ONLY return the Mermaid flowchart code, nothing else

The counter strategy should follow {ruleset} rules.
"""
            if measurables:
                prompt += f"\nThe athlete has these attributes: {measurables}"
            
            # Add formatting guidelines
            prompt += """
Important formatting requirements:
1. Use simple node IDs (A, B, C, etc.)
2. PUT DOUBLE QUOTES around all node text and arrow labels
3. Make the starting position node A and place it in the center
4. Maximum of 16-20 nodes total
5. Create transitions that branch outward from the center
"""
        else:
            # For text input
            prompt = f"""Generate an adversarial Jiu-Jitsu game plan to counter the following strategy:

ORIGINAL STRATEGY:
{original_plan}

INSTRUCTIONS:
1. Analyze the original strategy and identify key vulnerabilities and weaknesses
2. Create a detailed counter strategy that exploits these vulnerabilities
3. Organize your response with clear sections and specific technical details
4. Include specific grips, weight distribution, and timing
5. Focus on preventing the opponent from implementing their game plan
6. Include at least 3-4 specific counter techniques

The counter strategy should follow {ruleset} rules and start from the {position if position else 'appropriate'} position.
"""
            if measurables:
                prompt += f"\nThe counter athlete has these attributes: {measurables}"
        
        debug_info += f"Created prompt: {prompt[:100]}...\n"
        
        # Generate the adversarial game plan
        debug_info += "Calling generate_text...\n"
        response = genai.generate_text(prompt)
        debug_info += f"Response received from API: {response[:100]}...\n"
        
        # Clean up the response
        if "[Debug:" in response:
            response = response.split("[Debug:")[0].strip()
        
        # For Mermaid, extract just the code
        if is_mermaid and "```" in response:
            code_parts = response.split("```")
            for part in code_parts:
                if "graph" in part or "flowchart" in part:
                    response = part.strip()
                    break
            
            # Sanitize the Mermaid chart
            response = sanitize_mermaid(response)
        
        # Return both debug info and response during development
        return f"DEBUG INFO:\n{debug_info}\n\nRESPONSE:\n{response}"
    
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return f"Error generating adversarial game plan:\n{debug_info}\n\nException: {str(e)}\n\nTraceback:\n{tb}"

def format_strategy_for_display(strategy_text, role="initiator"):
    """
    Formats a strategy text for better display in the UI.
    Detects bullet points and ensures proper HTML formatting.
    
    Parameters:
    -----------
    strategy_text : str
        The strategy text to format
    role : str
        Either "initiator" or "defender" to determine styling
        
    Returns:
    --------
    str
        HTML-formatted strategy text
    """
    # Strip any remaining markdown or formatting indicators
    strategy_text = strategy_text.replace("```", "").strip()
    
    # Determine CSS class based on role
    css_class = "initiator-column" if role == "initiator" else "defender-column"
    
    # Check if text already has bullet points
    has_bullets = any(line.strip().startswith(('•', '-', '*', '1.', '2.', '3.')) for line in strategy_text.split('\n'))
    
    if has_bullets:
        # Convert markdown-style bullets to HTML list items
        lines = strategy_text.split('\n')
        formatted_lines = []
        
        in_list = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith(('•', '-', '*')):
                if not in_list:
                    formatted_lines.append("<ul class='strategy-bullet'>")
                    in_list = True
                # Extract the text after the bullet
                bullet_text = line[1:].strip()
                formatted_lines.append(f"<li>{bullet_text}</li>")
            elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                if not in_list:
                    formatted_lines.append("<ol>")
                    in_list = True
                # Extract the text after the number
                number_text = line.split('.', 1)[1].strip()
                formatted_lines.append(f"<li>{number_text}</li>")
            else:
                if in_list:
                    formatted_lines.append("</ul>" if line.startswith(('•', '-', '*')) else "</ol>")
                    in_list = False
                formatted_lines.append(f"<p>{line}</p>")
        
        if in_list:
            formatted_lines.append("</ul>" if lines[-1].startswith(('•', '-', '*')) else "</ol>")
        
        content = "\n".join(formatted_lines)
    else:
        # If no bullet points, just wrap in paragraph tags
        paragraphs = [p for p in strategy_text.split('\n\n') if p.strip()]
        content = "\n".join([f"<p>{p}</p>" for p in paragraphs])
    
    # Wrap in a div with appropriate class
    formatted_html = f"""
    <div class='strategy-entry {css_class}'>
        {content}
    </div>
    """
    
    return formatted_html

def display_strategy_battle(left_history, right_history):
    """
    Creates HTML for displaying the strategy battle between two opponents with equal height rows
    and color coordination for sequential responses. Supports multiple messages per participant.
    
    Parameters:
    -----------
    left_history : list
        List of strategies from the initiator
    right_history : list
        List of strategies from the defender
        
    Returns:
    --------
    str
        HTML string for displaying the battle
    """
    # Start HTML with container and styling
    html = """
    <style>
        .strategy-battle-container {
            width: 100%;
            box-sizing: border-box;
        }
        
        .strategy-row {
            display: flex;
            margin-bottom: 20px;
            width: 100%;
        }
        
        .strategy-cell {
            width: 48%;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }
        
        .strategy-cell.left {
            margin-right: 4%;
        }
        
        .strategy-cell h4 {
            margin-top: 0;
            margin-bottom: 15px;
            border-bottom: 1px solid rgba(0,0,0,0.1);
            padding-bottom: 8px;
        }
        
        .loading-cell {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 150px;
        }
        
        .loading-image {
            max-width: 80%;
            max-height: 130px;
            object-fit: contain;
        }
        
        /* Row color coordination */
        .row-level-0 { background-color: rgba(230, 242, 255, 0.7); }
        .row-level-1 { background-color: rgba(248, 238, 255, 0.7); }
        .row-level-2 { background-color: rgba(255, 242, 230, 0.7); }
        .row-level-3 { background-color: rgba(230, 255, 242, 0.7); }
        .row-level-4 { background-color: rgba(255, 230, 230, 0.7); }
        
        /* Content formatting */
        .strategy-content {
            width: 100%;
        }
        
        .strategy-bullet {
            padding-left: 20px;
            margin-top: 10px;
            margin-bottom: 10px;
            list-style-type: disc;
        }
        
        .strategy-bullet li {
            margin-bottom: 10px;
            padding-left: 5px;
        }
        
        /* Empty cell styling */
        .empty-cell {
            background-color: rgba(245, 245, 245, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #888;
            font-style: italic;
            min-height: 150px;
        }
    </style>
    
    <div class="strategy-battle-container">
        <div class="strategy-row">
            <div class="strategy-cell left">
                <h4>Initiator Strategy</h4>
            </div>
            <div class="strategy-cell right">
                <h4>Defender Strategy</h4>
            </div>
        </div>
    """
    
    # Create lists to pair messages for display
    max_pairs = max(len(left_history), len(right_history))
    paired_rows = []
    
    for i in range(max_pairs):
        left_content = left_history[i]["content"] if i < len(left_history) else None
        right_content = right_history[i]["content"] if i < len(right_history) else None
        paired_rows.append((left_content, right_content, i))
    
    # Generate rows with matched heights
    for left_content, right_content, index in paired_rows:
        row_class = f"row-level-{index % 5}"  # Cycle through 5 different row colors
        
        html += f'<div class="strategy-row">'
        
        # Left cell (Initiator)
        if left_content:
            # Format the content with preferred bullet format
            formatted_content = format_strategy_for_display(left_content, bullet_style='bullet')
            html += f'<div class="strategy-cell left {row_class}"><div class="strategy-content">{formatted_content}</div></div>'
        else:
            # If waiting for response, show loading image
            html += f'''
            <div class="strategy-cell left {row_class} loading-cell">
                <img src="hero_response.png" alt="Hero thinking..." class="loading-image">
            </div>
            '''
        
        # Right cell (Defender)
        if right_content:
            # Format the content with preferred bullet format
            formatted_content = format_strategy_for_display(right_content, bullet_style='bullet')
            html += f'<div class="strategy-cell right {row_class}"><div class="strategy-content">{formatted_content}</div></div>'
        else:
            # If waiting for response, show loading image
            html += f'''
            <div class="strategy-cell right {row_class} loading-cell">
                <img src="villain_response.png" alt="Villain thinking..." class="loading-image">
            </div>
            '''
            
        html += '</div>'  # Close row
    
    # Close container
    html += '</div>'
    
    return html

def format_strategy_for_display(strategy_text, bullet_style='bullet'):
    """
    Formats a strategy text for better display in the UI with preferred bullet formatting.
    
    Parameters:
    -----------
    strategy_text : str
        The strategy text to format
    bullet_style : str
        Style of bullets to use ('bullet' or 'asterisk')
        
    Returns:
    --------
    str
        HTML-formatted strategy text
    """
    # Strip any remaining markdown or formatting indicators
    strategy_text = strategy_text.replace("```", "").strip()
    
    # Check if text already has bullet points or numbered items
    has_bullets = any(line.strip().startswith(('•', '-', '*', '1.', '2.', '3.')) for line in strategy_text.split('\n'))
    
    if has_bullets:
        # Convert to the preferred bullet format
        lines = strategy_text.split('\n')
        formatted_text = ""
        
        # First, convert to plain text points
        points = []
        current_point = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                # If starting a new point and we already have one, save it
                if current_point:
                    points.append(current_point)
                
                # Extract the text after the bullet/number
                if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    current_point = line.split('.', 1)[1].strip()
                else:
                    current_point = line[1:].strip()
            else:
                # Continuation of current point
                if current_point:
                    current_point += " " + line
                else:
                    current_point = line
        
        # Add the last point if there is one
        if current_point:
            points.append(current_point)
        
        # Now format with the preferred style
        if points:
            formatted_text += "<ul class='strategy-bullet'>\n"
            for point in points:
                formatted_text += f"<li>{point}</li>\n"
            formatted_text += "</ul>"
        
        return formatted_text
    else:
        # If no bullet points, split into paragraphs
        paragraphs = [p for p in strategy_text.split('\n\n') if p.strip()]
        
        if len(paragraphs) > 1:
            return "\n".join([f"<p>{p.replace('\n', ' ')}</p>" for p in paragraphs])
        else:
            # Look for line breaks and convert each line to a bullet point
            lines = [line.strip() for line in strategy_text.split('\n') if line.strip()]
            
            if len(lines) > 1:
                # Multiple lines - format as bullet points
                formatted_text = "<ul class='strategy-bullet'>\n"
                for line in lines:
                    formatted_text += f"<li>{line}</li>\n"
                formatted_text += "</ul>"
                return formatted_text
            else:
                # Just one paragraph
                return f"<p>{strategy_text}</p>"
            
def get_image_base64(image_path):
    """
    Convert an image file to base64 encoding for embedding in HTML.
    
    Parameters:
    -----------
    image_path : str
        Path to the image file
        
    Returns:
    --------
    str
        Base64 encoded string of the image
    """
    import base64
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error loading image {image_path}: {str(e)}")
        return None

def save_default_waiting_images():
    """
    Generate and save default waiting images if the actual image files don't exist.
    This ensures the app doesn't break if the image files are missing.
    
    Returns:
    --------
    tuple
        (hero_image_path, villain_image_path)
    """
    import os
    from PIL import Image, ImageDraw, ImageFont
    
    hero_path = "hero_response.png"
    villain_path = "villain_response.png"
    
    # Create default images if they don't exist
    if not os.path.exists(hero_path):
        # Create a simple image with text
        img = Image.new('RGB', (300, 150), color=(230, 242, 255))
        d = ImageDraw.Draw(img)
        try:
            # Try to use a system font
            font = ImageFont.truetype("Arial", 20)
        except:
            # Fallback to default
            font = ImageFont.load_default()
        
        d.text((50, 75), "Hero thinking...", fill=(0, 0, 0), font=font)
        img.save(hero_path)
        print(f"Created default hero image at {hero_path}")
    
    if not os.path.exists(villain_path):
        # Create a simple image with text
        img = Image.new('RGB', (300, 150), color=(255, 230, 230))
        d = ImageDraw.Draw(img)
        try:
            # Try to use a system font
            font = ImageFont.truetype("Arial", 20)
        except:
            # Fallback to default
            font = ImageFont.load_default()
        
        d.text((50, 75), "Villain thinking...", fill=(0, 0, 0), font=font)
        img.save(villain_path)
        print(f"Created default villain image at {villain_path}")
    
    return hero_path, villain_path

def trim_video(input_path, output_path, start_time, end_time):
    """
    Trims a video file to the specified time range.
    
    Parameters:
    -----------
    input_path : str
        Path to the input video file
    output_path : str
        Path where the trimmed video will be saved
    start_time : float
        Start time in seconds
    end_time : float
        End time in seconds
        
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    import subprocess
    import os
    
    try:
        # Ensure the input file exists
        if not os.path.exists(input_path):
            print(f"Input file does not exist: {input_path}")
            return False
        
        # Execute ffmpeg command to trim the video
        # -ss specifies the start time, -to specifies the end time
        # -c copy copies the streams without re-encoding (fast)
        command = [
            "ffmpeg",
            "-i", input_path,
            "-ss", str(start_time),
            "-to", str(end_time),
            "-c", "copy",   # Use copy to avoid re-encoding
            "-y",           # Overwrite output file if it exists
            output_path
        ]
        
        # Execute the command
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if command was successful
        if process.returncode != 0:
            print(f"Error trimming video: {process.stderr}")
            return False
            
        # Verify the output file exists
        if not os.path.exists(output_path):
            print("Output file was not created")
            return False
            
        print(f"Video trimmed successfully to {output_path}")
        return True
        
    except Exception as e:
        print(f"Exception while trimming video: {str(e)}")
        return False

def get_video_duration(video_path):
    """
    Gets the duration of a video file in seconds.
    
    Parameters:
    -----------
    video_path : str
        Path to the video file
        
    Returns:
    --------
    float
        Duration in seconds, or None if an error occurs
    """
    import subprocess
    import json
    
    try:
        # Use ffprobe to get video metadata
        command = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            video_path
        ]
        
        # Execute the command
        process = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if command was successful
        if process.returncode != 0:
            print(f"Error getting video duration: {process.stderr}")
            return None
        
        # Parse the JSON output
        output = json.loads(process.stdout)
        duration = float(output["format"]["duration"])
        
        return duration
        
    except Exception as e:
        print(f"Exception while getting video duration: {str(e)}")
        return None

def generate_video_thumbnail(video_path, thumbnail_path, time_position=1.0):
    """
    Extracts a thumbnail from a video at the specified time position.
    
    Parameters:
    -----------
    video_path : str
        Path to the video file
    thumbnail_path : str
        Path where the thumbnail will be saved
    time_position : float
        Time position in seconds to extract the thumbnail
        
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    import subprocess
    import os
    
    try:
        # Execute ffmpeg command to extract the frame
        command = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(time_position),  # Seek to this position
            "-frames:v", "1",           # Extract one frame
            "-q:v", "2",                # High quality JPEG
            "-y",                       # Overwrite output file if it exists
            thumbnail_path
        ]
        
        # Execute the command
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if command was successful
        if process.returncode != 0:
            print(f"Error generating thumbnail: {process.stderr}")
            return False
            
        # Verify the output file exists
        if not os.path.exists(thumbnail_path):
            print("Thumbnail was not created")
            return False
            
        print(f"Thumbnail generated successfully at {thumbnail_path}")
        return True
        
    except Exception as e:
        print(f"Exception while generating thumbnail: {str(e)}")
        return False

def format_strategy_content(content):
    """
    Format strategy content with proper bullet points.
    
    Parameters:
    -----------
    content : str
        The content to format
        
    Returns:
    --------
    str
        HTML formatted content
    """
    # Format bullet points if needed
    if any(line.strip().startswith(('•', '-', '*', '1.', '2.', '3.')) for line in content.split('\n')):
        formatted_content = "<ul class='strategy-bullet'>"
        for line in content.split('\n'):
            line = line.strip()
            if line and line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                # Extract text after the bullet
                if line.startswith(('1.', '2.', '3.')):
                    text = line.split('.', 1)[1].strip()
                else:
                    text = line[1:].strip()
                formatted_content += f"<li>{text}</li>"
        formatted_content += "</ul>"
    else:
        # Handle regular text
        formatted_content = "<p>" + content.replace('\n\n', '</p><p>').replace('\n', '<br>') + "</p>"
    
    return formatted_content