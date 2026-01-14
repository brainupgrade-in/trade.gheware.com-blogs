#!/usr/bin/env python3
"""
Generate blog hero images using Gemini 2.5 Flash Image

Usage:
    python3 generate-hero-images.py                    # Generate all configured images
    python3 generate-hero-images.py --list             # List configured images
    python3 generate-hero-images.py --single "prompt"  # Generate single image with custom prompt

Requirements:
    pip install google-genai python-dotenv pillow

Configuration:
    GEMINI_API_KEY in /home/rajesh/.rajesh/health/.env
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import time

# Load API key
load_dotenv("/home/rajesh/.rajesh/health/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("GEMINI_API_KEY not found in /home/rajesh/.rajesh/health/.env")
    sys.exit(1)

# Configure Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash-image"

# Default output directory (can be overridden)
DEFAULT_OUTPUT_DIR = Path("/home/rajesh/trade.gheware.com/assets/images")

# Blog hero image configurations
HERO_CONFIGS = [
    {
        "filename": "import-zerodha-portfolio-hero.png",
        "prompt": "Generate an image: Professional blog hero image for investment portfolio import. Modern smartphone displaying portfolio dashboard with green growth charts, stock prices, and financial data. Clean navy blue gradient background. Professional investment finance aesthetic. High contrast, cinematic lighting. Landscape orientation 16:9."
    },
    {
        "filename": "manual-csv-portfolio-import-hero.png",
        "prompt": "Generate an image: Professional blog hero image for CSV data import. Spreadsheet transforming into beautiful dashboard visualization, data flow with blue accents. Clean modern design. Professional finance aesthetic. High contrast, cinematic lighting. Landscape orientation 16:9."
    },
    {
        "filename": "setting-up-smart-alerts-hero.png",
        "prompt": "Generate an image: Professional blog hero image for smart alerts. Bell notification icons with stock charts, alert dashboard interface, protective shield with financial graphs. Orange/gold accent color. Clean modern design. Professional finance aesthetic. Landscape orientation 16:9."
    },
    {
        "filename": "ai-stock-discovery-hero.png",
        "prompt": "Generate an image: Professional blog hero image for AI stock discovery. AI brain analyzing stock charts, neural network patterns over financial data, futuristic investment analysis. Purple accent color. Clean modern design. Professional finance aesthetic. Landscape orientation 16:9."
    },
    {
        "filename": "portfolio-diversification-hero.png",
        "prompt": "Generate an image: Professional blog hero image for portfolio diversification. Colorful pie chart showing asset allocation, diverse investment baskets, balanced portfolio visualization. Green accent color. Clean modern design. Professional finance aesthetic. Landscape orientation 16:9."
    },
    {
        "filename": "introduction-to-investing-hero.png",
        "prompt": "Generate an image: Professional blog hero image for introduction to investing. Seed growing into money tree, compound growth visualization, growth charts. Emerald green accent. Clean modern design. Professional finance aesthetic. Landscape orientation 16:9."
    },
    {
        "filename": "getting-started-hero.png",
        "prompt": "Generate an image: Professional blog hero image for portfolio tracking. Clean dashboard with portfolio metrics, real-time stock prices, returns visualization. Sky blue accent. Clean modern design. Professional finance aesthetic. Landscape orientation 16:9."
    },
    {
        "filename": "ai-powered-stock-discovery-hero.png",
        "prompt": "Generate an image: Professional blog hero image for AI-powered stock discovery revolution. Futuristic AI interface analyzing Indian stock market data, machine learning visualization, robot analyzing charts. Blue and purple gradient. Clean modern design. Professional finance aesthetic. Landscape 16:9."
    },
    {
        "filename": "understanding-diversification-hero.png",
        "prompt": "Generate an image: Professional blog hero image for understanding portfolio diversification. Multiple baskets with different colored eggs, pie chart segments, risk balance scale. Green and blue accents. Clean modern design. Professional finance aesthetic. Landscape 16:9."
    }
]


def generate_hero_image(prompt: str, output_path: Path, width: int = 1200, height: int = 630) -> bool:
    """Generate a single hero image using Gemini"""

    temp_path = Path("/tmp") / f"hero_raw_{output_path.name}"

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
        )

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data

                    if image_data:
                        # Save raw image
                        with open(temp_path, 'wb') as f:
                            f.write(image_data)

                        # Resize to exact dimensions
                        img = Image.open(temp_path)
                        img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
                        img_resized.save(output_path, "PNG", optimize=True)

                        # Clean up temp file
                        temp_path.unlink(missing_ok=True)
                        return True

        return False

    except Exception as e:
        print(f"   Error: {e}")
        return False


def generate_all(output_dir: Path):
    """Generate all configured hero images"""
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Trade Gheware Blog Hero Image Generator")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print(f"Images to generate: {len(HERO_CONFIGS)}")

    successful = 0
    failed = 0

    for i, config in enumerate(HERO_CONFIGS, 1):
        print(f"\n[{i}/{len(HERO_CONFIGS)}] Generating: {config['filename']}")
        print(f"   Prompt: {config['prompt'][:60]}...")

        output_path = output_dir / config['filename']
        if generate_hero_image(config['prompt'], output_path):
            file_size = output_path.stat().st_size / 1024
            print(f"   Saved: {output_path.name} ({file_size:.1f} KB)")
            successful += 1
        else:
            print(f"   Failed to generate image")
            failed += 1

        # Rate limiting
        if i < len(HERO_CONFIGS):
            time.sleep(3)

    print("\n" + "=" * 60)
    print(f"COMPLETE: {successful} successful, {failed} failed")
    print("=" * 60)

    # List generated files
    print("\nGenerated files:")
    for f in sorted(output_dir.glob("*.png")):
        size = f.stat().st_size / 1024
        print(f"  - {f.name} ({size:.1f} KB)")


def generate_single(prompt: str, filename: str, output_dir: Path):
    """Generate a single image with custom prompt"""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    print(f"Generating: {filename}")
    print(f"Prompt: {prompt[:80]}...")

    if generate_hero_image(prompt, output_path):
        file_size = output_path.stat().st_size / 1024
        print(f"Saved: {output_path} ({file_size:.1f} KB)")
    else:
        print("Failed to generate image")
        sys.exit(1)


def list_configs():
    """List all configured images"""
    print("Configured hero images:")
    print("-" * 60)
    for i, config in enumerate(HERO_CONFIGS, 1):
        print(f"{i}. {config['filename']}")
        print(f"   {config['prompt'][:70]}...")
        print()


def main():
    parser = argparse.ArgumentParser(description="Generate blog hero images using Gemini AI")
    parser.add_argument("--list", action="store_true", help="List configured images")
    parser.add_argument("--single", type=str, help="Generate single image with custom prompt")
    parser.add_argument("--filename", type=str, default="custom-hero.png", help="Filename for single image")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Output directory")

    args = parser.parse_args()
    output_dir = Path(args.output)

    if args.list:
        list_configs()
    elif args.single:
        generate_single(args.single, args.filename, output_dir)
    else:
        generate_all(output_dir)


if __name__ == "__main__":
    main()
