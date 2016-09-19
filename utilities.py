
def format_text(name):
    return name.replace('_', ' ').upper()

def get_zoom_area(zoom_level):
    w = h = 1 / zoom_level
    x = y = (1 - w) / 2
    return (x, y, w, h)
