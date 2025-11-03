# MEG-to-BIDS Converter Test Scenarios Guide

## Overview

This guide explains the comprehensive test suite for testing the `meg_to_bids.py` script across all possible scenarios.

## 🧪 Test Scenarios

### **Scenario 1: Brand New Project**
**Purpose:** Test creating a completely new BIDS project from scratch.

**Input Structure:**
```
test_data/scenario_1_new_project/audio-visual-session1/
├── 241201-1.con          # MEG data file 1
├── 241201-2.con          # MEG data file 2
├── 241201-1.mrk          # Marker file 1  
├── 241201-2.mrk          # Marker file 2
├── basic-surface.txt     # Headshape - basic surface
├── stylus-points.txt     # Headshape - stylus points
├── laser-scan.fsn        # Laser scan file
└── head-position.pos     # Head position file
```

**Test Command:**
```bash
python meg_to_bids.py test_data/scenario_1_new_project/audio-visual-session1 test_output/scenario_1 --project new-audio-visual --validate
```

**Expected Output:**
- Creates new BIDS project structure
- Generates all required BIDS files (`dataset_description.json`, `participants.tsv`, etc.)
- Creates `sub-001/ses-001/meg/` with properly named files
- Subject ID: `001`, Session ID: `001`

---

### **Scenario 2: Existing BIDS Project, New Subject**
**Purpose:** Test adding a new subject to an existing BIDS-compliant project.

**Input Structure:**
```
test_data/scenario_2_existing_project/
├── existing-bids-project/        # Pre-existing BIDS project
│   ├── dataset_description.json  # Already exists
│   ├── participants.tsv          # Contains sub-002
│   ├── participants.json
│   ├── README
│   └── CHANGES
└── new-subject-session/          # New session data
    ├── 241202-1.con
    ├── 241202-1.mrk
    ├── head-surface.txt
    └── digitized-points.txt
```

**Test Command:**
```bash
python meg_to_bids.py test_data/scenario_2_existing_project/new-subject-session test_data/scenario_2_existing_project --project existing-bids-project --subject 003
```

**Expected Output:**
- Detects existing BIDS structure
- Adds `sub-003` to `participants.tsv`
- Creates `sub-003/ses-001/meg/` in existing project
- Preserves existing subjects

---

### **Scenario 3: Existing Subject, New Session**
**Purpose:** Test adding a new session to an existing subject.

**Input Structure:**
```
test_data/scenario_3_existing_subject/
├── multi-session-project/        # Project with existing subject
│   ├── dataset_description.json
│   ├── participants.tsv          # Contains sub-001, sub-002
│   └── sub-001/
│       └── ses-001/              # Existing session
│           └── meg/
│               ├── sub-001_ses-001_task-existing_run-01_meg.con
│               └── sub-001_ses-001_task-existing_markers.mrk
└── sub-001-session2/             # New session data for sub-001
    ├── 241203-1.con
    ├── 241203-2.con
    ├── 241203-3.con              # 3 runs this time
    ├── 241203-1.mrk
    ├── 241203-2.mrk
    ├── 241203-3.mrk
    └── surface-scan.txt
```

**Test Command:**
```bash
python meg_to_bids.py test_data/scenario_3_existing_subject/sub-001-session2 test_data/scenario_3_existing_subject --project multi-session-project --subject 001
```

**Expected Output:**
- Detects existing subject `sub-001`
- Auto-generates next session ID: `ses-002`
- Creates `sub-001/ses-002/meg/` alongside existing `ses-001`
- Preserves existing session data

---

### **Scenario 4: Multiple Sessions**
**Purpose:** Test processing multiple session folders at once.

**Input Structure:**
```
test_data/scenario_4_multiple_sessions/
├── motor-task-session1/
│   ├── motor-1.con
│   ├── motor-1.mrk
│   └── head-basic.txt
├── visual-task-session2/
│   ├── visual-1.con
│   ├── visual-2.con
│   ├── visual-1.mrk
│   ├── visual-2.mrk
│   ├── head-stylus.txt
│   └── head-pos.pos
└── auditory-task-session3/
    ├── aud-241204.con
    ├── aud-241204.mrk
    ├── digitized-head.txt
    └── laser-points.fsn
```

**Test Command:**
```bash
python meg_to_bids.py "test_data/scenario_4_multiple_sessions/*" test_output/scenario_4 --project multi-session-study
```

**Expected Output:**
- Processes all 3 sessions sequentially
- Creates `sub-001/ses-001`, `sub-001/ses-002`, `sub-001/ses-003`
- Auto-increments session numbers
- Runs validation on complete dataset

---

### **Scenario 5: Edge Cases**
**Purpose:** Test unusual file patterns and edge cases.

#### **Edge Case 1: Only MEG File**
```
test_data/scenario_5_edge_cases/only-meg-data/
└── solo-recording.con             # No markers or headshape
```

#### **Edge Case 2: Unusual Naming**
```
test_data/scenario_5_edge_cases/unusual-naming/
├── MEG_RUN_001.con
├── MARKERS_001.mrk
├── HEAD_SHAPE_BASIC.txt
└── HEAD_SHAPE_DETAILED.txt
```

#### **Edge Case 3: Mixed Extensions**
```
test_data/scenario_5_edge_cases/mixed-extensions/
├── data.con
├── events.mrk
├── shape.txt
├── position.pos
└── head.mat
```

#### **Edge Case 4: Explicit Subject ID**
```
test_data/scenario_5_edge_cases/sub-005_explicit-subject/
├── recording.con
└── markers.mrk
```

**Expected Outputs:**
- Handles missing files gracefully
- Processes unusual naming patterns
- Extracts subject ID from folder name when available
- Creates valid BIDS structure regardless of input quirks

---

## 🚀 Running the Tests

### **1. Generate Test Data**
```bash
python create_test_data.py
```

### **2. Run Individual Tests**
```bash
# Test new project
python meg_to_bids.py test_data/scenario_1_new_project/audio-visual-session1 test_output/scenario_1 --project new-audio-visual

# Test existing project  
python meg_to_bids.py test_data/scenario_2_existing_project/new-subject-session test_data/scenario_2_existing_project --project existing-bids-project --subject 003

# Test multiple sessions
python meg_to_bids.py "test_data/scenario_4_multiple_sessions/*" test_output/scenario_4 --project multi-session-study
```

### **3. Run All Tests**
```bash
cd test_data
python run_all_tests.py
```

---

## 📊 What Each Test Validates

| Scenario | Tests | Expected Behavior |
|----------|-------|------------------|
| **1** | New project creation | Creates all BIDS files from scratch |
| **2** | Existing project detection | Preserves existing structure, adds new subject |
| **3** | Session auto-increment | Correctly numbers new sessions |
| **4** | Batch processing | Handles multiple folders systematically |
| **5a** | Missing files | Graceful handling of minimal data |
| **5b** | Naming variations | Robust file pattern recognition |
| **5c** | Mixed formats | Handles various file extensions |
| **5d** | Subject ID extraction | Parses subject IDs from folder names |

---

## 🎯 Success Criteria

**Each test should:**
1. ✅ Complete without errors
2. ✅ Create valid BIDS directory structure
3. ✅ Generate proper file names following BIDS conventions
4. ✅ Create required metadata files
5. ✅ Pass BIDS validation (where applicable)
6. ✅ Log appropriate information

**The complete test suite should:**
- 🎯 Achieve 100% pass rate
- 🎯 Cover all decision tree branches
- 🎯 Handle edge cases gracefully
- 🎯 Produce BIDS-compliant outputs 