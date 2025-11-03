# MEG BIDS Conversion Documentation

## Overview
Converting audio-visual-motor dataset to BIDS format following official MEG documentation.

## Key Documentation References
- **BIDS MEG Specification**: https://bids-specification.readthedocs.io/en/stable/modality-specific-files/magnetoencephalography.html
- **BIDS Validator (Online)**: https://bids-standard.github.io/bids-validator/
- **Reference Dataset**: https://openneuro.org/datasets/ds006334/versions/1.0.0

## Progress Made

### 1. BIDS Structure Implementation
- ✅ Converted audio-visual-motor dataset to BIDS format
- ✅ Created proper directory structure with subject/session organization
- ✅ Implemented correct file naming conventions

### 2. Required vs Optional Files
- **Required**: `*_meg.json` for each run ✅
- **Optional but recommended**: `*_channels.tsv` and `*_events.tsv` 
  - BIDS validation passes without these files
  - Decision needed: include based on task requirements

### 3. Marker File Handling (KIT/Yokogawa Systems)
- **Issue**: Multiple marker files per session require special handling
- **Solution**: Use `acq` entity instead of `run` entity
  - ✅ `*_acq-run1_markers.mrk`
  - ✅ `*_acq-run2_markers.mrk` 
  - ✅ `*_acq-run3_markers.mrk`
- **Reason**: BIDS specification does not allow `run` entity for marker files

### 4. Validation Setup
- ✅ **Online validation** at https://bids-standard.github.io/bids-validator/
- ✅ **Local validation** via npm:
  ```bash
  npm install -g bids-validator
  bids-validator "path/to/bids/folder"
  ```
- ✅ **Reference validation**: Downloaded and validated ds006334 dataset (passed with warnings only)

### 5. Project Organization
- **Source files**: Analysis scripts (.m, .py) can be stored in `project/sourcedata/` directory
- **Data structure**: Following BIDS hierarchy for MEG data

## Current Issues

### 1. 🔴 Headshape File Extension Validation Error
- **Problem**: Validator reports extension mismatch for `.txt` headshape files
- **Context**: Using KIT/Yokogawa system with `coordsystem.json` correctly specifying `"KitYokogawa"`
- **BIDS Specification**: Explicitly allows `.txt` files for KIT/Yokogawa systems
- **Status**: Appears to be a validator bug rather than BIDS compliance issue

### 2. 🟡 File Format Questions
- **`.fsn` headshape file**: Need to determine proper handling/conversion
- **Channels/Events TSV**: Need to decide inclusion based on task requirements

### 3. 🟡 Metadata Completion
- JSON placeholder values need to be filled with actual metadata
- README file needs project-specific content

## Next Steps

### Immediate
1. **Resolve validator issue**: 
   - Report headshape validation bug to BIDS community
   - Consider temporary workaround using `.pos` extension if needed
2. **Complete metadata**: Fill in JSON placeholders and README content
3. **Handle .fsn file**: Determine conversion/inclusion strategy

### Planning
1. **Standardize process**: Apply lessons learned to remaining 19 projects
2. **Documentation**: Create conversion workflow documentation
3. **Quality assurance**: Establish validation checklist for future conversions

## Questions for Resolution

1. **Channel/Events TSV files**: 
   - Do we have corresponding data for all `.con` files?
   - Should inclusion depend on specific task requirements?

2. **Headshape files**: 
   - How to handle `.fsn` format files in BIDS context?
   - Confirm validation workaround strategy

3. **Metadata completion**: 
   - What specific values should replace JSON placeholders?
   - What project details should be included in README?