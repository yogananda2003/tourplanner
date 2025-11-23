🌎 Multi-Agent Tourism Planner

A robust AI-powered tourism planner that uses multiple "Agents" to fetch real-time weather, locations, and tourist attractions.

🚀 How It Works

This project uses a Python Backend (Flask) to handle logic and an HTML/JS Frontend for the user interface.

Weather Agent: Fetches live data from Open-Meteo API.

Places Agent: Finds attractions using Overpass/OpenStreetMap API.

Orchestrator: Coordinates the agents and formats the output.

⚠️ Important Note for GitHub Users

This project requires a Python backend to run. If you are viewing the HTML file directly on GitHub or GitHub Pages, the "Plan Trip" button will not work because the Python server is not active. You must run the server locally or deploy it to a cloud provider (like Render/Railway).

🛠️ Installation & Setup (Local)

Clone the repository

git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
cd YOUR-REPO-NAME


Install Dependencies
Make sure you have Python installed. Then run:

pip install -r requirements.txt


Run the Application

python app.py


Open the App
The terminal will show a local URL (usually http://127.0.0.1:5000). Open that link in your browser.

📂 Project Structure

app.py: The Flask server (Backend).

tourism_system4.py: The logic for the AI Agents.

templates/index.html: The User Interface.

requirements.txt: List of Python libraries.

🤖 Agents Detail

Weather Agent: Checks current temperature and rain probability.

Attraction Agent: Searches for parks, museums, and historical sites within a 10km radius.

Location Agent: Converts city names to latitude/longitude coordinates.
