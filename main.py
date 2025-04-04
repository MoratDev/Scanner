import argparse
import os
import random
import tempfile
import io
from datetime import datetime
import uuid
from PIL import Image, ImageDraw, ImageFilter
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading

class PDFScannerEffects:
    @staticmethod
    def convert_page_to_image(page, dpi=150):
        """Convert a PDF page to a PIL Image"""
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
        
    @staticmethod
    def add_rotation(img, max_angle=1.5):
        """Add slight random rotation"""
        angle = random.uniform(-max_angle, max_angle)
        return img.rotate(angle, resample=Image.BICUBIC, expand=True)
    
    @staticmethod
    def convert_to_grayscale(img):
        """Convert to grayscale"""
        return img.convert('L').convert('RGB')
        
    @staticmethod
    def convert_to_black_and_white(img, threshold=200):
        """Convert to black and white with threshold"""
        gray = img.convert('L')
        return gray.point(lambda x: 0 if x < threshold else 255, '1').convert('RGB')
    
    @staticmethod
    def add_noise(img, factor=10):
        """Add random noise"""
        noise = Image.new('RGB', img.size, (0, 0, 0))
        draw = ImageDraw.Draw(noise)
        
        width, height = img.size
        for x in range(0, width, 2):
            for y in range(0, height, 2):
                if random.randint(0, 100) < factor:
                    noise_value = random.randint(0, 50)
                    draw.point((x, y), fill=(noise_value, noise_value, noise_value))
        
        return Image.blend(img, noise, 0.1)
    
    @staticmethod
    def add_fold_marks(img, count=1):
        """Add fold marks"""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        for _ in range(count):
            # Horizontal or vertical fold
            if random.choice([True, False]):
                # Horizontal fold
                y = random.randint(height // 4, 3 * height // 4)
                for x in range(0, width, 2):
                    y_var = y + random.randint(-2, 2)
                    intensity = random.randint(150, 230)
                    draw.point((x, y_var), fill=(intensity, intensity, intensity))
            else:
                # Vertical fold
                x = random.randint(width // 4, 3 * width // 4)
                for y in range(0, height, 2):
                    x_var = x + random.randint(-2, 2)
                    intensity = random.randint(150, 230)
                    draw.point((x_var, y), fill=(intensity, intensity, intensity))
        
        return img
    
    @staticmethod
    def add_edge_shadow(img):
        """Add subtle shadow near edges"""
        width, height = img.size
        shadow = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(shadow)
        
        edge_width = int(min(width, height) * 0.03)
        
        for i in range(edge_width):
            opacity = int(200 * (edge_width - i) / edge_width)
            draw.rectangle(
                [(i, i), (width - i, height - i)],
                outline=(255 - opacity, 255 - opacity, 255 - opacity)
            )
        
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=edge_width/2))
        return Image.blend(img, shadow, 0.3)
    
    @staticmethod
    def apply_blur(img, radius=0.5):
        """Apply slight blur"""
        if radius > 0:
            return img.filter(ImageFilter.GaussianBlur(radius=radius))
        return img
    
    @staticmethod
    def create_scanner_metadata(scanner_name="HP ScanJet Pro 3000"):
        """Create metadata to simulate a scan"""
        now = datetime.now()
        return {
            "/Creator": scanner_name,
            "/Producer": f"{scanner_name} Software 3.12.4",
            "/CreationDate": now.strftime("D:%Y%m%d%H%M%S"),
            "/ModDate": now.strftime("D:%Y%m%d%H%M%S"),
            "/Scanner": scanner_name,
            "/ScanningApplication": "HP Smart",
            "/ScanDate": now.strftime("%Y-%m-%d"),
            "/ScanTime": now.strftime("%H:%M:%S"),
            "/UUID": str(uuid.uuid4()),
        }
    
    @staticmethod
    def process_pdf(input_pdf, output_pdf, options):
        """Process PDF with scanning effects"""
        input_doc = fitz.open(input_pdf)
        pdf_writer = PdfWriter()
        
        for page_num in range(len(input_doc)):
            page = input_doc[page_num]
            
            # Convert to image
            img = PDFScannerEffects.convert_page_to_image(page, dpi=options.get('dpi', 150))
            
            # Apply effects
            if options.get('rotate', True):
                img = PDFScannerEffects.add_rotation(img, max_angle=options.get('max_rotation', 1.5))
            
            if options.get('grayscale', True):
                img = PDFScannerEffects.convert_to_grayscale(img)
            
            if options.get('bw', False):
                img = PDFScannerEffects.convert_to_black_and_white(img)
            
            if options.get('add_noise', True):
                img = PDFScannerEffects.add_noise(img)
            
            if options.get('fold_marks', True):
                img = PDFScannerEffects.add_fold_marks(img, count=options.get('fold_count', 1))
            
            if options.get('add_shadow', True):
                img = PDFScannerEffects.add_edge_shadow(img)
            
            if options.get('blur', 0.5) > 0:
                img = PDFScannerEffects.apply_blur(img, radius=options.get('blur', 0.5))
            
            # Convert back to PDF
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=options.get('quality', 85))
            img_bytes.seek(0)
            
            # Create a temporary PDF with the image
            temp_pdf = fitz.open()
            img_rectangle = fitz.Rect(0, 0, img.width, img.height)
            new_page = temp_pdf.new_page(width=img.width, height=img.height)
            new_page.insert_image(img_rectangle, stream=img_bytes)
            
            # Save temporary PDF but don't attempt deletion
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file_name = temp_file.name
            temp_file.close()
            temp_pdf.save(temp_file_name)
            temp_pdf.close()
            
            # Add page to output PDF
            temp_reader = PdfReader(temp_file_name)
            pdf_writer.add_page(temp_reader.pages[0])
            
            # No cleanup - just leave the temp file
        
        # Set metadata
        metadata = PDFScannerEffects.create_scanner_metadata(options.get('scanner_name', 'HP ScanJet Pro 3000'))
        pdf_writer.add_metadata(metadata)
        
        # Save output PDF
        with open(output_pdf, "wb") as f:
            pdf_writer.write(f)
        
        input_doc.close()

class ScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Scanner Effect Creator")
        self.root.geometry("600x600")
        
        self.input_pdf = tk.StringVar()
        self.output_pdf = tk.StringVar()
        self.dpi = tk.IntVar(value=150)
        self.rotate = tk.BooleanVar(value=True)
        self.max_rotation = tk.DoubleVar(value=1.5)
        self.grayscale = tk.BooleanVar(value=True)
        self.bw = tk.BooleanVar(value=False)
        self.add_noise = tk.BooleanVar(value=True)
        self.fold_marks = tk.BooleanVar(value=True)
        self.fold_count = tk.IntVar(value=1)
        self.quality = tk.IntVar(value=85)
        self.scanner_name = tk.StringVar(value="HP ScanJet Pro 3000")
        self.add_shadow = tk.BooleanVar(value=True)
        self.blur = tk.DoubleVar(value=0.5)
        
        self.create_widgets()
    
    def create_widgets(self):
        # File selection frame
        file_frame = ttk.LabelFrame(self.root, text="File Selection")
        file_frame.pack(fill="x", expand=True, padx=10, pady=10)
        
        ttk.Label(file_frame, text="Input PDF:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.input_pdf, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(file_frame, text="Output PDF:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_pdf, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.root, text="Scanning Effect Options")
        options_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Basic options
        ttk.Checkbutton(options_frame, text="Add rotation", variable=self.rotate).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(options_frame, text="Max rotation:").grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Scale(options_frame, from_=0.1, to=5.0, variable=self.max_rotation, orient=tk.HORIZONTAL).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Grayscale", variable=self.grayscale).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(options_frame, text="Black & White", variable=self.bw).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Add noise", variable=self.add_noise).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Checkbutton(options_frame, text="Add shadow", variable=self.add_shadow).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="Add fold marks", variable=self.fold_marks).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(options_frame, text="Number of folds:").grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(options_frame, from_=1, to=5, textvariable=self.fold_count, width=5).grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(options_frame, text="DPI:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Scale(options_frame, from_=72, to=300, variable=self.dpi, orient=tk.HORIZONTAL).grid(row=4, column=1, columnspan=2, padx=5, pady=5)
        
        ttk.Label(options_frame, text="JPEG Quality:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Scale(options_frame, from_=50, to=100, variable=self.quality, orient=tk.HORIZONTAL).grid(row=5, column=1, columnspan=2, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Blur:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Scale(options_frame, from_=0, to=2.0, variable=self.blur, orient=tk.HORIZONTAL).grid(row=6, column=1, columnspan=2, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Scanner name:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(options_frame, textvariable=self.scanner_name, width=30).grid(row=7, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=580, mode='determinate')
        self.progress.pack(fill="x", padx=10, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var)
        self.status_label.pack(padx=10, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Create Scanned PDF", command=self.process_pdf_threaded).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
    
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select input PDF file",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        if filename:
            self.input_pdf.set(filename)
            # Suggest output filename
            base, ext = os.path.splitext(filename)
            self.output_pdf.set(f"{base}_scanned{ext}")
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save scanned PDF as",
            defaultextension=".pdf",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        if filename:
            self.output_pdf.set(filename)
    
    def process_pdf_threaded(self):
        if not self.input_pdf.get():
            messagebox.showerror("Error", "Please select an input PDF file")
            return
        
        if not self.output_pdf.get():
            messagebox.showerror("Error", "Please specify an output PDF file")
            return
        
        threading.Thread(target=self.process_pdf).start()
    
    def process_pdf(self):
        self.status_var.set("Processing...")
        self.progress['value'] = 0
        self.root.update_idletasks()
        
        try:
            options = {
                'dpi': self.dpi.get(),
                'rotate': self.rotate.get(),
                'max_rotation': self.max_rotation.get(),
                'grayscale': self.grayscale.get(),
                'bw': self.bw.get(),
                'add_noise': self.add_noise.get(),
                'fold_marks': self.fold_marks.get(),
                'fold_count': self.fold_count.get(),
                'quality': self.quality.get(),
                'scanner_name': self.scanner_name.get(),
                'add_shadow': self.add_shadow.get(),
                'blur': self.blur.get()
            }
            
            PDFScannerEffects.process_pdf(self.input_pdf.get(), self.output_pdf.get(), options)
            
            self.status_var.set("Completed!")
            self.progress['value'] = 100
            messagebox.showinfo("Success", f"Created scanned-looking PDF: {self.output_pdf.get()}")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def parse_args():
    parser = argparse.ArgumentParser(description="Convert a PDF to look like it's been scanned")
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("output_pdf", help="Path to save the scanned-looking PDF")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for the scanned effect")
    parser.add_argument("--rotate", action="store_true", help="Add slight random rotation")
    parser.add_argument("--max-rotation", type=float, default=1.5, help="Maximum rotation angle in degrees")
    parser.add_argument("--grayscale", action="store_true", help="Convert to grayscale")
    parser.add_argument("--bw", action="store_true", help="Convert to black and white")
    parser.add_argument("--add-noise", action="store_true", help="Add noise to simulate scanner artifacts")
    parser.add_argument("--fold-marks", action="store_true", help="Add fold marks to pages")
    parser.add_argument("--fold-count", type=int, default=1, help="Number of fold marks to add")
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality for compression artifacts")
    parser.add_argument("--scanner-name", default="HP ScanJet Pro 3000", help="Scanner name for metadata")
    parser.add_argument("--add-shadow", action="store_true", help="Add subtle shadow near edges")
    parser.add_argument("--blur", type=float, default=0, help="Apply slight blur (0-2.0)")
    return parser.parse_args()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Command line mode
        args = parse_args()
        options = vars(args)
        PDFScannerEffects.process_pdf(args.input_pdf, args.output_pdf, options)
        print(f"Created scanned-looking PDF: {args.output_pdf}")
    else:
        # GUI mode
        root = tk.Tk()
        app = ScannerApp(root)
        root.mainloop()