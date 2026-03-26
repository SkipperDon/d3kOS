# PWA Icons Required

Before deploying to GitHub Pages, generate two PNG icons from icon.svg:

- icon-192.png — 192×192px
- icon-512.png — 512×512px

## Generate on Windows (browser method)
1. Open icon.svg in Chrome or Edge
2. Right-click → Inspect → Console
3. Paste and run:
   ```js
   const img = new Image(); img.src = 'icon.svg';
   img.onload = () => {
     [192, 512].forEach(size => {
       const c = document.createElement('canvas');
       c.width = c.height = size;
       c.getContext('2d').drawImage(img, 0, 0, size, size);
       const a = document.createElement('a');
       a.href = c.toDataURL('image/png');
       a.download = `icon-${size}.png`;
       a.click();
     });
   };
   ```
4. Save both PNG files to this folder

## Or use any image editor (Photopea, GIMP, Figma)
- Export icon.svg at 192×192 and 512×512 as PNG
