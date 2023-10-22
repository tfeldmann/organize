class ChangeDetector:
    def __init__(self):
        self._prev = None
        self._ready = False

    def changed(self, value):
        if not self._ready:
            self._prev = value
            self._ready = True
            return True
        else:
            changed = value != self._prev
            self._prev = value
            return changed

    def reset(self):
        self._ready = False
