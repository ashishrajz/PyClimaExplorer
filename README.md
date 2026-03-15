# 🌍 PyClimaExplorer
VIDEO URL: https://drive.google.com/file/d/1QoZES8aqwggcRaD0H9gzbt-cMOMzoeYP/view?usp=drivesdk


PyClimaExplorer is an interactive climate data visualization platform built using **Streamlit, Xarray, and Plotly**.  
It allows users to explore large **NetCDF climate datasets** through interactive maps, temporal analysis, dataset comparison, and AI-generated climate insights.

The goal of this project is to make complex climate datasets easier to understand through intuitive and interactive visualizations.

---

# 🚀 Features

### 🌍 Global Spatial Visualization
- Interactive **2D heatmap** visualization of global climate variables
- **3D globe visualization** for spatial exploration
- Click any location on the map to analyze climate patterns

### 📈 Temporal Climate Analysis
- View time-series graphs for selected geographic locations
- Identify climate trends over time

### ⚔️ Dataset Comparison
- Compare two climate datasets side by side
- Analyze changes across time periods or variables

### 🧠 AI Story Mode
- Generates AI-based climate insights for selected locations
- Uses an external API to generate climate narratives

### 📂 Dataset Explorer
- Load and explore NetCDF datasets
- Preview dataset variables before deeper analysis

---

# 📁 Project Structure

pyclimaexplorer/
│
├── app.py # Main application entry point
│
├── pages/
│ ├── 1_Dataset_Explorer.py
│ ├── 2_Spatial_Map.py
│ ├── 3_Temporal_Analysis.py
│ ├── 4_Comparison_Mode.py
│ └── 5_Story_Mode.py
│
├── utils/
│ └── load_data.py # Dataset loading utilities
│
├── data/ # Sample datasets (not included in repo due to size)
│
├── landing.html # Custom landing page UI
│
├── requirements.txt # Python dependencies
│
├── presentation.pptx # PPT submitted for the hackathon
│
├── demo_video.mp4 # Demo video of the project
│
└── README.md


---

# ⚙️ Installation

### 1️⃣ Clone the Repository

git clone https://github.com/<your-username>/pyclimaexplorer.git
cd pyclimaexplorer


---

### 2️⃣ Install Dependencies

pip install -r requirements.txt


---

### 3️⃣ Run the Application

streamlit run app.py


The app will start locally at:

http://localhost:8501


---

# 📊 Sample Dataset

The application works with **NetCDF (.nc) climate datasets**.

Due to GitHub file size limits, large datasets are **not included in the repository**.

You can download sample datasets from:

**Copernicus Climate Data Store (ERA5)**  
https://cds.climate.copernicus.eu

Recommended variables:
- 2m Temperature (`t2m`)
- Total Precipitation (`tp`)
- Wind components (`u10`, `v10`)

After downloading, place the files inside the `data/` directory.

Example:

data/
monthly_temperature.nc
monthly_precipitation.nc
daily_temperature.nc


You can also upload your own NetCDF datasets directly using the **Upload Custom Dataset** option in the app.

---

# 📦 Dependencies

Main libraries used in this project:

- Streamlit
- Xarray
- Plotly
- NumPy
- Pandas
- streamlit-plotly-events

All dependencies are listed in **requirements.txt**.

---

# 🎥 Demo Video

The repository includes a **demo video showing the implementation and functionality of the project**.
https://drive.google.com/file/d/1QoZES8aqwggcRaD0H9gzbt-cMOMzoeYP/view?usp=drivesdk


The demo demonstrates:
- Dataset loading
- Global climate visualization
- Temporal analysis
- Dataset comparison
- AI Story Mode

---

# 📊 Presentation

The PowerPoint presentation submitted for the hackathon is included in the repository:

[presentation.pptx](https://drive.google.com/file/d/14HHw69umZMJGPFyjNsi2kYL-KenfKV4-/view?usp=drivesdk)


---

# 🛠 Technologies Used

- **Python**
- **Streamlit**
- **Xarray**
- **Plotly**
- **NumPy**
- **Pandas**

---

# 👥 Team

Team Spartans  
HaXplore – CodeFest / Technex  
IIT (BHU) Varanasi

---

# 📌 Future Improvements

- Support for larger datasets via cloud storage
- Faster rendering for high-resolution climate data
- More climate variables and datasets
- Improved AI climate insights

---
