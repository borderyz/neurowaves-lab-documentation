# Pipeline Configuration Report Generation

This directory contains the tools to generate a PDF and HTML report detailing the pipeline configuration and the associated BIDS dataset.

## Prerequisites

Ensure you have the following installed:
- **Quarto**: [Download and Install Quarto](https://quarto.org/docs/get-started/)
- **Python**: with the `neurowaves` environment activated.

## Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

To generate the report, use the following command. You must specify the path to the configuration file using the `-P config_path:...` argument.

**Note:** It is recommended to run this command within the `neurowaves` conda environment to ensure all dependencies (including `papermill` and `mne`) are correctly resolved.

```bash
# Example command (adjust path as needed)
conda run -n neurowaves quarto render report.qmd -P config_path:"../pipeline_config_files/config_template.yml"
```

## Output

The generated reports will be saved in the `_output` directory:
- `_output/report.html`
- `_output/report.pdf`

## Features
- **Dataset Report**: Automatically generates a BIDS dataset summary using `mne_bids`.
- **Configuration Details**: Displays the pipeline configuration in a readable format.
- **Raw Configuration**: Shows the full configuration as a flattened table.
