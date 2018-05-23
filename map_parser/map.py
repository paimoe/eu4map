"""

"""
import sys
import delegator
import argparse
import numpy as np
from xml.dom import minidom

from PIL import Image, ImageOps

def rgb_to_hex(red, green, blue):
    return '%02x%02x%02x' % (red, green, blue)
def hex_to_rgb(hx):
    return tuple(int(hx.lstrip('#')[i:i+2], 16) for i in (0, 2 ,4))

def map_full():
    """
    """
    im = Image.open('provinces.bmp')

    npim = np.array(im)
    print('shape of npim', npim.shape)
    #assert im.size == npim.size and im.mode == npim.mode

    mask = Image.new('L', im.size, 'white')
    #mask.save('maskwut.bmp')
    colors = im.getcolors(maxcolors=9001)
    # sort by most common
    colors_sorted = sorted(colors, key=lambda x: x[0], reverse=True)
    #assert False
    width, height = im.size

    svg_final = open('parsed.svg', 'w') # check to overwrite
    svg_final.write("<?xml version='1.0' standalone='no'?><svg version='1.0' xmlns='http://www.w3.org/2000/svg'>")

    # First version:
    # - loop each colour, then loop each pixel
    # - might be faster in v2, to loop each pixel, then color. ending up with 3k masks/images

    # Now for each color, loop and process
    TESTMODE = 0
    for i, c in enumerate(colors_sorted):
        count, rgb = c
        hex = rgb_to_hex(*c[1]).upper()
        print('count {}/{} {}:{}'.format(i, len(colors_sorted), count, hex))

        # Go by pixel?
        if TESTMODE == 1:
            for x in range(width):
                for y in range(height):
                    px = im.getpixel((x,y))

                    if px == rgb:
                        #im.putpixel((x,y), (255,255,255))
                        # just draw on the mask?
                        mask.putpixel((x,y), 0)
                        count -= 1                 

                if count == 0: # after we've changed all applicable pixels, swift exit
                    break
        if TESTMODE == 0:
            # convert npim colors
            #to_black = npim[np.where((npim == rgb).all(axis=2))] = np.zeros(3)
            #to_black = npim[np.where(npim == rgb)] = [0,0,0]
            npim = np.array(im) # maybe try making a copy, rather than remaking it 
            _red, _green, _blue = npim[:,:,0], npim[:,:,1], npim[:,:,2]
            npmask = (_red == rgb[0]) & (_green == rgb[1]) & (_blue == rgb[2])
            npim[:,:,:3][npmask] = [0,0,0]
            npim[:,:,:3][~npmask] = [255,255,255]
            #to_black.reshape()
            #print('type', type(npim), npim.shape)
            mask = Image.fromarray(npim, 'RGB')

        # make hex black # make the rest white

        # Now pass to potrace
        # potrace -s input -o output -t <min num pixels to render> --flat <because its all the one colour anyway, means no manual editing>
        po_input = 'selected_new.tmp.bmp'
        po_output = 'selected_new.tmp.svg'
        mask.save(po_input)
        po_args = ['potrace', '--svg', '--output', po_output, '--turdsize=5', '--flat', '--margin=0', po_input]
        d = delegator.run(' '.join(po_args))
        #print(' '.join(po_args))

        # Now po_output will have the svg for the one province
        po = minidom.parse(po_output)

        # g element
        g = po.getElementsByTagName('g')[0]
        g.setAttribute('fill', '#' +  hex) # update colour
        g.removeAttribute('stroke')
        g.setAttribute('transform', 'translate(0,2048) scale(0.1, -0.1)') # shorten a bit

        path = g.getElementsByTagName('path')[0]
        #path.setAttribute('id', from csv)

        #print(g.toxml())
        # put g.toxml() into our file
        svg_final.write(g.toxml())

        # end of loop, reset mask
        #mask = Image.new('L', im.size, 'white')

        if i == 50:
            pass
        #    # save temp
        #    #mask.save('maskwut.bmp')
        #    break
    svg_final.write("</svg>")
    svg_final.close()

    # rm po_input, po_output

def map_one_color(color): pass
def map_province(pid): pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Parse provinces.bmp into svg file', prog='eu4map')
    parser.add_argument('action', nargs='?', help='What action to perform (map))')
    parser.add_argument('focus', nargs='?', help='Depends on action, province ID, country tag, to limit to test')

    #parser.add_argument('--keep', action='store_true', help='Keep mask files (idk why)')
    
    opts = parser.parse_args()

    if opts.action == 'map':
        map_full()