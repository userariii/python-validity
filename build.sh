#!/bin/bash
set -e

OUTPUT_DIR="output"

echo "🧹 Cleaning old output directory..."
rm -rf "$OUTPUT_DIR"

echo "📁 Creating fresh output directory..."
mkdir -p "$OUTPUT_DIR"

echo "🔨 Building python-validity package..."
dpkg-buildpackage -us -uc -b

echo "📦 Moving build artifacts into $OUTPUT_DIR/..."

mv ../python3-validity_*.deb "$OUTPUT_DIR/" 2>/dev/null || true
mv ../python-validity_*.changes "$OUTPUT_DIR/" 2>/dev/null || true
mv ../python-validity_*.buildinfo "$OUTPUT_DIR/" 2>/dev/null || true

echo
echo "✅ Build complete."
echo "📂 Output files:"
ls -lh "$OUTPUT_DIR"