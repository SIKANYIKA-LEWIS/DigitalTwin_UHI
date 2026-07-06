#  Digital Twin for Urban Heat Island (UHI) Mitigation
Digital Twin for Urban Heat Island (UHI) Mitigation is my Final Year Computer Science Project, focused on the development of a digital twin platform for simulating and analyzing Urban Heat Island (UHI) effects. The system integrates geospatial data, temperature mapping, and intervention modeling to evaluate cooling strategies such as tree planting, green spaces, and green roofs, supporting data-driven decision-making in urban planning and sustainable city development.

1. LANGUAGES
   Backend:  Python 3.10+ (all logic)
   Frontend: HTML / CSS / JavaScript (served by Dash)

2. MAP DISPLAY
   deck.gl (via pydeck library) + Carto Positron basemap tiles

3. HOW TO SETUP

   ---------------------------------------------------------------
   Step 1: Install Python
   ---------------------------------------------------------------
   Go to https://www.python.org/downloads/
   Download Python 3.10 or newer.
   During installation, CHECK the box that says
   "Add Python to PATH", then click Install.

   ---------------------------------------------------------------
   Step 2: Copy the project folder
   ---------------------------------------------------------------
   Copy the "DigitalTwin_UHI" folder to your computer.
   Put it somewhere easy like D:\DigitalTwin_UHI

   ---------------------------------------------------------------
   Step 3: Open a terminal (Command Prompt)
   ---------------------------------------------------------------
   Press Windows Key + R, type "cmd", press Enter.
   In the black window, type:
      cd /d D:\DigitalTwin_UHI
   and press Enter.

   ---------------------------------------------------------------
   Step 4: Create a virtual environment
   ---------------------------------------------------------------
   Type this and press Enter:
      python -m venv .venv

   ---------------------------------------------------------------
   Step 5: Activate the environment
   ---------------------------------------------------------------
   Type this and press Enter:
      .venv\Scripts\activate
   You should see (.venv) appear at the start of the line.

   ---------------------------------------------------------------
   Step 6: Install required packages
   ---------------------------------------------------------------
   Type this and press Enter (wait 5-10 minutes):
      pip install -r requirements.txt

   ---------------------------------------------------------------
   Step 7: Start the application
   ---------------------------------------------------------------
   Type this and press Enter:
      python main.py
   Wait until you see: Dash is running on http://127.0.0.1:8050

   ---------------------------------------------------------------
   Step 8: Open in your browser
   ---------------------------------------------------------------
   Open Google Chrome or Microsoft Edge.
   Type this in the address bar and press Enter:
      http://127.0.0.1:8050
   The map should appear.


