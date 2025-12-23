const scrape = require('website-scraper');
const axios = require('axios');
const cheerio = require('cheerio');
const path = require('path');
const fs = require('fs');

const url = process.argv[2];
const outputDir = process.argv[3] || 'dist';

if (!url) {
    console.error('Please provide a URL as the first argument.');
    process.exit(1);
}

async function identifySite(targetUrl) {
    console.log(`Identifying site: ${targetUrl}`);
    try {
        const response = await axios.get(targetUrl);
        const $ = cheerio.load(response.data);

        // Detect WordPress
        const isWordPress = $('meta[name="generator"]').attr('content')?.toLowerCase().includes('wordpress') ||
            $('link[rel="https://api.w.org/"]').length > 0 ||
            response.data.includes('wp-content') ||
            response.data.includes('wp-includes');

        if (isWordPress) return 'WordPress';

        // Detect Shopify
        const isShopify = response.data.includes('shopify') || response.data.includes('cdn.shopify.com');
        if (isShopify) return 'Shopify';

        return 'Generic HTML';
    } catch (error) {
        console.error(`Error identifying site: ${error.message}`);
        return 'Unknown';
    }
}

async function scrapeSite(targetUrl, directory) {
    const siteType = await identifySite(targetUrl);
    console.log(`Detected Site Type: ${siteType}`);

    const options = {
        urls: [targetUrl],
        directory: path.resolve(directory),
        recursive: false,
        request: {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
    };

    if (fs.existsSync(directory)) {
        console.log(`Cleaning existing directory: ${directory}`);
        fs.rmSync(directory, { recursive: true, force: true });
    }

    try {
        console.log(`Starting scrape of ${targetUrl}...`);

        const scraperFunc = typeof scrape === 'function' ? scrape : scrape.default;

        if (typeof scraperFunc !== 'function') {
            throw new Error(`Scraper is not a function. Type of scrape: ${typeof scrape}, Type of scraperFunc: ${typeof scraperFunc}`);
        }

        await scraperFunc(options);
        console.log(`Scrape completed successfully. Files saved to ${directory}`);

        fs.writeFileSync(path.join(directory, '.scraper-metadata.json'), JSON.stringify({
            url: targetUrl,
            siteType,
            scrapedAt: new Date().toISOString()
        }));

    } catch (error) {
        console.error(`Scraping failed: ${error.message}`);
        console.error(error);
        process.exit(1);
    }
}

scrapeSite(url, outputDir);
