#!/bin/bash
# Quick launch wrapper for Interior Inspiration Engine
# Handles conda environment activation and UI launch

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDA_ENV="idp"

echo "============================================================"
echo "🏠 Interior Inspiration Engine - Quick Launcher"
echo "============================================================"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found!"
    echo "   Please install Anaconda or Miniconda first"
    exit 1
fi

# Activate conda environment
echo "📦 Activating environment: $CONDA_ENV"
source "$(conda info --base)/etc/profile.d/conda.sh"

if ! conda activate "$CONDA_ENV" 2>/dev/null; then
    echo "❌ Environment '$CONDA_ENV' not found!"
    echo ""
    echo "Create it with:"
    echo "  conda create -n $CONDA_ENV python=3.9"
    echo "  conda activate $CONDA_ENV"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo "✅ Environment activated"
echo ""

# Run status check
echo "📊 System Status:"
echo "--------------------------------------------------------------"
python "$PROJECT_DIR/status.py"

echo ""
echo "🚀 Launching Streamlit UI..."
echo "   Press Ctrl+C to stop"
echo ""

# Launch with python module to avoid import issues
cd "$PROJECT_DIR"
python -m streamlit run ui/app.py \
    --server.port=8501 \
    --theme.base=light \
    --theme.primaryColor=#1976D2
