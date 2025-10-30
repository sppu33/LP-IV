from PIL import Image

def embed_text_in_image(infile, outfile, text):
    img = Image.open(infile).convert('RGB')
    data = ''.join([format(ord(c), '08b') for c in text]) + '00000000'  # terminator
    arr = img.copy()
    pixels = arr.load()
    w, h = arr.size
    idx = 0
    for y in range(h):
        for x in range(w):
            if idx >= len(data):
                break
            r,g,b = pixels[x,y]
            rb = list(map(int, format(r, '08b')))
            gb = list(map(int, format(g, '08b')))
            bb = list(map(int, format(b, '08b')))
            # embed in R channel LSB (for simplicity)
            rb[-1] = int(data[idx]); idx += 1
            if idx < len(data):
                gb[-1] = int(data[idx]); idx += 1
            if idx < len(data):
                bb[-1] = int(data[idx]); idx += 1
            nr = int(''.join(map(str, rb)),2)
            ng = int(''.join(map(str, gb)),2)
            nb = int(''.join(map(str, bb)),2)
            pixels[x,y] = (nr,ng,nb)
        if idx >= len(data):
            break
    arr.save(outfile)

# Usage
embed_text_in_image('7.png','stego.jpg','SecretMessage123')
print("Text embedded in image 'stego.jpg'")