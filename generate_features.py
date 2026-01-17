import json
from datetime import datetime

def generate_features():
    # Simplified categories for a local single-user app
    categories = {
        "A. Core Workflow": 10,       # Creating songs, generating vibes, drafting lyrics
        "B. Local Persistence": 5,    # Saving/loading from SQLite
        "C. UI/UX Interaction": 8,    # Sidebar, editor, glassmorphism
        "D. Gemini Integration": 5,   # API calls, streaming, thinking models
        "E. Error Handling": 3,       # Basic error states (no network, API error)
        "F. Navigation": 4            # Basic routing (Home, Editor, Library)
    }

    features = []
    feature_id = 1
    test_id = 1

    # Define specific high-value features for the core app
    core_features = [
        ("A. Core Workflow", "Create New Song", "User can create a new song project with a title."),
        ("A. Core Workflow", "Generate Vibe Cloud", "User enters a keyword, Gemini Flash generates sensory anchors."),
        ("A. Core Workflow", "Draft Lyrics (Ghostwriter)", "Gemini Pro writes lyrics based on Vibe Cloud anchors."),
        ("A. Core Workflow", "Syllable Counter", "Real-time syllable counting updates as user types."),
        ("A. Core Workflow", "Stress Highlighting", "Gemini identifies and highlights stressed syllables."),
        ("A. Core Workflow", "Rhyme Scheme Setup", "User can define rhyme schemes (AABB, ABAB) for the Architect agent."),
        ("A. Core Workflow", "Anti-Cliché Filter", "Verify generated lyrics don't contain banned words."),
        ("A. Core Workflow", "Manual Edit", "User can manually edit generated lyrics."),
        ("A. Core Workflow", "Regenerate Line", "User can request a regeneration of a specific line."),
        ("A. Core Workflow", "Clear Session", "User can reset the current workspace."),
        
        ("B. Local Persistence", "Auto-Save", "Changes to lyrics are auto-saved to SQLite."),
        ("B. Local Persistence", "Load Song", "Opening a song from the library loads all data correctly."),
        ("B. Local Persistence", "Delete Song", "User can delete a song project permanently."),
        ("B. Local Persistence", "Rename Song", "User can rename an existing song."),
        ("B. Local Persistence", "Export Lyrics", "User can copy lyrics to clipboard or save as text file."),

        ("C. UI/UX Interaction", "Sidebar Navigation", "Switch between songs via sidebar."),
        ("C. UI/UX Interaction", "Glassmorphic Panels", "Verify visual styling of panels."),
        ("C. UI/UX Interaction", "Thinking Indicator", "Show pulse animation during Gemini API calls."),
        ("C. UI/UX Interaction", "Responsive Editor", "Editor resizes correctly on window resize."),
        ("C. UI/UX Interaction", "Theme Consistency", "Colors match the VibeFlow aesthetic."),
        ("C. UI/UX Interaction", "Input Feedback", "Buttons show active/disabled states."),
        ("C. UI/UX Interaction", "Toast Notifications", "Show success/error messages for actions."),
        ("C. UI/UX Interaction", "Keyboard Shortcuts", "Basic shortcuts like Cmd+S (though auto-save exists)."),

        ("D. Gemini Integration", "API Key Config", "Load API key from environment variable."),
        ("D. Gemini Integration", "Stream Response", "Lyrics appear word-by-word via streaming."),
        ("D. Gemini Integration", "Model Switching", "System uses Flash for vibes, Pro for writing."),
        ("D. Gemini Integration", "Thought Signature Storage", "Save/Resume 'thought signature' for context."),
        ("D. Gemini Integration", "Token Usage", "Graceful handling of context limits (basic)."),

        ("E. Error Handling", "API Failure", "Show friendly error if Gemini is unreachable."),
        ("E. Error Handling", "Empty Input", "Prevent submission of empty prompts."),
        ("E. Error Handling", "DB Lock", "Handle SQLite lock gracefully (retry)."),

        ("F. Navigation", "Home Dashboard", "Show 'Create New' or 'Recent Songs' on load."),
        ("F. Navigation", "Editor Route", "Direct URL to song ID works."),
        ("F. Navigation", "404 Page", "Redirect to home for invalid song IDs."),
        ("F. Navigation", "Library View", "List all songs with metadata.")
    ]

    for cat, name, desc in core_features:
        f_id = f"F{feature_id:03}"
        
        feature = {
            "id": f_id,
            "category": cat,
            "name": name,
            "description": desc,
            "priority": 1,
            "dependencies": [],
            "status": "pending",
            "test_cases": [],
            "files_modified": []
        }

        # Generate 3 standard test steps for each feature
        steps = ["Input/Action", "Verification", "Persistence/State Check"]
        for s_idx, s_name in enumerate(steps):
            feature["test_cases"].append({
                "id": f"T{test_id:04}",
                "description": f"Step {s_idx+1}: {s_name} for {name}",
                "status": "pending"
            })
            test_id += 1
        
        features.append(feature)
        feature_id += 1

    project = {
        "project_name": "VibeFlow Studio (Local Lite)",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "features": features
    }

    with open("features.json", "w") as f:
        json.dump(project, f, indent=2)

if __name__ == "__main__":
    generate_features()