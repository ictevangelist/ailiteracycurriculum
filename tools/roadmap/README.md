# A3 road map

Built from data/curriculum.json (lessons) and strands.json (each lesson's progression strands, from the plans).

    npm install react@18.3.1 react-dom@18.3.1 react-icons@5.3.0   # once, in a scratch folder
    OUT_DIR=<dir> ICON_NODE_MODULES=<scratch>/node_modules python3 tools/roadmap/road.py
    node tools/roadmap/render.js <dir>/road.html <dir>

render.js writes the A3 PDF, a PNG for the site image (convert to webp at 2482x1754), spots.json for the site hotspots, and reports any card whose text overflows. Fonts: Exo 2 headings, Poppins everything else.
