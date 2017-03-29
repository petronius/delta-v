# """
# View for the 'Load game' screen.
# """

# import os
# import pyglet

# import blackmango.system
# import blackmango.ui.labels
# import blackmango.ui.views
# import blackmango.ui.views.game
# import blackmango.ui.views.main_menu

# from blackmango.configure import COLORS
# from blackmango.ui import keyboard

# TITLE_COLOR = COLORS['secondary-a-5']
# MENU_ITEM_COLOR = COLORS['primary-4']
# SELECTED_COLOR = COLORS['secondary-b-5']
# ERROR_COLOR=(255,0,0,255)

# class LoadGameView(blackmango.ui.views.BaseView):
    
#     def __init__(self):

#         savedir = blackmango.system.DIR_SAVEDGAMES
#         savefiles = os.listdir(savedir)
#         savefiles = filter(lambda x: x.endswith('.blackmango'), savefiles)

#         self.batch = pyglet.graphics.Batch()

#         self.menu_options = []
#         for f in savefiles:
#             name = f[:-11]
#             if len(name) > 55:
#                 name = '%s...' % name[:52]
#             f = os.path.join(savedir, f)
#             self.menu_options.append((name, f))
#         self.menu_items = []

#         self.title = MenuTitle('Load game', batch = self.batch)
#         offset = 0

#         x, y = blackmango.ui.game_window.get_size()
#         self.labelset = blackmango.ui.labels.ScrollableLabelSet(
#             width = x,
#             height = y - 220,
#             anchor_x = 1,
#             anchor_y = y - 120,
#         )
        
#         for option, s in self.menu_options:
#             label = MenuLabel(option, self.batch, offset)
#             label.action = lambda : self.load_game(s)
#             self.menu_items.append(label)
#             self.labelset.add(label)
#             offset += 1

#         #cancel = MenuLabel('Cancel', offset, batch = self.batch)
#         #cancel.action = self.cancel_action
#         #self.menu_items.append(cancel)
#         #self.labelset.add(cancel)

#         self.selected = 0
#         self.set_selected(0)

#         self.errors = []
#         self.logger = blackmango.configure.logger

#     def destroy(self):
#         for i in self.menu_items:
#             i.delete()
#         self.title.delete()

#     def load_game(self, savefile):
#         # Check the save version before we attempt to start up a game
#         with open(savefile) as f:
#             versioninfo = f.readline().strip()
#             if versioninfo != blackmango.configure.SAVE_GAME_VERSION:
#                 self.logger.debug("Version mistmatch error opening file: %s" \
#                         % savefile)
#                 self.open_error()
#                 return
#         from blackmango.ui.views.game import GameView
#         blackmango.ui.game_window.set_view(GameView(savefile))

#     def open_error(self):
#         error = ErrorLabel("File can't be opened due to save version mismatch",
#             batch = self.batch)
#         self.errors.append(error)

#     def clear_errors(self):
#         for error in self.errors:
#             error.delete()

#     def cancel_action(self):
#         from blackmango.ui.views.main_menu import MainMenuView
#         blackmango.ui.game_window.set_view(MainMenuView())
           
#     def set_selected(self, i):
#         self.labelset.set_selected(i, MENU_ITEM_COLOR)
#         # Handled by the labelse
#         #self.menu_items[self.selected].color = MENU_ITEM_COLOR
#         self.selected = i
#         self.menu_items[i].color = SELECTED_COLOR

#     def select_next(self):
#         s = self.selected
#         s += 1
#         if s > len(self.menu_items) - 1:
#             s = 0
#         for i in self.menu_items:
#             i.y += i.content_height
#         self.set_selected(s)

#     def select_prev(self):
#         s = self.selected
#         s -= 1
#         if s < 0:
#             s = len(self.menu_items) - 1
#         for i in self.menu_items:
#             i.y -= i.content_height
#         self.set_selected(s)

#     def on_draw(self):
#         self.batch.draw()

#     def get_intersecting_menu_item(self, x, y):
#         # If the mouse intersects with any menu items, select them
#         for idx, item in enumerate(self.menu_items):
#             if hasattr(item, 'visible') and not item.visible:
#                 continue
#             # Assuming menu items are top- and right-anchored, but if that 
#             # changes then we need to change this line
#             if x < item.x + 1 and x > item.x - item.content_width - 1 and \
#                y < item.y + 1 and y > item.y - item.content_height - 1:
#                 return idx, item
#         else:
#             return -1, None

#     def on_mouse_motion(self, x, y, dx, dy):
#         idx, item = self.get_intersecting_menu_item(x, y)
#         if item:
#             self.set_selected(idx)
#         return

#     def on_mouse_press(self, x, y, button, modifiers):
#         self.clear_errors()
#         idx, item = self.get_intersecting_menu_item(x, y)
#         if button == 1 and item:
#             item.action()

#     def tick(self):
#         pass

#     def on_key_press(self, k, modifiers):

#         self.clear_errors()
        
#         if keyboard.check('menu_move_up'):
#             self.select_prev()
        
#         elif keyboard.check('menu_move_down'):
#             self.select_next()

#         elif keyboard.check('menu_select'):
#             self.menu_items[self.selected].action()

#         elif keyboard.check('menu_cancel'):
#             self.cancel_action()

# class MenuTitle(pyglet.text.Label):

#     def __init__(self, title, batch):

#         x, y = blackmango.ui.game_window.get_size()

#         super(MenuTitle, self).__init__(
#             title,
#             font_name = 'Chapbook',
#             font_size = 52,
#             x = x // 2,
#             y = y - (y // 4),
#             anchor_x = 'right',
#             anchor_y = 'center',
#             batch = batch,
#             color = TITLE_COLOR,
#         )

# class MenuLabel(pyglet.text.Label):

#     def __init__(self, title, batch, offset = 0):

#         x, y = blackmango.ui.game_window.get_size()

#         offset += 1
#         offset *= .4

#         super(MenuLabel, self).__init__(
#             title,
#             font_name = 'Prociono TT',
#             font_size = 18, 
#             x = x - 140,
#             y = y - 180 - 100*offset,
#             anchor_x = 'right',
#             anchor_y = 'top',
#             batch = batch,
#             color = MENU_ITEM_COLOR,
#         )

# class ErrorLabel(pyglet.text.Label):

#     def __init__(self, title, batch):

#         x, y = blackmango.ui.game_window.get_size()

#         super(ErrorLabel, self).__init__(
#             title,
#             font_name = 'Prociono TT',
#             font_size = 18, 
#             x = x//2,
#             y = y - (y - 40),
#             anchor_x = 'center',
#             anchor_y = 'center',
#             batch = batch,
#             color = ERROR_COLOR, 
#         )
