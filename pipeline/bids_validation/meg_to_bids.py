#!/usr/bin/env python3
"""
MEG to BIDS Converter for Yokogawa System

This script converts MEG data from Yokogawa system to BIDS format.
Handles multiple scenarios: new/existing projects, subjects, and sessions.

Author: Generated for MEG_migration project
Date: 2024
"""

import os
import shutil
import json
import pandas as pd
import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse


class MEGToBIDSConverter:
    """Main class for converting MEG data to BIDS format."""
    
    def __init__(self, verbose: bool = True):
        """Initialize the converter with logging setup."""
        self.verbose = verbose
        self.setup_logging()
        
        # BIDS required file extensions for Yokogawa/KIT system
        self.yokogawa_extensions = {
            'meg_data': ['.con'],
            'markers': ['.mrk'],
            'headshape': ['.txt'],
            'headpos': ['.pos', '.mat']
        }
        
        # BIDS entities and their order
        self.bids_entities = ['sub', 'ses', 'task', 'acq', 'run', 'proc', 'space', 'rec']
        
    def setup_logging(self):
        """Setup logging configuration."""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('meg_to_bids.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def identify_input_files(self, input_folder: Path) -> Dict[str, List[Path]]:
        """
        Identify and categorize input files from the session folder.
        
        Args:
            input_folder: Path to folder containing MEG session files
            
        Returns:
            Dictionary with categorized file paths
        """
        files = {
            'meg_data': [],
            'markers': [],
            'headshape': [],
            'headpos': [],
            'unknown': []
        }
        
        if not input_folder.exists():
            raise FileNotFoundError(f"Input folder not found: {input_folder}")
            
        for file_path in input_folder.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                categorized = False
                
                for category, extensions in self.yokogawa_extensions.items():
                    if ext in extensions:
                        files[category].append(file_path)
                        categorized = True
                        break
                        
                if not categorized:
                    files['unknown'].append(file_path)
                    
        self.logger.info(f"Identified files in {input_folder}:")
        for category, file_list in files.items():
            self.logger.info(f"  {category}: {len(file_list)} files")
            
        return files
        
    def check_bids_compliance(self, project_path: Path) -> bool:
        """
        Check if an existing project is BIDS-compliant.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            True if BIDS-compliant, False otherwise
        """
        required_files = [
            'dataset_description.json',
            'participants.tsv'
        ]
        
        for req_file in required_files:
            if not (project_path / req_file).exists():
                self.logger.warning(f"Missing required BIDS file: {req_file}")
                return False
                
        # Check if dataset_description.json has required fields
        try:
            with open(project_path / 'dataset_description.json', 'r') as f:
                desc = json.load(f)
                required_fields = ['Name', 'BIDSVersion']
                for field in required_fields:
                    if field not in desc:
                        self.logger.warning(f"Missing required field in dataset_description.json: {field}")
                        return False
        except Exception as e:
            self.logger.error(f"Error reading dataset_description.json: {e}")
            return False
            
        self.logger.info("Project appears to be BIDS-compliant")
        return True
        
    def create_bids_structure(self, project_path: Path, project_name: str) -> None:
        """
        Create basic BIDS directory structure and required files.
        
        Args:
            project_path: Path where BIDS structure should be created
            project_name: Name of the project/study
        """
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create dataset_description.json
        dataset_desc = {
            "Name": project_name,
            "BIDSVersion": "1.8.0",
            "DatasetType": "raw",
            "License": "CC0",
            "Authors": ["Research Team"],
            "Acknowledgements": "Generated by MEG-to-BIDS converter",
            "HowToAcknowledge": "Please cite this dataset",
            "Funding": [""],
            "EthicsApprovals": [""],
            "ReferencesAndLinks": [""],
            "DatasetDOI": ""
        }
        
        with open(project_path / 'dataset_description.json', 'w') as f:
            json.dump(dataset_desc, f, indent=2)
            
        # Create participants.tsv
        participants_df = pd.DataFrame(columns=['participant_id', 'age', 'sex', 'group'])
        participants_df.to_csv(project_path / 'participants.tsv', sep='\t', index=False)
        
        # Create participants.json
        participants_json = {
            "participant_id": {
                "LongName": "Participant identifier",
                "Description": "Unique identifier for the participant"
            },
            "age": {
                "LongName": "Age",
                "Description": "Age of the participant",
                "Units": "years"
            },
            "sex": {
                "LongName": "Sex",
                "Description": "Sex of the participant",
                "Levels": {
                    "M": "male",
                    "F": "female",
                    "O": "other"
                }
            },
            "group": {
                "LongName": "Group",
                "Description": "Experimental group"
            }
        }
        
        with open(project_path / 'participants.json', 'w') as f:
            json.dump(participants_json, f, indent=2)
            
        # Create README
        readme_content = f"""# {project_name}

## Description

This dataset contains MEG data collected using a Yokogawa/KIT system.
Converted to BIDS format using automated MEG-to-BIDS converter.

## Data Collection

- **MEG System**: Yokogawa/KIT
- **Conversion Date**: {datetime.now().strftime('%Y-%m-%d')}

## Files

The dataset follows the Brain Imaging Data Structure (BIDS) specification.

## Usage

Please refer to the BIDS specification for information on how to use this dataset.
"""
        
        with open(project_path / 'README', 'w') as f:
            f.write(readme_content)
            
        # Create CHANGES
        changes_content = f"""1.0.0 {datetime.now().strftime('%Y-%m-%d')}
\t- Initial BIDS conversion
"""
        
        with open(project_path / 'CHANGES', 'w') as f:
            f.write(changes_content)
            
        self.logger.info(f"Created BIDS structure for project: {project_name}")
        
    def get_subject_sessions(self, project_path: Path, subject_id: str) -> List[str]:
        """
        Get list of existing sessions for a subject.
        
        Args:
            project_path: Path to BIDS project
            subject_id: Subject identifier (without 'sub-' prefix)
            
        Returns:
            List of session identifiers
        """
        subject_path = project_path / f"sub-{subject_id}"
        sessions = []
        
        if subject_path.exists():
            for item in subject_path.iterdir():
                if item.is_dir() and item.name.startswith('ses-'):
                    sessions.append(item.name[4:])  # Remove 'ses-' prefix
                    
        return sorted(sessions)
        
    def get_next_session_number(self, project_path: Path, subject_id: str) -> str:
        """
        Get the next session number for a subject.
        
        Args:
            project_path: Path to BIDS project
            subject_id: Subject identifier
            
        Returns:
            Next session number as string
        """
        existing_sessions = self.get_subject_sessions(project_path, subject_id)
        
        if not existing_sessions:
            return "001"
            
        # Find the highest numeric session number
        max_num = 0
        for session in existing_sessions:
            try:
                num = int(session)
                max_num = max(max_num, num)
            except ValueError:
                continue
                
        return f"{max_num + 1:03d}"
        
    def update_participants_file(self, project_path: Path, subject_id: str) -> None:
        """
        Add subject to participants.tsv if not already present.
        
        Args:
            project_path: Path to BIDS project
            subject_id: Subject identifier
        """
        participants_file = project_path / 'participants.tsv'
        
        # Read existing participants, preserving empty values as empty strings
        if participants_file.exists():
            df = pd.read_csv(participants_file, sep='\t', dtype=str, keep_default_na=False)
        else:
            df = pd.DataFrame(columns=['participant_id', 'age', 'sex', 'group'])
            
        participant_id = f"sub-{subject_id}"
        
        # Check if subject already exists
        if participant_id not in df['participant_id'].values:
            new_row = {
                'participant_id': participant_id,
                'age': 'n/a',
                'sex': 'n/a', 
                'group': 'n/a'
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Write back preserving empty values and existing data
            df.to_csv(participants_file, sep='\t', index=False, na_rep='')
            self.logger.info(f"Added {participant_id} to participants.tsv")
        else:
            self.logger.info(f"Subject {participant_id} already exists in participants.tsv")
            
    def create_meg_metadata(self, meg_folder: Path, task_name: str = "task") -> None:
        """
        Create MEG-specific metadata files.
        
        Args:
            meg_folder: Path to MEG folder within subject/session
            task_name: Name of the task
        """
        # Create coordsystem.json for MEG
        coordsystem = {
            "MEGCoordinateSystem": "KitYokogawa",
            "MEGCoordinateUnits": "m"
            # "HeadCoilCoordinateSystem": "KitYokogawa",
            # "HeadCoilCoordinateUnits": "m",
            # "DigitizedLandmarks": True,
            # "DigitizedHeadPoints": True
        }
        
        with open(meg_folder / f"sub-{self.current_subject}_ses-{self.current_session}_coordsystem.json", 'w') as f:
            json.dump(coordsystem, f, indent=2)
            
        # Create basic MEG json metadata
        meg_json = {
            "TaskName": task_name,
            "InstitutionName": "Research Institution",
            "Manufacturer": "Yokogawa",
            "ManufacturersModelName": "KIT System",
            "SamplingFrequency": 1000,
            "PowerLineFrequency": 50,
            "SoftwareFilters": "n/a",
            "DewarPosition": "upright",
            "DigitizedLandmarks": True,
            "DigitizedHeadPoints": True
        }
        
        # Find MEG data files and create metadata for each
        for meg_file in meg_folder.glob("*.con"):
            json_file = meg_file.with_suffix('.json')
            with open(json_file, 'w') as f:
                json.dump(meg_json, f, indent=2)
                
        self.logger.info("Created MEG metadata files")
        
    def convert_files_to_bids(self, files: Dict[str, List[Path]], 
                            target_folder: Path, 
                            subject_id: str, 
                            session_id: str, 
                            task_name: str = "task") -> None:
        """
        Convert and copy files to BIDS format.
        
        Args:
            files: Dictionary of categorized file paths
            target_folder: MEG folder in BIDS structure
            subject_id: Subject identifier
            session_id: Session identifier  
            task_name: Task name for the experiment
        """
        self.current_subject = subject_id  # Set current subject for metadata creation
        self.current_session = session_id
        
        target_folder.mkdir(parents=True, exist_ok=True)
        
        # Convert MEG data files (.con)
        for i, meg_file in enumerate(files['meg_data'], 1):
            run_id = f"{i:02d}"
            bids_name = f"sub-{subject_id}_ses-{session_id}_task-{task_name}_run-{run_id}_meg.con"
            target_path = target_folder / bids_name
            shutil.copy2(meg_file, target_path)
            self.logger.info(f"Copied MEG data: {meg_file.name} -> {bids_name}")
            
        # Convert marker files (.mrk) 
        for i, marker_file in enumerate(files['markers'], 1):
            if len(files['markers']) == 1:
                bids_name = f"sub-{subject_id}_ses-{session_id}_task-{task_name}_markers.mrk"
            else:
                # Use acq entity for multiple marker files
                bids_name = f"sub-{subject_id}_ses-{session_id}_task-{task_name}_acq-{i:02d}_markers.mrk"
            target_path = target_folder / bids_name
            shutil.copy2(marker_file, target_path)
            self.logger.info(f"Copied markers: {marker_file.name} -> {bids_name}")
            
        # Convert headshape files (.txt)
        for i, headshape_file in enumerate(files['headshape'], 1):
            # Determine acquisition type based on filename patterns
            filename_lower = headshape_file.name.lower()
            if 'basic' in filename_lower or 'surface' in filename_lower:
                acq_type = "basicsurface"
            elif 'stylus' in filename_lower or 'points' in filename_lower:
                acq_type = "styluspoints"
            else:
                acq_type = f"{i:02d}"
                
            bids_name = f"sub-{subject_id}_ses-{session_id}_acq-{acq_type}_headshape.txt"
            target_path = target_folder / bids_name
            shutil.copy2(headshape_file, target_path)
            self.logger.info(f"Copied headshape: {headshape_file.name} -> {bids_name}")
            
        # Convert head position files (.pos/.mat)
        for i, headpos_file in enumerate(files['headpos'], 1):
            ext = headpos_file.suffix
            if len(files['headpos']) == 1:
                bids_name = f"sub-{subject_id}_ses-{session_id}_headshape{ext}"
            else:
                bids_name = f"sub-{subject_id}_ses-{session_id}_acq-{i:02d}_headshape{ext}"
            target_path = target_folder / bids_name
            shutil.copy2(headpos_file, target_path)
            self.logger.info(f"Copied head position: {headpos_file.name} -> {bids_name}")
            
        # Update coordsystem.json with actual headshape file references
        self.update_coordsystem_references(target_folder, subject_id, session_id)
        
        # Create MEG metadata
        self.create_meg_metadata(target_folder, task_name)
        
    def update_coordsystem_references(self, meg_folder: Path, subject_id: str, session_id: str) -> None:
        """
        Update coordsystem.json with references to actual headshape files.
        
        Args:
            meg_folder: Path to MEG folder
            subject_id: Subject identifier
            session_id: Session identifier
        """
        coordsystem_file = meg_folder / f"sub-{subject_id}_ses-{session_id}_coordsystem.json"
        
        if not coordsystem_file.exists():
            return
            
        with open(coordsystem_file, 'r') as f:
            coordsystem = json.load(f)
            
        # Find headshape files and update references
        headshape_files = list(meg_folder.glob(f"sub-{subject_id}_ses-{session_id}_*_headshape.*"))
        
        if headshape_files:
            # Update references based on acquisition types
            for hf in headshape_files:
                if 'basicsurface' in hf.name:
                    coordsystem["DigitizedHeadPoints"] = hf.name
                elif 'styluspoints' in hf.name:
                    coordsystem["DigitizedLandmarksFile"] = hf.name
                    
        with open(coordsystem_file, 'w') as f:
            json.dump(coordsystem, f, indent=2)
            
    def run_bids_validator(self, project_path: Path) -> Tuple[bool, str]:
        """
        Run BIDS validator on the project and return results.
        
        Args:
            project_path: Path to BIDS project
            
        Returns:
            Tuple of (is_valid, validation_output)
        """
        try:
            # Try to run bids-validator (handle Windows PowerShell execution policy)
            import platform
            if platform.system() == "Windows":
                # Use cmd /c to bypass PowerShell execution policy on Windows
                result = subprocess.run([
                    'cmd', '/c', 'bids-validator', str(project_path), '--json'
                ], capture_output=True, text=True, timeout=300)
            else:
                # Direct call on Unix-like systems
                result = subprocess.run([
                    'bids-validator', str(project_path), '--json'
                ], capture_output=True, text=True, timeout=300)
            
            # Only use stdout for JSON output, stderr may contain Node.js warnings
            validation_output = result.stdout
            is_valid = result.returncode == 0
            
            # Save validation log as JSON outside BIDS dataset (in parent directory)
            log_file = project_path.parent / f'{project_path.name}_validation_log.json'
            
            # Clean and save the BIDS validator JSON output
            # Filter out Node.js warnings and keep only JSON content
            clean_output = validation_output.strip()
            if clean_output:
                # Try to validate it's proper JSON and format it nicely
                try:
                    parsed_json = json.loads(clean_output)
                    with open(log_file, 'w') as f:
                        json.dump(parsed_json, f, indent=2)
                except json.JSONDecodeError:
                    # If not valid JSON, save as-is but log a warning
                    with open(log_file, 'w') as f:
                        f.write(clean_output)
                    self.logger.warning("Validation output may not be valid JSON")
            else:
                # Empty output, create minimal JSON structure
                with open(log_file, 'w') as f:
                    json.dump({"note": "No validation output received"}, f, indent=2)
                
            if is_valid:
                success_msg = f"BIDS validation PASSED - This is a validated BIDS dataset"
                self.logger.info(success_msg)
                self.logger.info(f"Validation log saved: {log_file}")
            else:
                self.logger.warning(f"BIDS validation FAILED - See validation log: {log_file}")
                
            return is_valid, validation_output
            
        except subprocess.TimeoutExpired:
            error_msg = "BIDS validation timed out"
            self.logger.error(error_msg)
            return False, error_msg
        except FileNotFoundError:
            error_msg = "bids-validator not found. Please install: npm install -g bids-validator"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error running BIDS validator: {e}"
            self.logger.error(error_msg)
            return False, error_msg
            
    def process_session(self, input_folder: Path, 
                       output_base: Path, 
                       project_name: Optional[str] = None,
                       subject_id: Optional[str] = None, 
                       session_id: Optional[str] = None,
                       task_name: str = "task") -> bool:
        """
        Process a single session following the decision tree logic.
        
        Args:
            input_folder: Path to folder with MEG session files
            output_base: Base output directory
            project_name: Name of the project (from folder name if not specified)
            subject_id: Subject identifier (extracted if not provided)
            session_id: Session identifier (auto-generated if not provided)
            task_name: Task name for the experiment
            
        Returns:
            True if processing was successful
        """
        try:
            # Extract project name from input folder if not provided
            if not project_name:
                project_name = input_folder.name
                
            # Extract subject ID from folder structure if not provided
            if not subject_id:
                # Try to extract from folder name or use default
                folder_name = input_folder.name.lower()
                if 'sub-' in folder_name:
                    parts = folder_name.split('sub-')[1].split('_')[0].split('-')[0]
                    subject_id = parts
                else:
                    subject_id = "001"  # Default subject
                    
            self.logger.info(f"Processing session for project: {project_name}, subject: {subject_id}")
            
            # Step 1: Identify input files
            files = self.identify_input_files(input_folder)
            
            if not files['meg_data']:
                raise ValueError("No MEG data files (.con) found in input folder")
                
            # Step 2: Determine project path
            project_path = output_base / project_name
            
            # Step 3: Check if project exists and is BIDS-compliant
            project_exists = project_path.exists()
            is_bids_compliant = False
            
            if project_exists:
                is_bids_compliant = self.check_bids_compliance(project_path)
                self.logger.info(f"Existing project found. BIDS compliant: {is_bids_compliant}")
            else:
                self.logger.info("Creating new project")
                
            # Step 4: Create/update BIDS structure if needed
            if not project_exists or not is_bids_compliant:
                self.logger.info("Creating/updating BIDS structure")
                self.create_bids_structure(project_path, project_name)
                
            # Step 5: Determine session ID
            if not session_id:
                session_id = self.get_next_session_number(project_path, subject_id)
                
            self.logger.info(f"Using session ID: {session_id}")
            
            # Step 6: Create subject/session directory structure
            subject_path = project_path / f"sub-{subject_id}"
            session_path = subject_path / f"ses-{session_id}"
            meg_folder = session_path / "meg"
            
            # Step 7: Update participants file
            self.update_participants_file(project_path, subject_id)
            
            # Step 8: Convert and copy files
            self.convert_files_to_bids(files, meg_folder, subject_id, session_id, task_name)
            
            self.logger.info(f"Successfully processed session: sub-{subject_id}/ses-{session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing session: {e}")
            return False
            
    def process_multiple_sessions(self, input_folders: List[Path], 
                                output_base: Path, 
                                project_name: Optional[str] = None) -> None:
        """
        Process multiple session folders.
        
        Args:
            input_folders: List of paths to session folders
            output_base: Base output directory
            project_name: Project name (extracted from first folder if not provided)
        """
        if not project_name and input_folders:
            project_name = input_folders[0].parent.name
            
        success_count = 0
        
        for i, folder in enumerate(input_folders, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing folder {i}/{len(input_folders)}: {folder.name}")
            self.logger.info(f"{'='*60}")
            
            if self.process_session(folder, output_base, project_name):
                success_count += 1
                
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Processing complete: {success_count}/{len(input_folders)} sessions successful")
        
        if success_count > 0:
            if project_name:
                project_path = output_base / project_name
                self.logger.info("Running BIDS validation...")
                is_valid, validation_output = self.run_bids_validator(project_path)
            
            if is_valid:
                self.logger.info("All done! Your BIDS dataset is valid.")
            else:
                self.logger.warning(f"BIDS validation found issues. Check {project_name}_validation_log.json in output directory")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Convert MEG data from Yokogawa system to BIDS format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single session
  python meg_to_bids.py /path/to/session/folder /path/to/output --project myproject
  
  # Convert with specific subject and session IDs
  python meg_to_bids.py /path/to/session/folder /path/to/output --subject 001 --session 001
  
  # Convert multiple sessions (using pattern)
  python meg_to_bids.py "/path/to/sessions/*" /path/to/output --project myproject
        """
    )
    
    parser.add_argument('input_path', type=str,
                       help='Path to session folder or pattern for multiple folders')
    parser.add_argument('output_path', type=str,
                       help='Base output directory for BIDS structure')
    parser.add_argument('--project', type=str,
                       help='Project name (default: extracted from input folder)')
    parser.add_argument('--subject', type=str,
                       help='Subject ID (default: auto-extracted or 001)')
    parser.add_argument('--session', type=str,
                       help='Session ID (default: auto-generated)')
    parser.add_argument('--task', type=str, default='task',
                       help='Task name (default: task)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--validate', action='store_true',
                       help='Run BIDS validation after conversion')
    
    args = parser.parse_args()
    
    # Initialize converter
    converter = MEGToBIDSConverter(verbose=args.verbose)
    
    # Process input path(s)
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)
    
    if '*' in str(input_path):
        # Handle multiple folders with glob pattern
        import glob
        input_folders = [Path(p) for p in glob.glob(str(input_path)) if Path(p).is_dir()]
        if not input_folders:
            converter.logger.error(f"No folders found matching pattern: {input_path}")
            return
        converter.process_multiple_sessions(input_folders, output_path, args.project)
    else:
        # Single folder
        if not input_path.exists():
            converter.logger.error(f"Input path does not exist: {input_path}")
            return
            
        success = converter.process_session(
            input_path, output_path, args.project, 
            args.subject, args.session, args.task
        )
        
        if success and args.validate:
            project_name = args.project or input_path.name
            project_path = output_path / project_name
            converter.run_bids_validator(project_path)


if __name__ == "__main__":
    main() 