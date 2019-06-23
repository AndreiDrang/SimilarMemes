import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


def copy_image(image_full_path: str):
    """
	Get image full path and copy it to clipboard
	:param image_full_path: Image path
	:return: True if all is Ok, False if can`t copy image
	"""
    image = Gtk.Image.new_from_file(image_full_path)
    if image.get_storage_type() == Gtk.ImageType.PIXBUF:
        pixbuf = image.get_pixbuf()
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_image(pixbuf)
        clipboard.store()
        return True
    else:
        return False
