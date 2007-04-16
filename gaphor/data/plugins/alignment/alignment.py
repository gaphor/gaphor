
from gaphor.core import transactional
from gaphor.plugin import Action


class Alignment(Action):

    def init(self, window):
	self._window = window
    
    def update(self):
        diagram_tab = self.get_window().get_current_diagram_tab()
        self.sensitive = diagram_tab and len(diagram_tab.get_view().selected_items) > 0

    @transactional
    def execute(self):
        view = self._window.get_current_diagram_view()
        items = view.selected_items
        if len(items)>1:
            self.align(items)
        
    def moveItemsToTarget(self, items, target_x, target_y):
        for item in items:
            if target_x is not None:
                x = target_x - item.matrix[4]
            else:
                x = 0
            if target_y is not None:
                y = target_y - item.matrix[5]
            else:
                y = 0
            item.matrix.translate(x,y)
            item.request_update()
            
    def align(self, items):
        pass


class AlignVertical(Alignment):
	
    def getXCoords(self, items):
        return [item.matrix[4] for item in items]

    def align(self, items):
        target_x=min(self.getXCoords(items))
        target_y=None
        self.moveItemsToTarget(items, target_x, target_y)


class AlignHorizontal(Alignment):

    def getYCoords(self, items):
        return [item.matrix[5] for item in items]

    def align(self, items):
        target_y=min(self.getYCoords(items))
        target_x=None
        self.moveItemsToTarget(items, target_x, target_y)

# vim:sw=4:et:ai
