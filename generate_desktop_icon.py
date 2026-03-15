"""
Utility to generate a simple desktop app icon
Creates SVG and converts to PNG for multiple resolutions
"""

import os
from pathlib import Path

# SVG icon data (Piddy logo concept)
PIDDY_SVG = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <!-- Background circle -->
  <circle cx="128" cy="128" r="120" fill="#6366F1" opacity="0.1"/>
  
  <!-- Main accent circle -->
  <circle cx="128" cy="128" r="100" fill="#6366F1"/>
  
  <!-- Piddy P icon (stylized) -->
  <g fill="#FFFFFF">
    <!-- Vertical line of P -->
    <rect x="90" y="65" width="20" height="130" rx="10"/>
    
    <!-- Top curve of P -->
    <path d="M 110 65 Q 155 65 155 95 Q 155 120 110 120 Z" fill="#FFFFFF"/>
    
    <!-- AI sparkle accent -->
    <circle cx="165" cy="60" r="8" fill="#FCD34D"/>
    <circle cx="175" cy="75" r="6" fill="#FCD34D" opacity="0.7"/>
    <circle cx="155" cy="75" r="5" fill="#FCD34D" opacity="0.5"/>
  </g>
  
  <!-- Bottom accent -->
  <rect x="120" y="200" width="16" height="40" rx="8" fill="#6366F1"/>
  
  <!-- Version indicator -->
  <text x="128" y="235" font-size="14" font-weight="bold" fill="#6366F1" text-anchor="middle">v1.0</text>
</svg>
'''

def main():
    assets_dir = Path(__file__).parent / 'desktop' / 'assets'
    assets_dir.mkdir(exist_ok=True, parents=True)
    
    # Write SVG
    svg_file = assets_dir / 'icon.svg'
    svg_file.write_text(PIDDY_SVG)
    print(f"✅ Created {svg_file}")
    
    # Try to convert SVG to PNG if cairosvg is available
    try:
        import cairosvg
        
        # Generate multiple resolutions
        sizes = [16, 32, 64, 128, 256, 512]
        
        for size in sizes:
            png_file = assets_dir / f'icon_{size}.png'
            cairosvg.svg2png(
                url=str(svg_file),
                write_to=str(png_file),
                output_width=size,
                output_height=size
            )
            print(f"✅ Created {png_file}")
        
        # Also create main icon.png (256x256)
        png_file = assets_dir / 'icon.png'
        cairosvg.svg2png(
            url=str(svg_file),
            write_to=str(png_file),
            output_width=256,
            output_height=256
        )
        print(f"✅ Created {png_file}")
        
    except ImportError:
        print("ℹ️ cairosvg not available. Install to generate PNG icons:")
        print("   pip install cairosvg")
        print("   Or convert SVG manually using online tools")
        
        # As fallback, create a simple PNG placeholder using PIL if available
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (256, 256), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw Piddy pink/purple circles
            draw.ellipse([28, 28, 228, 228], fill='#6366F1', outline='#4F46E5')
            draw.text((128, 128), 'P', fill='white', anchor='mm')
            
            icon_file = assets_dir / 'icon.png'
            img.save(icon_file)
            print(f"✅ Created placeholder {icon_file}")
        except ImportError:
            print("⚠️  PIL not available either. Create icon manually.")

if __name__ == '__main__':
    main()
