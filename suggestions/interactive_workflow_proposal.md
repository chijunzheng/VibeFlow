# Proposal: Interactive Vibe & Lyric Loop

## Goal
Transform the current "One-Click" generation into an interactive, human-in-the-loop creative tool. This allows users to refine the *direction* (Vibe) before committing to the *destination* (Lyrics).

## 1. The Interactive Vibe Loop (Architectural Change)

Currently, the frontend calls `POST /songs/{id}/generate_vibe` which automatically saves the result. The user sees it but can't easily tweak it before lyric generation.

**Proposed Flow:**
1.  **User Input:** User provides a seed (e.g., "Sleep").
2.  **AI Brainstorm (New Endpoint):** `POST /ai/brainstorm_vibes`
    *   Returns 10-15 candidates (Visuals, Sounds, Metaphors).
    *   *Does not save to Song DB yet.*
3.  **UI Selection:** User clicks/toggles the anchors they like.
    *   *User can also add custom anchors manually.*
4.  **Refine (Optional):** User clicks "More like this" on selected anchors.
5.  **Commit:** User clicks "Save Vibe".
    *   Frontend calls `PUT /songs/{id}` with the *final curated list* of anchors.

## 2. The Lyric Feedback Loop

Once the Vibe is set, the Lyric generation can also be iterative.

**Proposed Flow:**
1.  **Drafting:** User requests lyrics. AI generates "Draft 1".
2.  **Highlight & Critique:**
    *   User highlights a section (Verse 1).
    *   User selects a directive: "Make it darker", "Too rhymey", "Show, don't tell".
3.  **Targeted Regenerate (Agentic Rewrite):**
    *   The `rewrite_text` tool (already in `ai.py`) is exposed to the UI.
    *   AI rewrites *only* that section while maintaining context.

## 3. Implementation Suggestions

### Backend (`backend/ai.py` & `backend/api/`)
-   **Split `generate_vibe`:** Expose the candidate generation and curation steps as separate utilities if needed, or simply allow the Frontend to pass the *final* anchors into the `stream_lyrics` endpoint (overriding the DB ones temporarily or permanently).
-   **New Endpoint:** `POST /songs/{id}/refine_lyrics` taking `{current_lyrics, selection_range, instruction}`.

### Frontend
-   **Vibe Card:** transform into a "Tag Cloud" component where items are selectable/dismissible.
-   **Lyric Editor:** A rich text editor where the AI stream is just the *initial* state. Highlighting text pops up a "Magic Wand" menu for AI adjustments.

## 4. Immediate Value (What we just did)
We have implemented an *internal* loop for the Vibe Cloud:
1.  **Generate:** Creates 10 cinematic/atmospheric options.
2.  **Curate:** AI selects the best 5 automatically.

This provides higher quality defaults immediately, while paving the way for the fully interactive UI described above.
