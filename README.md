# InfluenceOpt 🚀

**Advanced Influencer Campaign Optimization Platform**

InfluenceOpt is a desktop application that helps brand managers identify the optimal set of influencers to maximize campaign reach while respecting budget, risk, and quality constraints. Built on advanced operations research techniques (Mixed-Integer Linear Programming), it provides an intuitive interface for complex marketing optimization problems.

![InfluenceOpt Screenshot](plateform.jpg)

##   Key Features

###  Intelligent Optimization
- **Mixed-Integer Programming**: Leverages Gurobi (or greedy fallback) to solve complex constrained optimization problems
- **Multi-Objective Optimization**: Balance cost minimization with reach maximization
- **Real-time Validation**: Constraint validation with visual feedback as you adjust parameters

###  Interactive Network Visualization
- **Platform-Coded Nodes**: Visual distinction between Instagram, TikTok, YouTube, and Twitter
- **Risk Indicators**: Color-coded borders showing influencer risk levels
- **Hover Tooltips**: Detailed metrics on followers, cost, engagement, and fake percentage
- **Drag & Drop**: Manually rearrange network layout
- **Zoom & Pan**: Smooth navigation through large networks
- **Multiple Layout Algorithms**: Spring, circular, Kamada-Kawai, and community detection

###  Comprehensive Constraint Management
- **Budget Control**: Set maximum campaign spend with real-time tracking
- **Risk Management**: Filter by risk level with topic-specific thresholds
- **Coverage Targets**: Ensure minimum audience reach percentage
- **Platform Distribution**: Specify min/max percentages per platform
- **Quality Filters**: Exclude high-fake influencers automatically
- **Demographics**: Target specific age groups, regions, and genders

###  Advanced Analytics
- **Monte Carlo Robustness**: 100-trial simulations testing edge probability variations
- **ROI Estimation**: Calculate monetary return based on conversion values
- **Reach Propagation**: Visualize cascading effects through follower networks
- **Scenario Comparison**: Radar charts comparing multiple campaign strategies

###  Session & Scenario Management
- **Named Sessions**: Save and reload complete campaign configurations
- **Auto-save**: Versioned auto-save every 30 seconds (keeps last 10 versions)
- **Scenario Library**: Save multiple optimization results for comparison
- **Export Options**: CSV lists, PowerPoint briefs with screenshots

###  Modern UI/UX
- **Dark/Light Themes**: Toggle between professional dark mode and clean light mode
- **Visual Status Indicators**: Real-time status lights for constraints
- **Metric Dashboard**: Large, clear displays for cost, reach, and ROI
- **Responsive Layout**: Resizable panels and dockable constraint editor
- **Keyboard Shortcuts**: Power-user accelerators for common tasks

---

##  Quick Start

### Prerequisites
- Python 3.8 or higher
- PyQt5
- NetworkX
- (Optional) Gurobi with valid license for optimal solutions

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/influenceopt.git
cd influenceopt

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python main.py
```

### First Steps

1. **Load Demo Dataset**: Click "Load Demo" in the toolbar
2. **Explore the Network**: Use mouse wheel to zoom, drag to pan
3. **Set Constraints**: Adjust budget, risk, and coverage in left panel
4. **Optimize**: Click "Optimize" to find best influencer set
5. **Review Results**: Check highlighted influencers and metrics
6. **Save Scenario**: Click "Save Scenario" to preserve this configuration

---

##  User Guide

### Network View

The main canvas displays your influencer network:

**Node Colors** (Platform):
- 🟣 **Instagram** (IG): Pink/Purple gradient
- ⚫ **TikTok** (TT): Black gradient
- 🔴 **YouTube** (YT): Red gradient
- 🔵 **Twitter** (TW): Blue gradient

**Node Borders** (Risk Level):
- 🟢 **Green**: Low risk (< 10%)
- 🟡 **Yellow**: Medium risk (10-20%)
- 🔴 **Red**: High risk (20-30%)
- 🔴 **Dark Red**: Critical risk (> 30%)

**Node Size**: Proportional to follower count (logarithmic scale)

**Edge Colors** (Connection Strength):
- 🟢 **Green**: High probability (> 70%)
- 🟡 **Yellow**: Medium probability (40-70%)
- 🔴 **Red**: Low probability (< 40%)

**Interactive Features**:
- **Hover**: View detailed metrics in tooltip
- **Right-click**: Edit node properties
- **Drag**: Reposition nodes manually
- **Scroll**: Zoom in/out
- **Middle-drag**: Pan the view

### Constraint Panel

#### Budget & Reach
- Set maximum campaign budget
- Progress bar shows budget utilization
- Turns red if exceeded

#### Risk Management
- Select campaign topic (General, Sensitive, Health, Politics)
- Set maximum acceptable risk percentage
- Real-time status indicator

#### Target Audience
- Demographic filters: Age groups, regions, gender
- Coverage percentage slider (50-100%)
- Tree view for easy selection

#### Platforms
- Checkboxes to include/exclude platforms
- Min/Max percentage distribution controls
- Ensures balanced platform representation

#### ROI Estimation
- Set conversion value per engagement
- Displays expected monetary return
- Large metric displays for Cost, Reach, and ROI

### Optimization

The optimization model solves:

```
Minimize: Σ cost_i · x_i - λ · Σ z_f

Subject to:
  Σ cost_i · x_i ≤ Budget
  Σ risk_i · x_i ≤ RiskMax
  z_f ≤ Σ_{i∈N(f)} x_i  (reach constraint)
  Σ z_f ≥ Coverage% · |V|
  Platform min/max bounds
  x_i ∈ {0,1}, z_f ∈ {0,1}
```

Where:
- `x_i`: Binary selection variable for influencer i
- `z_f`: Binary variable indicating follower f is reached
- `λ`: Reach weight parameter (from coverage slider)

**Solution Methods**:
1. **Gurobi**: Optimal MILP solution (if installed)
2. **Greedy Fallback**: Cost-effectiveness heuristic

**Runtime**: Typically 5-60 seconds depending on network size

### Scenario Management

**Saving Scenarios**:
1. Run optimization with desired constraints
2. Click "Save Scenario" in toolbar
3. Scenarios appear in "Scenarios" tab

**Comparing Scenarios**:
1. Select 2-5 scenarios in the table
2. Click "Compare (radar)"
3. View radar chart comparing Budget/Reach/Risk/ROI

**Exporting**:
- **CSV**: List of selected influencer IDs
- **PowerPoint**: Slide with screenshot and key metrics

### Session Persistence

**Auto-save**:
- Runs every 30 seconds automatically
- Keeps last 10 versions
- Restore from "Help → Restore History"

**Named Sessions**:
- Save: File → Save Session (Ctrl+S)
- Load: File → Load Session (Ctrl+O)
- Contains: Graph, constraints, all scenarios

---

##  Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New campaign |
| `Ctrl+O` | Open dataset |
| `Ctrl+S` | Save session |
| `Ctrl+Shift+S` | Save session as |
| `Ctrl+R` | Run optimization |
| `Ctrl+Q` | Quit application |
| `F1` | Show help |

---

##  Project Structure

```
InfluenceOpt/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── data/                  # Sample datasets
│   ├── demo_users.csv
│   └── demo_edges.csv
├── core/                  # Core logic
│   ├── data_models.py     # User, Edge, Campaign dataclasses
│   ├── graph_builder.py   # CSV import utilities
│   ├── optimizer.py       # MILP solver & greedy fallback
│   └── scenarios.py       # Session/scenario management
├── gui/                   # User interface
│   ├── main_window.py     # Main application window
│   ├── network_view.py    # Interactive graph canvas
│   ├── constraint_panel.py# Constraint configuration UI
│   ├── scenario_manager.py# Scenario comparison UI
│   ├── solve_worker.py    # Background solver thread
│   └── widgets/           # Reusable UI components
│       ├── budget_slider.py
│       ├── risk_meter.py
│       ├── audience_filter.py
│       ├── multi_platform.py
│       ├── roi_label.py
│       └── coverage_dial.py
├── utils/                 # Utilities
│   ├── exporters.py       # CSV/PPTX export
│   └── settings.py        # QSettings wrapper
└── tests/                 # Unit tests
    ├── test_optimizer.py
    ├── test_scenarios.py
    └── ...
```

---

##  Configuration

### Data Format

**users.csv**:
```csv
id,name,platform,followers,cost,risk,fake,age,region,gender,eng_rate
u1,Alice,IG,12000,1500,0.05,0.02,25,NA,F,0.05
```

**edges.csv**:
```csv
source,target,weight,prob,delay_hours
u1,u3,1.0,0.9,24
```

### Gurobi Setup (Optional)

For optimal solutions, install Gurobi:

1. Download from https://www.gurobi.com/
2. Install and activate license
3. `pip install gurobipy`
4. InfluenceOpt will auto-detect and use Gurobi

Without Gurobi, the app uses a greedy heuristic solver.

---

**Author: Ferdawes Benali**