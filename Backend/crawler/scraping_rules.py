SCRAPING_RULES = {
    "default": {
        "name": {"type": "tag", "value": "h1"},
        "price": {"type": "css", "value": "span[data-product-price]"},
        "description": {"type": "css", "value": "div.product__description.rte"},
        "image": {"type": "css", "value": "img.photoswipe__image"},
    },
    "website1.com": {
        "name": {"type": "css", "value": "div.product-block--header h1"},
        "price": {"type": "css", "value": "div.price__regular span.price-item--regular"},
        "description": {"type": "css", "value": "div.rte"},
        "image": {"type": "css", "value": "div.product__media img"},
    },
    "website2.com": {
        "name": {"type": "css", "value": "div.product__title h1"},
        "price": {"type": "css", "value": "span.price-item--regular"},
        "description": {"type": "css", "value": "div.product__description.rte"},
        "image": {"type": "css", "value": "img.product-image"},
    },
    "website3.com": {
        "name": {"type": "css", "value": "div.product__title h1"},
        "price": {"type": "css", "value": "span.price-item--regular"},
        "description": {"type": "css", "value": "div.product__description.rte"},
        "image": {"type": "css", "value": "img.product-image"},
    },
}
