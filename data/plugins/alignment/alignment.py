from gaphor.plugin import Action

class Alignment(Action):
    def init(self, window):
	self._window = window
    
    def execute(self):
        view = self._window.get_current_diagram_view()
        items = view.selected_items
        if len(items)>1:
            view.canvas.undo_manager.begin_transaction()
            self.align(items)
            view.canvas.undo_manager.commit_transaction()
        
    def moveItemsToTarget(self, items, target_x, target_y):
        for item in items:
            if target_x is not None:
                affine=list(item.item.affine)
                x=target_x-affine[4]
            else:
                x=0
            if target_y is not None:
                affine=list(item.item.affine)
                y=target_y-affine[5]
            else:
                y=0
            item.item.move(x,y)
            
    def getXCords(self, items):
        return [item.item.affine[4] for item in items]

    def getYCords(self, items):
        return [item.item.affine[5] for item in items]

    def align(self, items):
        pass

class AlignVertical(Alignment):
    def align(self, items):
        target_x=min(self.getXCords(items))
        target_y=None
        self.moveItemsToTarget(items, target_x, target_y)

class AlignHorizontal(Alignment):
    def align(self, items):
        target_y=min(self.getYCords(items))
        target_x=None
        self.moveItemsToTarget(items, target_x, target_y)

