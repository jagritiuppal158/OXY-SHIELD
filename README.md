**OXY-SHIELD** is an intelligent health monitoring and early-warning system designed for soldiers operating in high-altitude or extreme environments. Its purpose is to continuously track vital signs and environmental conditions, analyze risk in real time, and alert medical or command teams before a health emergency occurs.


**Key Features**
1. Real‑time sensor data integration
2. Machine learning–based health prediction
3. Web dashboard for live monitoring
4. Alert generation and management
5. Modular Flask backend
6. Clean frontend with separate pages for admin, profile, and alerts



**Tech Stack**
_Frontend_
  HTML, CSS, JavaScript
_Backend_
  Python
  Flask
  Flask‑SocketIO
_Machine Learning_
  scikit‑learn
  NumPy

**Installation**
1. Clone the repository
git clone <your-repo-url>
cd OXY-SHIELD
2. Create virtual environment
python -m venv venv
Activate it:
Windows
venv\Scripts\activate
Linux/Mac
source venv/bin/activate
3. Install dependencies
pip install -r Backend/requirements.txt
Running the Backend
From the Backend directory:
python app.py
The Flask server will start locally.
Frontend Usage

Open index.html or serve the Frontend folder using a local server. The dashboard connects to the Flask backend for real‑time updates.


**Data Flow**
1. Sensor or wearable device sends health metrics.
2. Backend API receives and validates data.
3. ML model analyzes the input.
4. Risk score and alerts are generated.
5. Dashboard updates in real time via SocketIO.

**Machine Learning Model**
The prediction engine is implemented in health_predictor.py and uses a pre‑trained scikit‑learn model stored as ml_model.pkl.
The model is responsible for:
Feature preprocessing
Risk prediction
Alert triggering
To retrain the model, replace the pickle file and ensure feature consistency.

**Environment Variables (Recommended)**
For production, store secrets such as API keys in environment variables instead of hardcoding them.
Example:

export CLIENT_ID=your_client_id
export CLIENT_SECRET=your_client_secret

**Future Improvements**
iot sensors integration
Native mobile integration
Enhanced anomaly detection
Multi‑user support
Cloud deployment pipeline
Advanced visualization analytics



---
**Contributors**
