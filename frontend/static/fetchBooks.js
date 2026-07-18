const fs = require('fs');

async function downloadBook(url, filename) {
    console.log(`Starting download for ${filename}...`);
    try {
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            }
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const arrayBuffer = await response.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);
        fs.writeFileSync(filename, buffer);
        console.log(`Successfully downloaded ${filename}`);
    } catch (e) {
        console.error(`Failed to download ${filename}:`, e.message);
    }
}

async function main() {
    // Download Brihat Parashara Hora Shastra
    await downloadBook(
        "https://archive.org/download/BrihatParasaraHoraShastraByR.Santhanam/Brihat%20Parasara%20Hora%20Shastra%20by%20R.%20Santhanam.pdf", 
        "f:/Atro/Books/Brihat_Parashara.pdf"
    );
    // Download Phaladeepika
    await downloadBook(
        "https://archive.org/download/PhaladeepikaByDr.G.S.Kapoor/Phaladeepika%20by%20Dr.%20G.%20S.%20Kapoor.pdf", 
        "f:/Atro/Books/Phaladeepika.pdf"
    );
}

main();
