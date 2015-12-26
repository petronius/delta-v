"""
Text and label classes shared by more than one view or submodule. Many define
their own, but a few have more various utility.
"""

import pyglet

title_batch = pyglet.graphics.Batch()

class ScrollableLabelSet(object):
    """
    A quick and dirty class for handling sets of scrolling labels.

    - If the anchor points are outside of the set's box, they become hidden.
    - If a label becomes selected that is outside of the box, all labels are
      scrolled until it is inside the box.
    """

    def __init__(self,
        width,
        height,
        anchor_x,
        anchor_y):

        self.width = width
        self.height = height
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y

        self.bounds = {
            'left': anchor_x,
            'right': anchor_x + width,
            'top': anchor_y,
            'bottom': anchor_y - height,
        }

        self.labels = []

    def add(self, label):
        self.labels.append(label)

    def remove(self, label):
        self.labels = filter(lambda x: x is not label, self.labels)

    def set_selected(self, i, reset_color):
        selected = self.labels[i]
        while selected.y < self.bounds['bottom']:
            for i in self.labels:
                i.y += 1
        while selected.y > self.bounds['top']:
            for i in self.labels:
                i.y -= 1
        while selected.x < self.bounds['left']:
            for i in self.labels:
                i.x += 1
        while selected.x > self.bounds['right']:
            for i in self.labels:
                i.x -= 1

        for i in self.labels:
            if i.y < self.bounds['bottom']:
                i.visible = False
            elif i.y > self.bounds['top']:
                i.visible = False
            elif i.x < self.bounds['left']:
                i.visible = False
            elif i.x > self.bounds['right']:
                i.visible = False
            else:
                i.visible = True

            # Manually hide labels that are 'visible = False' by setting 100%
            # transparency
            if hasattr(i, 'visible') and not i.visible:
                i.color = i.color[:-1] + (0,)
            elif hasattr(i, 'visible') and i.visible:
                i.color = reset_color

class TextBox(pyglet.text.Label):
    """
    Text with an accompanying border box behind.
    """

    def __init__(self, title, 
            padding = 15,
            box_color = (0,0,0,255),
            text_color = (255,255,255,255),
            position = 'center',
            font_size = 15,
        ):

        import blackmango.ui

        x, y = blackmango.ui.game_window.get_size()

        if position == 'center':
            x //= 2
            y //= 2
            anchor_x = anchor_y = 'center'
        elif position == 'bottom':
            x //= 2
            y //= 6
            anchor_x = 'center'
            anchor_y = 'bottom'
        else: raise ValueError('Bad position value')

        super(TextBox, self).__init__(
            title,
            font_name = 'Prociono TT',
            #font_name = 'Chapbook',
            font_size = font_size, 
            x = x,
            y = y,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            batch = title_batch,
            color = text_color,
        )

        w_2, h_2 = self.content_width / 2, self.content_height / 2
        w_2 += padding
        h_2 += padding
        x1, x2 = self.x - w_2, self.x + w_2
        if anchor_y == 'center':
            y1, y2 = self.y - h_2, self.y + h_2
        elif anchor_y == 'bottom':
            y1, y2 = self.y - padding, self.y + self.content_height + padding

        self.borderbox = title_batch.add(4, pyglet.gl.GL_QUADS, None,
            ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
            ('c4B', list(box_color) * 4)
        )

    def delete(self):
        self.borderbox.delete()
        super(TextBox, self).delete()
