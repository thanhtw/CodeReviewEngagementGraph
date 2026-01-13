# Review Graph Visualization

A comprehensive web-based platform for analyzing and visualizing peer review data in educational settings. This system uses machine learning to classify review quality and provides interactive visualizations to help educators understand student review patterns.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)

---

## ✨ Features

### 🔐 Multi-User Authentication
- Session-based login system with cookie authentication
- Per-user isolated workspace (uploads and outputs)
- Role-based access (admin/user)
- 24-hour session timeout

### 📊 Data Pipeline
- **CSV to JSON Conversion**: Automatically parse and convert raw peer review CSV data
- **Data Organization**: Structure data by homework assignments (HW1-HW7)
- **ML Inference**: 3-label classification using BERT model
  - **Relevance**: Is the feedback relevant to the submission?
  - **Concreteness**: Is the feedback specific and detailed?
  - **Constructiveness**: Does the feedback provide actionable suggestions?

### 📈 Visualization Dashboard
- **Interactive Network Graph**: Visualize reviewer-author relationships using vis.js
- **Quality Analysis Charts**: Bar charts, pie charts, and distribution plots
- **Per-Homework Breakdown**: View statistics for each assignment
- **Student Detail Modal**: Click on any student to see their review patterns

### 📉 Score-Review Correlation Analysis
- Correlation between homework scores and review activity
- Statistical analysis (mean, median, standard deviation)
- Quality metrics visualization
- Student performance comparison

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Browser                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐│
│  │  Login  │  │Pipeline │  │  Graph  │  │Score Correlation││
│  │  Page   │  │   UI    │  │  View   │  │    Analysis     ││
│  └─────────┘  └─────────┘  └─────────┘  └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Python HTTP Server                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Multi-threaded Request Handler           │  │
│  │  • Session Management  • File Upload  • API Routes   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Processing Pipeline                       │
│                                                              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────┐ │
│  │  CSV    │ → │  JSON   │ → │Organized│ → │ ML Labeled  │ │
│  │ Upload  │   │Convert  │   │  Data   │   │   Output    │ │
│  └─────────┘   └─────────┘   └─────────┘   └─────────────┘ │
│                                                   │         │
│                              ┌────────────────────┘         │
│                              ▼                              │
│                    ┌─────────────────┐                      │
│                    │  Score-Review   │                      │
│                    │   Analysis      │                      │
│                    └─────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Node.js (optional, for development)

### Step 1: Clone the Repository

```bash
git clone https://github.com/thanhtw/ReviewGraphVisualization.git
cd ReviewGraphVisualization
```

### Step 2: Install Python Dependencies

```bash
pip install torch transformers pandas numpy scikit-learn
```

### Step 3: (Optional) Install Node.js Dependencies

```bash
npm install
```

### Step 4: Configure Users

Edit `pipeline/users.json` to add or modify user accounts:

```json
{
  "users": [
    {
      "id": "user1",
      "username": "student1",
      "password": "student123",
      "name": "Student Name",
      "role": "user"
    }
  ]
}
```

### Step 5: (Optional) Add Score Data

Place your score CSV file in `pipeline/score/Score-By-HW.csv` with format:

```csv
ID,Name,Pre,Midterm,Final,HW1,HW2,HW3,HW4,HW5,HW6,HW7
S001,John Doe,85,90,88,95,92,88,90,85,88,92
```

---

## 📖 Usage

### Starting the Server

```bash
cd pipeline
python server.py
```

The server will start on port **8002** by default.

### Accessing the System

Open your browser and navigate to:

| Page | URL | Description |
|------|-----|-------------|
| Login | `http://localhost:8002/login` | User authentication |
| Pipeline | `http://localhost:8002/` | Main data processing interface |
| Graph View | `http://localhost:8002/graph` | Interactive visualization |
| Score Analysis | `http://localhost:8002/correlation` | Score-review correlation |

### Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| student1 | student123 | User |
| student2 | student123 | User |

### Running the Pipeline

1. **Login** to the system
2. **Upload** your CSV file (drag & drop or click to browse)
3. **Configure** homework range (HW1-HW7)
4. **Enable/Disable** ML inference (requires BERT model)
5. Click **Run Pipeline**
6. View results in **Graph Visualization** or **Score Analysis**

### CSV Input Format

Your input CSV should have these columns:

```csv
Author,Reviewer,Feedback,Time,Assignment,Round
John Doe,Jane Smith,"Good work on the implementation",2024-01-15,HW1,1
```

---

## 📁 Project Structure

```
ReviewGraphVisualization/
├── models/
│   └── bert_3label_finetuned_model/    # Pre-trained BERT model
├── pipeline/
│   ├── server.py                       # Main HTTP server
│   ├── csv_converter.py                # CSV to JSON conversion
│   ├── data_organizer.py               # Data organization by HW
│   ├── ml_inference.py                 # ML labeling module
│   ├── score_review_analysis.py        # Score correlation analysis
│   ├── index.html                      # Pipeline UI
│   ├── login.html                      # Login page
│   ├── graph.html                      # Visualization dashboard
│   ├── score_review_correlation.html   # Score analysis page
│   ├── users.json                      # User credentials
│   ├── uploads/                        # Per-user uploaded files
│   │   └── {user_id}/
│   ├── output/                         # Per-user output files
│   │   └── {user_id}/
│   ├── score/                          # Score data directory
│   └── static/                         # Static assets (JS, CSS)
├── package.json
└── README.md
```

---

## 🔌 API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/login` | POST | User login |
| `/api/logout` | GET | User logout |
| `/api/check-session` | GET | Verify session |
| `/api/user-info` | GET | Get current user info |

### Pipeline

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload CSV file |
| `/run` | POST | Start pipeline execution |
| `/status` | GET | Get pipeline status |
| `/result` | GET | Get final result JSON |
| `/api/run-analysis` | GET | Run score-review analysis |

### Static Files

| Endpoint | Description |
|----------|-------------|
| `/static/{file}` | Static assets |
| `/output/{file}` | User's output files |
| `/function/{file}` | Function data files |

---

## ⚙️ Configuration

### Server Configuration

Edit `server.py` to modify:

```python
SESSION_TIMEOUT = 86400  # Session timeout in seconds (default: 24 hours)
port = 8002              # Server port
```

### Running on Public IP

The server binds to all interfaces (`0.0.0.0`) by default. To make it accessible:

1. Open firewall port:
   ```bash
   sudo ufw allow 8002/tcp
   ```

2. Access via your IP:
   ```
   http://YOUR_IP:8002
   ```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Authors

- **Thomas** - *Initial work and development*

---

## 🙏 Acknowledgments

- [vis.js](https://visjs.org/) - Network visualization library
- [Chart.js](https://www.chartjs.org/) - Chart visualization
- [Hugging Face Transformers](https://huggingface.co/transformers/) - BERT model support
