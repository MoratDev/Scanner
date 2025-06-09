# PDF Scanner Effect Creator

A Python application that transforms clean PDFs into realistic scanned documents with customizable aging effects.

## Features

### Core Effects
- **Rotation**: Add slight random rotation to simulate manual scanning
- **Grayscale/B&W**: Convert to grayscale or black and white
- **Noise**: Add random noise and artifacts
- **Fold marks**: Simulate document creases and folds
- **Edge shadows**: Add subtle shadows near page edges
- **Blur**: Apply slight blur for realistic scanning quality

### Interface
- **GUI Mode**: Easy-to-use interface with real-time preview
- **Command Line**: Batch processing and automation support
- **PDF Preview**: Navigate through pages with effect preview
- **Random Scanner Names**: 18+ realistic printer/scanner models

## Installation

### Requirements
```
pip install pillow pymupdf pypdf2 tkinter
```

### Dependencies
- Python 3.6+
- PIL (Pillow)
- PyMuPDF (fitz)
- PyPDF2
- tkinter (usually included with Python)

## Usage

### GUI Mode
```bash
python pdf_scanner.py
```

1. Browse and select input PDF
2. Set output filename
3. Adjust scanning effects using controls
4. Use "Preview Effects" to see results on current page
5. Navigate between pages with arrow buttons
6. Click "Random" to randomize scanner name
7. Click "Create Scanned PDF" to process

### Command Line Mode
```bash
python pdf_scanner.py input.pdf output.pdf [options]
```

#### Command Line Options
```
--dpi INT              DPI for scanning effect (default: 150)
--rotate               Add slight random rotation
--max-rotation FLOAT   Maximum rotation angle in degrees (default: 1.5)
--grayscale            Convert to grayscale
--bw                   Convert to black and white
--add-noise            Add noise to simulate scanner artifacts
--fold-marks           Add fold marks to pages
--fold-count INT       Number of fold marks (default: 1)
--quality INT          JPEG quality for compression (default: 85)
--scanner-name STR     Scanner name for metadata
--add-shadow           Add subtle shadow near edges
--blur FLOAT           Apply blur radius 0-2.0 (default: 0)
```

#### Examples
```bash
# Basic scanned effect
python pdf_scanner.py document.pdf scanned.pdf --rotate --grayscale --add-noise

# High quality scan with minimal effects
python pdf_scanner.py clean.pdf scan.pdf --dpi 300 --quality 95 --blur 0.2

# Aged document effect
python pdf_scanner.py modern.pdf aged.pdf --bw --fold-marks --fold-count 3 --add-shadow
```

## Preview Features

- **Live Preview**: See pages before processing
- **Effect Preview**: Apply effects to current page preview
- **Page Navigation**: Browse multi-page documents
- **Scale Display**: Optimized preview scaling

## Scanner Models

The app includes 18+ realistic scanner/printer names from major brands:
- HP ScanJet series
- Canon imageFORMULA and CanoScan
- Epson WorkForce and Perfection
- Brother ADS and MFC series
- Fujitsu ScanSnap
- Xerox WorkCentre
- And more...

## Technical Details

### Process Flow
1. PDF pages converted to images at specified DPI
2. Effects applied in sequence to each page
3. Images converted back to PDF format
4. Scanner metadata added to output file
5. Final PDF assembled with all processed pages

### Effect Details
- **Rotation**: Random angle within specified range using bicubic interpolation
- **Noise**: Scattered pixel-level artifacts with configurable intensity
- **Fold marks**: Horizontal/vertical lines with natural variation
- **Shadows**: Gaussian-blurred edge darkening
- **Compression**: JPEG quality simulation for authentic scan appearance

## File Structure
```
pdf_scanner.py          # Main application
├── PDFScannerEffects   # Core processing class
├── ScannerApp          # GUI interface class
└── Command line args   # CLI argument parsing
```
## Troubleshooting

**Import Errors**: Install required packages with pip
**Preview Not Loading**: Check PDF file permissions and format
**Memory Issues**: Reduce DPI for large documents
**Quality Issues**: Adjust JPEG quality and blur settings

## Changelog

## v2.0
- Effects preview

### v1.5
- Added PDF preview with page navigation
- Random scanner name generator
- Enhanced GUI layout
- Improved error handling

### v1.0
- Initial release
- Basic scanning effects
- Command line and GUI modes
