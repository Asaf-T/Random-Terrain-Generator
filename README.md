# Random-Terrain-Generator
An interactive, multi-layered 3D map generation tool engineered in Python. The application relies on multi-octave Perlin Noise algorithms to map temperature, humidity, and height constraints dynamically, culminating in realistic biome distribution patterns in real time. 

![Application Demo](demo.gif)

## 🚀 Key Architectural Features
* **Multi-Octave Noise Synthesis:** Simulates structural landscapes by cross-referencing four distinct perlin noise layers (temperature, humidity, primary height, and secondary height arrays).
* **Dynamic Biome Mapping:** Utilises dual-axis distribution boundaries to seamlessly partition environments into custom biomes (Water, Grass, Dark Grass, Sand, Stone, and Snow).
* **On-Demand Chunk Generation:** Features real-time spatial expansions, updating underlying terrain arrays directly based on user coordinate interactions.
* **3D Geometry Exportation:** Built-in asynchronous export sequence capable of translating 2D data metrics directly into standard 3D wavefront object formats (`.obj`).

## 📦 Prerequisites
Ensure you have the following installed on your host system:
* **Python 3.8+**
* An active package manager tool (`pip`)

## 🛠️ Installation & Environment Setup
To clone and run this simulation engine locally, execute the following commands in your command line terminal:

1. **Clone the project repository:**
   ```bash
   git clone https://github.com
   cd YOUR_REPOSITORY_NAME
   ```

2. **Initialize dependencies:**
   Install the required functional ecosystem libraries directly from the workspace manifest layout:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Execution & Interactive Controls
Launch the simulation workspace with the primary Python processor:
```bash
python main.py
```

### Active Input Mapping
* `Left-Click + Drag` — Pan across the infinite landscape canvas.
* `Scroll Wheel (Up / Down)` — Zoom the layout display transformation matrix dynamically.
* `G` — Toggle runtime target generation mode (Click on unmapped areas to generate real-time local land chunks).
* `C` — Initialize multi-pass wavefront file sequence (`.obj` format saver).
* `X` — Terminate and break the current background map generation export workflow.
* `ESC` — Safe application disposal and system terminal teardown thread hook.
