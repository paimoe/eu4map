"""

"""
import sys, os
import delegator
import argparse
import numpy as np
from xml.dom import minidom

from PIL import Image, ImageOps

def rgb_to_hex(red, green, blue):
    return '%02x%02x%02x' % (red, green, blue)
def hex_to_rgb(hx):
    return tuple(int(hx.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))

def map_full(opts):
    """
    """
    im = Image.open(opts.input)
    base_npim = np.array(im)

    if opts.mode == 1:
        mask = Image.new('L', im.size, 'white')

    #mask.save('maskwut.bmp')
    colors = im.getcolors(maxcolors=9001)
    # sort by most common
    colors_sorted = sorted(colors, key=lambda x: x[0], reverse=True)
    #assert False
    width, height = im.size

    if os.path.exists(opts.output):
        if input('Do you want to delete the existing {}? [y/n]'.format(opts.output)) != 'y':
            print('Exiting')
            sys.exit(0)

    svg_final = open(opts.output, 'w') # check to overwrite
    svg_final.write("<?xml version='1.0' standalone='no'?><svg version='1.0' xmlns='http://www.w3.org/2000/svg'>")
    
    po_input = 'selected_new.tmp.bmp'
    po_output = 'selected_new.tmp.svg'
    # First version:
    # - loop each colour, then loop each pixel
    # - might be faster in v2, to loop each pixel, then color. ending up with 3k masks/images

    # Now for each color, loop and process
    for i, c in enumerate(colors_sorted):
        count, rgb = c
        hex = rgb_to_hex(*c[1]).upper()
        print('count {}/{} {}:{}'.format(i, len(colors_sorted), count, hex))

        # Go by pixel
        if opts.mode == 1:
            for x in range(width):
                for y in range(height):
                    px = im.getpixel((x,y))

                    if px == rgb:
                        # im.putpixel((x,y), (255,255,255))
                        # just draw on the mask?
                        mask.putpixel((x,y), 0)
                        count -= 1                 

                if count == 0: # after we've changed all applicable pixels, swift exit
                    break

        # Conver to np arrays, use masks properly
        if opts.mode == 0:
            # convert npim colors
            npim = np.copy(base_npim) # maybe try making a copy, rather than remaking it 
            _red, _green, _blue = npim[:,:,0], npim[:,:,1], npim[:,:,2]
            npmask = (_red == rgb[0]) & (_green == rgb[1]) & (_blue == rgb[2])
            npim[:,:,:3][npmask] = [0,0,0]
            npim[:,:,:3][~npmask] = [255,255,255]
            #print('type', type(npim), npim.shape)
            mask = Image.fromarray(npim, 'RGB')

        # make hex black # make the rest white

        # Now pass to potrace
        # potrace -s input -o output -t <min num pixels to render> --flat <because its all the one colour anyway, means no manual editing>
        mask.save(po_input)
        po_args = ['potrace', '--svg', '--output', po_output, '--turdsize=5', '--flat', '--margin=0', po_input]
        d = delegator.run(' '.join(po_args))

        # Now po_output will have the svg for the one province
        po = minidom.parse(po_output)

        # g element
        g = po.getElementsByTagName('g')[0]
        g.setAttribute('fill', '#' +  hex) # update colour
        g.removeAttribute('stroke')
        g.setAttribute('transform', 'translate(0,2048) scale(0.1, -0.1)') # shorten a bit

        path = g.getElementsByTagName('path')[0]
        #path.setAttribute('id', from csv)

        # put g.toxml() into our file
        svg_final.write(g.toxml())

        if i == 50:
            pass

    svg_final.write("</svg>")
    svg_final.close()

    # cleanup
    os.remove(po_input)
    os.remove(po_output)

def map_one_color(color, opts): pass
def map_province(pid, opts): pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Parse provinces.bmp into svg file', prog='eu4map')
    parser.add_argument('action', nargs='?', help='What action to perform (map))')
    parser.add_argument('focus', nargs='?', help='Pick one province to render, return the svg element')
    parser.add_argument('--input', help='provinces.bmp file', default='provinces.bmp')
    parser.add_argument('--output', help='Output to this svg file', default='parsed.svg')
    parser.add_argument('--mode', help='0= numpy arrays, 1=pixel by pixel', default=0)
    #parser.add_argument('--keep', action='store_true', help='Keep mask files (idk why)')
    
    opts = parser.parse_args()

    if not os.path.exists(opts.input):
        raise OSError('Can\'t find file "{}"'.format(opts.input))

    if opts.action == 'map':
        map_full(opts)
    elif opts.action in ['color', 'colour']:
        if opts.focus.startswith('#'):
            map_one_color(opts.focus, opts)
        else:
            print('Unknown colour: {}'.format(opts.focus))
    elif opts.action == 'province':
        map_province(opts.focus, opts)
    print(opts)