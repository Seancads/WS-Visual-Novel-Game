# Echoes of Valor

A story-driven visual novel about brotherhood, sacrifice, and the choices that define us.  
Built with **Python** and **Pygame**.

---

## 📖 Overview

*Echoes of Valor* places you in the boots of a young recruit leaving home to join the military. Navigate emotional goodbyes, brutal training, and life-or-death decisions that shape your journey and relationships. Your choices matter – each one can lead to success, failure, or a new understanding of what it means to fight for something bigger.

The game features multiple chapters, star ratings based on performance, and a persistent save system that unlocks content as you improve.

---

## ✨ Features

- **Branching narrative** – your decisions directly affect the story flow and character reactions
- **Star rating system** – earn up to 3 stars per chapter based on how many mistakes you make
- **Persistent progress** – saves your best scores and unlocks subsequent chapters
- **Pause menu** – resume, return to main menu, or take a break
- **Original art & sound** – hand‑crafted character portraits, backgrounds, and atmospheric audio
- **Replayability** – try different choices to achieve perfect scores and unlock everything

---

## 🕹️ Controls

| Action              | Input                     |
|---------------------|---------------------------|
| Advance dialogue    | Left click or `Enter`     |
| Select choice       | Click the corresponding button |
| Pause / Resume      | Click the pause icon (top‑right) |
| Navigate menus      | Mouse                     |

---

## 📂 Project Structure

EchoesOfValor/
├── game/                           # Main Python application
│   ├── res                         
│   │   ├── main.py                 # Entry point & scene manager
│   │   ├── gameplay.py             # Core gameplay loop (dialogue, choices, portraits)
│   │   ├── menus.py                # Main menu, chapter select, level select
│   │   ├── save.py                 # Save/load game progress
│   │   ├── audio.py                # Music & sound effects
│   │   ├── theme.py                # Colours, fonts, layout constants
│   │   ├── config.json             # Story data (chapters, scenarios, dialogues)
│   │   └── assets/
│   │       ├── images/             # Character portraits, backgrounds, UI icons
│   │       └── sounds/             # Music tracks and sound effects
│   └── dist
│       └── Echoes Of Valor.exe
├── web/                            # (optional) Web version placeholder
│   ├── css/
│   ├── js/
│   └── img/
└── index.html

The entire story, including dialogue, choices, and branching logic, is defined in `config.json`. You can extend the game by adding new chapters, characters, or scenarios directly to this file.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **Pygame 2.1+** (for graphics and audio)

### Installation

1. **Clone the repository** (or download and extract the source):
   ```bash
   git clone https://github.com/yourusername/echoes-of-valor.git
   cd echoes-of-valor
   

2. *Install dependencies*:
   
   pip install pygame
   

3. *Run the game*:
   
   cd game
   python main.py
   

   (You can also run python game/main.py from the project root if Python’s path allows.)

### Optional: Virtual Environment

python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
pip install pygame
python game/main.py

---

## 🎮 How to Play

1. Launch the game → you’ll see the *Main Menu*.
2. Click *PLAY* to enter the *Chapter Select* screen.
3. Choose an unlocked chapter (chapters unlock when you earn enough stars in previous ones).
4. In a chapter, read the dialogue and click or press Enter to advance.
5. When a choice appears, click the button for your decision:
   - *Correct* choices move the story forward and contribute to your star rating.
   - *Incorrect* choices may show a brief failure, after which you can try again.
6. Complete all scenarios in the chapter to see your *star rating* and overall attempts.
7. Return to the chapter select to replay for a better score or continue to the next unlocked chapter.

---

## 📊 Saving & Progress

Your progress is automatically saved in save.json (located in the game/ folder). The file records:

- Which chapters you’ve completed and your best star rating + attempts
- Which chapter is currently unlocked

You can reset progress by deleting save.json.

---

## 🎨 Customisation

- *Colours & Fonts*: adjust values in theme.py
- *Story content*: edit config.json (chapters, characters, scenarios, choices)
- *Assets*: replace images in assets/images/ and sounds in assets/sounds/ (keep the same filenames or update the config accordingly)

## 🎵 Credits

- *Story, Design & Programming* – Devisean, Saemeow
- *Art* – Devisean
- *Website* - Saemeow
- *Built with* [Pygame](https://www.pygame.org/)

If you’d like to contribute, report issues, or suggest improvements, feel free to open an issue or pull request!

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details (if included).  
Feel free to add your own license.