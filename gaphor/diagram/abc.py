import abc


class EditorBase(metaclass=abc.ABCMeta):
    """
    Provide an interface for editing text with the TextEditTool.
    """

    @abc.abstractmethod
    def is_editable(self, x, y):
        """
        Is this item editable in it's current state.
        x, y represent the cursors (x, y) position.
        (this method should be called before get_text() is called.
        """

    @abc.abstractmethod
    def get_text(self):
        """
        Get the text to be updated
        """

    @abc.abstractmethod
    def get_bounds(self):
        """
        Get the bounding box of the (current) text. The edit tool is not
        required to do anything with this information but it might help for
        some nicer displaying of the text widget.

        Returns: a gaphas.geometry.Rectangle
        """

    @abc.abstractmethod
    def update_text(self, text):
        """
        Update with the new text.
        """

    @abc.abstractmethod
    def key_pressed(self, pos, key):
        """
        Called every time a key is pressed. Allows for 'Enter' as escape
        character in single line editing.
        """
