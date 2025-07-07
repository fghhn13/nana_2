# Nana 2

Nana 2 is a small desktop assistant built with `tkinter`.  
It uses OpenAI's API via DashScope for natural language command recognition and provides a plugin system for extending its skills.

## Setup

1. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure API key**:
   Create a `.env` file in the project root containing:
   ```env
   DASHSCOPE_API_KEY=your_openai_key
   ```
4. **Run the application**:
   ```bash
   python nana_2/main.py
   ```

The GUI will launch and connect to the AI service.  Plugins are loaded from the `nana_2/plugins` directory.
