"""Application settings support for Gaphor."""

from gi.repository import Gio
import logging

APPLICATION_ID = "org.gaphor.Gaphor"

logger = logging.getLogger(__name__)


class Settings(Gio.Settings):
    """Gaphor settings."""

    def __init__(self):
        Gio.Settings.__init__(self)

    @classmethod
    def new(cls) -> Gio.Settings | None:
        """Create a new Settings object."""
        schemas = Gio.Settings.list_schemas()
        if APPLICATION_ID in schemas:
            gio_settings = Gio.Settings.new(APPLICATION_ID)
            gio_settings.__class__ = Settings
            return gio_settings
        logger.info(
            "Settings schema not found and settings won't be saved, run `poe install-schemas`"
        )
        return None


settings = Settings.new()
