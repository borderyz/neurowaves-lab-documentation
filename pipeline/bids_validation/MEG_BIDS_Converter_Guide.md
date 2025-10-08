# MEG to BIDS Converter Guide

## Overview

This Python script converts MEG data from Yokogawa/KIT systems to BIDS (Brain Imaging Data Structure) format. It handles multiple scenarios including new projects, existing projects, and various subject/session combinations.

## Features

- ✅ **Automatic BIDS structure creation**
- ✅ **File identification and conversion**
- ✅ **Multiple session handling**
- ✅ **BIDS validation integration**
- ✅ **Flexible subject/session management**
- ✅ **Comprehensive logging**
- ✅ **Error handling and recovery**

## Installation

### Prerequisites

1. **Python 3.7+**
2. **Required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **BIDS Validator (optional but recommended):**
   ```bash
   npm install -g bids-validator
   ```

### Setup

1. Download the script files:
   - `meg_to_bids.py`
   - `requirements.txt`

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Input File Requirements

Your session folder should contain Yokogawa/KIT MEG files:

- **`.con`** - MEG data files (required)
- **`.mrk`** - Marker files 
- **`.txt`** - Headshape files
- **`.pos` or `.mat`** - Head position files

### Example Input Folder Structure
```
audio-visual-session-1/
├── session-1.con              # MEG data
├── session-1.mrk              # Markers
├── basic-surface.txt          # Headshape (basic surface)
├── stylus-points.txt          # Headshape (stylus points)
└── head-position.pos          # Head position
```

## Usage

### Basic Usage

```bash
python meg_to_bids.py <input_folder> <output_folder> [options]
```

### Examples

#### 1. Convert Single Session (New Project)
```bash
python meg_to_bids.py /path/to/meg/session /path/to/output --project audio-visual-motor
```

#### 2. Convert with Specific Subject/Session IDs
```bash
python meg_to_bids.py /path/to/meg/session /path/to/output \
    --project audio-visual-motor \
    --subject 001 \
    --session 001 \
    --task audiovisual
```

#### 3. Add New Session to Existing Subject
```bash
python meg_to_bids.py /path/to/new/session /path/to/output \
    --project audio-visual-motor \
    --subject 001
# Session ID will be auto-generated (002, 003, etc.)
```

#### 4. Convert Multiple Sessions
```bash
python meg_to_bids.py "/path/to/sessions/*" /path/to/output \
    --project audio-visual-motor
```

#### 5. Run with Validation
```bash
python meg_to_bids.py /path/to/session /path/to/output \
    --project audio-visual-motor \
    --validate
```

#### 6. Verbose Logging
```bash
python meg_to_bids.py /path/to/session /path/to/output \
    --project audio-visual-motor \
    --verbose
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `input_path` | Path to session folder (required) | - |
| `output_path` | Output directory for BIDS structure (required) | - |
| `--project` | Project name | Extracted from input folder |
| `--subject` | Subject ID | Auto-extracted or "001" |
| `--session` | Session ID | Auto-generated |
| `--task` | Task name | "task" |
| `--verbose, -v` | Enable verbose logging | False |
| `--validate` | Run BIDS validation | False |

## Decision Tree Logic

The script follows this logic for handling different scenarios:

```
New Session Input
│
├── Is it an existing project?
│   ├── Yes
│   │   ├── Is it BIDS-compliant?
│   │   │   ├── Yes
│   │   │   │   ├── Existing subject → Add new session
│   │   │   │   └── New subject → Create subject + session
│   │   │   └── No → BIDSify project, then add session
│   │   └── 
│   └── No → Create new BIDS project + subject + session
```

## Output Structure

The script creates a standard BIDS structure:

```
project-name/
├── dataset_description.json
├── participants.tsv
├── participants.json
├── README
├── CHANGES
├── validation_log.txt          # If validation run
└── sub-001/
    └── ses-001/
        └── meg/
            ├── sub-001_coordsystem.json
            ├── sub-001_ses-001_task-audiovisual_run-01_meg.con
            ├── sub-001_ses-001_task-audiovisual_run-01_meg.json
            ├── sub-001_ses-001_task-audiovisual_markers.mrk
            ├── sub-001_ses-001_acq-basicsurface_headshape.txt
            └── sub-001_ses-001_acq-styluspoints_headshape.txt
```

## File Naming Conventions

The script automatically applies BIDS naming conventions:

### MEG Data Files
- `sub-<ID>_ses-<ID>_task-<name>_run-<##>_meg.con`
- `sub-<ID>_ses-<ID>_task-<name>_run-<##>_meg.json`

### Marker Files
- Single file: `sub-<ID>_ses-<ID>_task-<name>_markers.mrk`
- Multiple files: `sub-<ID>_ses-<ID>_task-<name>_acq-<##>_markers.mrk`

### Headshape Files
- Basic surface: `sub-<ID>_ses-<ID>_acq-basicsurface_headshape.txt`
- Stylus points: `sub-<ID>_ses-<ID>_acq-styluspoints_headshape.txt`
- Generic: `sub-<ID>_ses-<ID>_acq-<##>_headshape.txt`

### Head Position Files
- `sub-<ID>_ses-<ID>_headshape.pos` (or `.mat`)

## Logging

The script provides comprehensive logging:

- **Console output** (INFO level by default, DEBUG with `--verbose`)
- **Log file** (`meg_to_bids.log`)
- **Validation log** (`validation_log.txt` in project root)

### Log Levels
- ✅ **Success messages** (green checkmarks)
- ℹ️ **Info messages** (blue info)
- ⚠️ **Warnings** (yellow warnings)
- ❌ **Errors** (red errors)

## BIDS Validation

The script can automatically run BIDS validation using the `bids-validator`:

```bash
# Install validator
npm install -g bids-validator

# Run conversion with validation
python meg_to_bids.py /path/to/session /path/to/output --validate
```

### Validation Output

- **Valid dataset**: Creates success message in validation log
- **Invalid dataset**: Details saved to `validation_log.txt`
- **Validation unavailable**: Warning message (validator not installed)

## Troubleshooting

### Common Issues

#### 1. No MEG Data Files Found
```
Error: No MEG data files (.con) found in input folder
```
**Solution**: Ensure your input folder contains `.con` files

#### 2. BIDS Validator Not Found
```
Error: bids-validator not found. Please install: npm install -g bids-validator
```
**Solution**: Install the validator or skip validation

#### 3. Permission Errors
```
Error: Permission denied when creating directory
```
**Solution**: Check write permissions for output directory

#### 4. Import Errors
```
Error: No module named 'pandas'
```
**Solution**: Install requirements: `pip install -r requirements.txt`

### Advanced Troubleshooting

#### Enable Debug Logging
```bash
python meg_to_bids.py /path/to/session /path/to/output --verbose
```

#### Check Log Files
- Review `meg_to_bids.log` for detailed processing information
- Check `validation_log.txt` for BIDS compliance issues

#### Manual BIDS Validation
```bash
bids-validator /path/to/output/project-name
```

## Best Practices

### 1. **File Organization**
- Keep related session files in the same folder
- Use descriptive folder names that include subject/session info

### 2. **Project Management**
- Use consistent project names across sessions
- Plan your subject/session numbering scheme

### 3. **Quality Control**
- Always run BIDS validation (`--validate` flag)
- Review log files for warnings or errors
- Verify output structure matches expectations

### 4. **Batch Processing**
- Use wildcards for multiple sessions: `"/path/to/sessions/*"`
- Process one project at a time to avoid confusion

## Example Workflows

### Workflow 1: Single Subject, Multiple Sessions
```bash
# Session 1
python meg_to_bids.py /data/sub001/session1 /output --project myproject --subject 001

# Session 2 (auto-increments to ses-002)
python meg_to_bids.py /data/sub001/session2 /output --project myproject --subject 001

# Session 3 (auto-increments to ses-003)
python meg_to_bids.py /data/sub001/session3 /output --project myproject --subject 001
```

### Workflow 2: Multiple Subjects, Single Sessions
```bash
# Subject 001
python meg_to_bids.py /data/sub001/session1 /output --project myproject --subject 001

# Subject 002  
python meg_to_bids.py /data/sub002/session1 /output --project myproject --subject 002

# Subject 003
python meg_to_bids.py /data/sub003/session1 /output --project myproject --subject 003
```

### Workflow 3: Batch Processing
```bash
# All sessions in one command
python meg_to_bids.py "/data/all_sessions/*" /output --project myproject --validate
```

## Testing the Script

You can test the script with your sample data:

```bash
# Test with your audio-visual-motor data
python meg_to_bids.py ./audio-visual-motor/sub-001 ./test-output \
    --project audio-visual-motor \
    --subject 001 \
    --session 001 \
    --task audiovisual \
    --validate \
    --verbose
```

This will create a test BIDS structure and validate it, providing detailed logging of the conversion process.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review log files (`meg_to_bids.log`)
3. Verify input file requirements
4. Test with verbose logging (`--verbose`)
5. Manually run BIDS validation

The script is designed to be robust and provide helpful error messages to guide you through any issues. 