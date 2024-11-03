"""
解析URL中product id
"""

'''
https://www.amazon.com/dp/B0D266JS5H
https://www.amazon.com/dp/B0BNNCYW7P?ref=myi_title_dp
'''
def amazon_url_parser(link):
    product_id = link.split("dp/")[1].split("?")[0].strip()
    return product_id

'''
https://www.wayfair.com/office-storage-cabinets/pdp/wade-logan-belak-63-wide-office-storage-cabinets-w110297593.html
https://www.wayfair.com/desks/pdp/wade-logan-bernarrdetta-63-w-l-shaped-lift-desk-w110304578.html?piid=1282191077
'''
def wayfair_url_parser(link):
    product_id = link.split(".html")[0].split("-")[-1].strip()
    return product_id

'''
https://www.walmart.com/ip/2839719289
'''
def walmart_url_parser(link):
    link = link.split('?')[0].split('#')[0]
    product_id = link.split('ip/')[-1].strip()
    return product_id

'''
https://www.homedepot.com/p/FUFU-GAGA-5-Drawers-White-Makeup-Vanity-Sets-Dressing-Table-Sets-with-LED-Dimmable-Mirror-Stool-and-3-Tier-Storage-Shelves-KF210141-01/318504099
'''
def homedepot_url_parser(link):
    link = link.split('?')[0].split('#')[0]
    product_id = link.split('/')[-1].strip()
    return product_id

'''
https://www.overstock.com/Home-Garden/1-Panel-Cabinet-Iron-Fireplace-Screen/34166905/product.html?option=64407264
https://www.bedbathandbeyond.com/c/storage-furniture/bookshelves?t=24446&featuredproduct=37837477
'''
def overstock_url_parser(link):
    product_id = -1
    if link.find('/product.html') > -1:
        link = link.split('?')[0].split('#')[0]
        product_id = link.split('/')[-2].strip()
    elif link.find('featuredproduct=') > -1:
        product_id = link.split('featuredproduct=')[-1].strip().split('&')[0].strip()
    return product_id

'''
https://www.lowes.com/pd/FUFU-GAGA-3-Blades-Retro-Wood-Ceiling-Fan/5015392509?idProductFound=false&idExtracted=true
https://www.lowes.com/pd/MIDHAM-Composite-Indoor-Outdoor-Large-Dog-House/5015479007?idProductFound=false&idExtracted=true
'''
def lowes_url_parser(link):
    link = link.split('?')[0].split('#')[0]
    product_id = link.split('/')[-1].strip()
    return product_id

