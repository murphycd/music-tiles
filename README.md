# Musical Tile Grid (Tonnetz Explorer)

This application provides an interactive musical grid based on the Tonnetz, a conceptual lattice diagram representing tonal relationships. Users can select tiles on an infinite grid to play musical notes, pan and zoom the view, and switch between different grid layouts and MIDI instruments.

## Architecture Overview

The application is built on a decoupled, **event-driven architecture** using a publish/subscribe pattern. This design separates the core data model from the components that react to its changes, such as the user interface and the audio output.

The flow of information is as follows:

1.  **User Interaction**: The main `App` class in `main.py` captures user input (mouse clicks, drags, scrolls).
2.  **Model Update**: The `App` translates user input into commands that modify the state of the `TonnetzModel` (e.g., `model.toggle_selection()`).
3.  **Event Broadcasting**: The `TonnetzModel` updates its internal state and then broadcasts an event (e.g., `TileSelectedEvent`) to all registered listeners. It has no knowledge of what these listeners are or what they do.
4.  **Listener Reaction**:
    - The `GridRenderer` (a listener) receives the event and updates the visual representation of the affected tile on the screen.
    - The `MidiController` (another listener) receives the same event, uses the `NoteMapper` to translate the tile's coordinate into a MIDI note, and instructs the `MidiHandler` to play the sound.

This decoupling means new output vectors (like a visualizer, OSC message sender, or a different synthesizer) can be added simply by creating a new listener class and registering it with the model, without changing any existing code.

### ASCII Architecture Diagram

```text
[ User Input ]
 (Mouse Click/Drag)
       |
       v
+--------------+
| App (main.py)|
| (Controller) |
+--------------+
       |
       | 1. Calls a method on the model, e.g.,
       |    model.toggle_selection(coord, octave)
       v
+-----------------+
| TonnetzModel    |
| (Data & Events) |
+-----------------+
       |
       | 2. Broadcasts an event to all listeners:
       |    _notify(TileSelectedEvent(...))
       +-------------------------------------------------+
       |                                                 |
       v                                                 v
+----------------+                                +-------------------+
| GridRenderer   |                                | MidiController    |
| (Listener)     |                                | (Listener)        |
+----------------+                                +-------------------+
       |                                                 |
       | 3a. Receives event, updates                   | 3b. Receives event, uses
       |     the canvas visuals.                         |     NoteMapper to get MIDI note.
       v                                                 v
+----------------+                                +-------------------+
|   Tkinter      |                                | MidiHandler       |
|   Canvas       |                                | (MIDI Output)     |
+----------------+                                +-------------------+

## Component Breakdown

* **`main.py`**: The application entry point. Initializes all components, sets up the UI with Tkinter, and connects user input events to the `TonnetzModel`.
* **`tonnetz.py`**: The core data model (`TonnetzModel`). Manages the state of selected tiles and their octaves. It acts as an event broadcaster, notifying listeners of any state changes.
* **`events.py`**: Defines the simple data classes (`TileSelectedEvent`, `SelectionClearedEvent`, etc.) used for communication between the model and its listeners.
* **`renderer.py`**: The `GridRenderer` class, which listens to model events and handles all drawing operations on the Tkinter canvas.
* **`midi_controller.py`**: The `MidiController` class, which listens to model events and translates them into MIDI commands. It acts as the bridge between the abstract model and the concrete MIDI output.
* **`note_mapper.py`**: A stateless utility class (`NoteMapper`) that contains the pure logic for converting grid coordinates and octaves into MIDI note numbers.
* **`midi_handler.py`**: A low-level wrapper (`MidiHandler`) for the `pyfluidsynth` library, responsible for all direct communication with the FluidSynth synthesizer.
* **`viewport.py`**: Manages the view state (pan, zoom) and handles coordinate transformations between the canvas (pixels) and the grid's world space (q, r).
* **`config.py`**: Contains all configuration constants for styling, interaction, music theory, and MIDI settings.
* **`utils.py`**: A collection of pure, standalone utility functions for geometry (Bresenham's algorithm) and music theory calculations.

---

## Installation and Setup

### 1. Python Dependencies

The project requires the `pyfluidsynth` library. You can install it using pip:

    pip install pyfluidsynth

### 2. FluidSynth Synthesizer

`pyfluidsynth` is a wrapper and requires the underlying **FluidSynth** software synthesizer to be installed on your system.

**For Windows:**

1.  Go to the official FluidSynth repository's releases page: [https://github.com/FluidSynth/fluidsynth/releases](https://github.com/FluidSynth/fluidsynth/releases)
2.  Download the latest release zip file for your system (e.g., `fluidsynth-2.x.x-win10-x64.zip`).
3.  Extract the contents of the zip file to `C:\tools\fluidsynth`.

**For macOS:**

Use Homebrew to install FluidSynth:

    brew install fluidsynth

**For Linux (Debian/Ubuntu):**

Use the package manager to install FluidSynth:

    sudo apt-get install fluidsynth

### 3. SoundFont

This application requires a SoundFont (`.sf2` or `.sf3`) file to generate audio.

1.  A recommended general-purpose SoundFont is "MuseScore General," which is included, or you can download it from the MuseScore website.
2.  Place your downloaded SoundFont file inside this `soundfonts` directory.
3.  Ensure the `SOUNDFONT_PATH` in `config.py` matches the name of your file (e.g., `"soundfonts/MuseScore_General.sf3"`).

## Running the Application

Once all dependencies are installed and the SoundFont is in place, you can run the application from your terminal:

    python main.py
```
