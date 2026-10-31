"""Original pure-state specification; no FMOD/Wwise API or thread simulation."""
from dataclasses import dataclass


class FakePort:
    def __init__(self):
        self.calls = []  # ordered receipts; duplicates remain observable
        self.fail_next_mode = False

    def emit(self, op, generation, handle, *args):
        self.calls.append((op, generation, handle, *args))
        if op == 'mode' and self.fail_next_mode:
            self.fail_next_mode = False
            return False
        return True


@dataclass(frozen=True)
class Ticket:
    generation: int
    revision: int


class Adapter:
    def __init__(self, port):
        self.port = port
        self.generation = 0
        self.revision = 0
        self.state = 'Stopped'
        self.desired = None
        self.submitted = None
        self.handle = None
        self.owned = {}  # historical ownership receipts; handles never reused
        self.started = set()  # command state, not port call-count assertions
        self.released = set()

    def begin(self, mode):
        if self.state != 'Stopped':
            raise ValueError('exit current session before begin')
        if not isinstance(mode, str) or not mode:
            raise ValueError('mode must be nonempty string')
        self.generation += 1
        self.revision += 1
        self.state = 'Starting'
        self.desired = mode
        self.submitted = None
        self.handle = None
        return self.generation

    def intent(self, mode):
        if self.state not in ('Starting', 'Active'):
            raise ValueError('no live session')
        if not isinstance(mode, str) or not mode:
            raise ValueError('mode must be nonempty string')
        if mode != self.desired:
            self.desired = mode
            self.revision += 1
        self._submit()
        if self.state == 'Starting' and self.submitted == self.desired:
            self._start()
        return Ticket(self.generation, self.revision)

    def ready(self, generation, handle):
        """Trusted loader completion transfers a unique handle, even if cancelled."""
        if (type(generation) is not int or not 1 <= generation <= self.generation
                or not isinstance(handle, str) or not handle):
            raise ValueError('invalid loader receipt')
        if handle in self.owned:
            if self.owned[handle] != generation:
                raise ValueError('handle reused across sessions')
            return  # duplicate completion delivery, not a second allocation
        self.owned[handle] = generation
        if generation != self.generation or self.state != 'Starting' or self.handle is not None:
            self._release(generation, handle)
            return
        self.handle = handle
        self._submit()
        # In this specification desired mode must be submitted before start.
        if self.submitted == self.desired:
            self._start()

    def retry(self, ticket):
        if (ticket.generation, ticket.revision) != (self.generation, self.revision):
            return
        if self.state not in ('Starting', 'Active'):
            return
        self._submit()
        if self.state == 'Starting' and self.submitted == self.desired:
            self._start()

    def invalidate_external_write(self):
        if self.state not in ('Starting', 'Active'):
            return
        self.submitted = None
        self.revision += 1
        self._submit()
        if self.state == 'Starting' and self.submitted == self.desired:
            self._start()

    def _submit(self):
        if self.handle is None or self.submitted == self.desired:
            return
        if self.port.emit('mode', self.generation, self.handle, self.revision, self.desired):
            self.submitted = self.desired

    def _start(self):
        if self.handle is not None and self.handle not in self.started:
            self.port.emit('start', self.generation, self.handle)
            self.started.add(self.handle)
            # Accepted command != Active; wait for modeled outcome.

    def outcome(self, generation, handle, kind):
        if kind not in ('started', 'start_failed', 'stopped'):
            raise ValueError('unknown outcome')
        if (generation != self.generation or handle != self.handle or
                self.state not in ('Starting', 'Active')):
            return
        if handle not in self.started:
            raise ValueError('outcome without accepted start')
        if kind == 'start_failed' and self.state != 'Starting':
            return  # contradictory late outcome cannot cancel an Active session
        if kind == 'started':
            self.state = 'Active'
        else:
            # START_FAILED is terminal here; no STOPPED is required.
            self._release(generation, handle)
            self.handle = None
            self.submitted = None
            self.state = 'Stopped'

    def exit(self):
        if self.state == 'Stopped':
            return
        if self.handle is not None:
            if self.handle in self.started:
                self.port.emit('stop', self.generation, self.handle)
            self._release(self.generation, self.handle)
        self.handle = None
        self.submitted = None
        self.state = 'Stopped'
        # Logical cancellation; loader may still finish and transfer ownership.

    def _release(self, generation, handle):
        if self.owned.get(handle) != generation:
            raise ValueError('ownership mismatch')
        if handle not in self.released:
            self.port.emit('release', generation, handle)
            self.released.add(handle)
