"""Download the reviewed licensed photographs and generate local WebP/credits."""
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import html
from io import BytesIO, StringIO
import json
from pathlib import Path
import subprocess
import threading
import time
from urllib.parse import urlparse

import httpx
from PIL import Image, ImageChops, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'apps/web/public'
ASSETS = PUBLIC / 'images/products'
ABO = 'https://amazon-berkeley-objects.s3.amazonaws.com/'
Image.MAX_IMAGE_PIXELS = 40_000_000
WIKIMEDIA_LOCK = threading.Lock()


def download(url, maximum=20_000_000):
    assert urlparse(url).hostname in {'amazon-berkeley-objects.s3.amazonaws.com', 'upload.wikimedia.org'}
    if urlparse(url).hostname == 'upload.wikimedia.org':
        # Wikimedia accepts this project's Node fetch transport; its Python
        # HTTP transport receives 403 for these same public, licensed files.
        script = '''const response = await fetch(process.argv[1], {signal: AbortSignal.timeout(55000)});
if (response.status === 429) {console.error(JSON.stringify({retryAfter:response.headers.get('retry-after')})); process.exit(75);}
if (!response.ok) throw new Error(`Public image returned HTTP ${response.status}`);
let length = 0; const chunks = [];
for await (const chunk of response.body) { length += chunk.length; if (length > Number(process.argv[2])) throw new Error('Image too large'); chunks.push(Buffer.from(chunk)); }
process.stdout.write(Buffer.concat(chunks));'''
        with WIKIMEDIA_LOCK:
            for attempt in range(2):
                response = subprocess.run(['node', '--input-type=module', '-e', script, url, str(maximum)],
                                          capture_output=True, timeout=60)
                if response.returncode == 75 and attempt == 0:
                    retry = json.loads(response.stderr).get('retryAfter')
                    delay = int(retry) if retry and str(retry).isdigit() else 90
                    if delay > 180:
                        raise RuntimeError('Wikimedia asks for a longer wait; rerun the importer later')
                    time.sleep(max(30, delay))
                    continue
                response.check_returncode()
                time.sleep(12)  # Sequential, conservative requests to Wikimedia.
                return response.stdout
    with httpx.Client(timeout=60, follow_redirects=False, headers={'User-Agent': 'PayFoundDemoImageCurator/1.0'}) as client:
        with client.stream('GET', url) as response:
            response.raise_for_status()
            body = bytearray()
            for chunk in response.iter_bytes():
                body.extend(chunk)
                if len(body) > maximum:
                    raise ValueError('Photo source exceeds the bounded download limit')
    return bytes(body)


def main():
    catalogue = json.loads((ROOT / 'apps/api/app/demo_photos.json').read_text())
    products = catalogue['products']
    expanded = ROOT / 'apps/api/app/demo_catalogue.json'
    if expanded.exists():
        products = products + json.loads(expanded.read_text())['products']
    wanted = {p['image_id'] for p in products if p.get('image_id')}
    index = csv.DictReader(StringIO(gzip.decompress(download(ABO + 'images/metadata/images.csv.gz')).decode()))
    paths = {row['image_id']: row['path'] for row in index if row['image_id'] in wanted}
    assert set(paths) == wanted, 'Every selected image must exist in the licensed ABO image index'
    ASSETS.mkdir(parents=True, exist_ok=True)
    old_manifest = ASSETS / 'manifest.json'
    previous = {p['id']: p for p in json.loads(old_manifest.read_text())['products']} if old_manifest.exists() else {}

    def prepare(product):
        product = dict(product)
        if product.get('image_id'):
            product.update(source='Amazon Berkeley Objects', source_title=product['name'], author='Amazon.com',
                source_url=ABO + 'index.html', source_metadata_url=ABO + 'listings/metadata/',
                download_url=ABO + 'images/original/' + paths[product['image_id']],
                license='CC BY 4.0', license_url='https://creativecommons.org/licenses/by/4.0/')
        output = ASSETS / (product['id'] + '.webp')
        prior = previous.get(product['id'], {})
        original_digest = prior.get('original_sha256')
        reusable = output.exists() and prior.get('download_url') == product['download_url'] and (
            prior.get('asset_sha256') == hashlib.sha256(output.read_bytes()).hexdigest())
        if reusable:
            with Image.open(output) as existing:
                existing.verify()
        else:
            original = download(product['download_url'])
            original_digest = hashlib.sha256(original).hexdigest()
            transform(original, output)
        asset = output.read_bytes()
        product.update(image_url='/images/products/' + output.name, width=600, height=600, bytes=len(asset),
            original_sha256=original_digest, asset_sha256=hashlib.sha256(asset).hexdigest(),
            changes='Near-white outer margins trimmed; resized and centered on a white square; converted to WebP. No generated imagery.',
            derivative_license=product['license'])
        return product

    def transform(original, output):
        with Image.open(BytesIO(original)) as opened:
            image = ImageOps.exif_transpose(opened)
            if image.mode in ('RGBA', 'LA') or 'transparency' in image.info:
                background = Image.new('RGBA', image.size, 'white')
                background.alpha_composite(image.convert('RGBA'))
                image = background.convert('RGB')
            else:
                image = image.convert('RGB')
            # Remove only near-white outer margins; preserve the photographed
            # object and its shadows. All transformations are disclosed below.
            difference = ImageChops.difference(image, Image.new('RGB', image.size, 'white')).convert('L')
            bounds = difference.point(lambda v: 255 if v > 18 else 0).getbbox()
            if bounds:
                image = image.crop(bounds)
            image.thumbnail((530, 530), Image.Resampling.LANCZOS)
            canvas = Image.new('RGB', (600, 600), 'white')
            canvas.paste(image, ((600 - image.width) // 2, (600 - image.height) // 2))
            canvas.save(output, 'WEBP', quality=86, method=6)

    with ThreadPoolExecutor(max_workers=4) as pool:
        photos = list(pool.map(prepare, products))
    manifest = {'generated_at': datetime.now(timezone.utc).isoformat(), 'dataset_url': catalogue['dataset_url'],
                'copyright': 'Amazon Berkeley Objects © Amazon.com; Wikimedia photographs credited individually.',
                'abo_dataset_builders': ['Matthieu Guillaumin', 'Thomas Dideriksen', 'Kenan Deng', 'Himanshu Arora',
                    'Arnab Dhua', 'Xi (Brian) Zhang', 'Tomas Yago-Vicente', 'Jasmine Collins', 'Shubham Goel', 'Jitendra Malik'],
                'products': photos}
    (ASSETS / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    # Remove only obsolete derivatives we generated and whose bytes still
    # match the previous manifest; preserve any unknown/user-edited files.
    for pid in set(previous) - {p['id'] for p in photos}:
        obsolete = ASSETS / (pid + '.webp')
        if obsolete.exists() and hashlib.sha256(obsolete.read_bytes()).hexdigest() == previous[pid].get('asset_sha256'):
            obsolete.unlink()
    (ASSETS / 'LICENSE-CC-BY-4.0.txt').write_bytes(download(ABO + 'LICENSE-CC-BY-4.0.txt'))
    esc = html.escape
    cards = []
    for photo in photos:
        cards.append(f'<article id="{esc(photo["id"])}"><img src="{esc(photo["image_url"])}" alt="{esc(photo["name"])}" loading="lazy" width="180" height="180"><div><h2>{esc(photo["name"])}</h2><p>Photo: {esc(photo["author"])} · {esc(photo["source"])}</p><p><a href="{esc(photo["source_url"])}">Source and original licensing</a> · <a href="{esc(photo["download_url"])}">Original photograph</a> · <a href="{esc(photo["license_url"])}">{esc(photo["license"])}</a></p><p>{esc(photo["changes"])}</p><p>Distributed image and any image adaptations retain {esc(photo["derivative_license"])}.</p><small>Product {esc(photo["id"])}{(" · ABO item " + esc(photo["item_id"]) + " · image " + esc(photo["image_id"])) if photo.get("item_id") else ""}</small></div></article>')
    document = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Product image credits · PayFound</title><style>body{font:15px/1.7 system-ui,sans-serif;color:#20383d;background:#f4f7f6;margin:0}main{max-width:1000px;margin:auto;padding:40px 24px}h1{font-size:36px;letter-spacing:-1px;line-height:1.2}h2{font-size:18px}a{color:#07569c}header{margin-bottom:34px}header>p{max-width:850px;color:#657d7c}.links{display:flex;flex-wrap:wrap;gap:20px}article{background:white;border:1px solid #e0e9e4;border-radius:12px;padding:22px;margin:16px 0;display:flex;gap:26px;align-items:center}article img{object-fit:contain;flex-shrink:0}article p{font-size:12px;color:#718480;margin:6px 0}small{font-size:10px;color:#899a93;overflow-wrap:anywhere}@media(max-width:600px){article{display:block}article img{display:block;margin:auto}h1{font-size:28px}}</style></head><body><main><header><div class="links"><a href="/">PayFound</a><a href="/pos/sell">POS simulator</a><a href="/images/products/manifest.json">Image manifest</a></div><h1>Real photographs. Clear credits.</h1><p>Product photographs in this demo come from the Amazon Berkeley Objects catalogue-image dataset and individually licensed Wikimedia Commons photographs. Product names were adjusted to describe the pictured products. Stores, prices, availability and transactions remain fictional demonstration data. Photography does not imply endorsement or a live merchant relationship.</p><p>ABO data and images: © Amazon.com, licensed CC BY 4.0. Dataset creation: ' + esc(', '.join(manifest['abo_dataset_builders'])) + '. <a href="https://amazon-berkeley-objects.s3.amazonaws.com/index.html">Dataset and attribution</a> · <a href="/images/products/LICENSE-CC-BY-4.0.txt">License text and disclaimer of warranties</a>.</p></header>' + ''.join(cards) + '</main></body></html>'
    (PUBLIC / 'image-credits.html').write_text(document)
    contact = Image.new('RGB', (1200, ((len(photos) + 5) // 6) * 215), '#edf2ef')
    painter = ImageDraw.Draw(contact)
    for i, photo in enumerate(photos):
        with Image.open(ASSETS / (photo['id'] + '.webp')) as tile:
            tile.thumbnail((182, 182))
            x, y = (i % 6) * 200 + 9, (i // 6) * 215 + 5
            contact.paste(tile, (x, y))
            painter.text((x, y + 185), photo['id'], fill='#213e39')
    contact.save(ROOT / 'docs/evidence/product-photo-contact-sheet.jpg')
    print(json.dumps({'photos': len(photos), 'total_webp_bytes': sum(p['bytes'] for p in photos),
                      'sources': sorted({p['source'] for p in photos}), 'credits': '/image-credits.html'}, indent=2))


if __name__ == '__main__':
    main()
