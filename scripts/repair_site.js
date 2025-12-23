const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

const directory = process.argv[2];

if (!directory) {
    console.error('Please provide a directory to repair.');
    process.exit(1);
}

const repairCss = `
/* Repair CSS for Static Export */
.fluid-width-video-wrapper {
    width: 100%;
    position: relative;
    padding: 0;
    padding-top: 56.25%; /* 16:9 Aspect Ratio */
}
.fluid-width-video-wrapper iframe,
.fluid-width-video-wrapper object,
.fluid-width-video-wrapper embed {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
`;

function repairHtmlFile(filePath) {
    console.log(`Repairing: ${filePath}`);
    const content = fs.readFileSync(filePath, 'utf8');
    const $ = cheerio.load(content);

    if (!$('style#repair-css').length) {
        $('head').append(`<style id="repair-css">${repairCss}</style>`);
    }

    $('iframe[src*="youtube.com"], iframe[src*="vimeo.com"]').each((i, el) => {
        const $iframe = $(el);
        if (!$iframe.parent().hasClass('fluid-width-video-wrapper')) {
            $iframe.wrap('<div class="fluid-width-video-wrapper"></div>');
        }
    });

    fs.writeFileSync(filePath, $.html());
}

function walkDir(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            walkDir(fullPath);
        } else if (file.endsWith('.html')) {
            repairHtmlFile(fullPath);
        }
    }
}

console.log(`Starting automated repair in ${directory}...`);
if (fs.existsSync(directory)) {
    walkDir(directory);
    console.log('Automated repair completed.');
} else {
    console.error(`Directory ${directory} does not exist.`);
    process.exit(1);
}
