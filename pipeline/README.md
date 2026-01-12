# Review Graph Data Pipeline

A standalone pipeline for processing peer review CSV data and generating visualization-ready JSON.

## Quick Start

```bash
# Start the pipeline server
python server.py

# Open in browser
# http://localhost:8002
```

## Pipeline Steps

```
CSV File → JSON Records → Organized by HW → ML Labels → Graph Visualization
```

### Step 1: CSV to JSON (`csv_converter.py`)
Converts raw CSV data to JSON format with proper field mapping.

**Input CSV Columns:**
- `Owner_name` - Author/Student name
- `Reviewer_name` - Reviewer name  
- `feedback` - Review text
- `Time` - Submission timestamp
- `Assignment` - HW1, HW2, etc.
- `Metrics` - Metric ID
- `PMetric` - Category ID
- `Round` - Review round number

### Step 2: Data Organization (`data_organizer.py`)
Groups records by assignment and author-reviewer pairs.

### Step 3: ML Inference (`ml_inference.py`)
Adds 3-label predictions:
- **Relevance** - Is feedback related to the code?
- **Concreteness** - Is feedback specific?
- **Constructive** - Does feedback provide suggestions?

## Files

```
pipeline/
├── server.py          # Main server with web interface
├── index.html         # Upload & run interface
├── csv_converter.py   # Step 1: CSV → JSON
├── data_organizer.py  # Step 2: Organize data
├── ml_inference.py    # Step 3: ML labeling
├── uploads/           # Uploaded CSV files
└── output/            # Generated JSON files
```

## Usage

### Web Interface
1. Start server: `python server.py`
2. Open http://localhost:8002
3. Upload CSV file
4. Configure options (HW range, ML model)
5. Click "Start Pipeline"
6. View graph when complete

### Command Line

```bash
# Step 1: Convert CSV to JSON
python csv_converter.py input.csv step1.json

# Step 2: Organize data
python data_organizer.py step1.json step2.json 1 7

# Step 3: Add ML labels
python ml_inference.py step2.json final.json
```

## Output

The final JSON file is automatically copied to:
- `pipeline/output/final_result.json`
- `function/3labeled_processed_totalData.json` (for graph.html)

## Ports

- Pipeline Server: `http://localhost:8002`
- Graph Visualization: `http://localhost:8002/static/graph.html`
