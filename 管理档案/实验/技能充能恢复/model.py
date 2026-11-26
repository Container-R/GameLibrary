"""Fixed duration, nondecreasing integer simulation time. No engine dependencies."""
from dataclasses import dataclass, field


@dataclass
class ChargePool:
    serial: bool
    capacity: int = 2
    duration: int = 10
    due: list[int] = field(default_factory=list)
    now: int | None = None

    def advance(self, t: int):
        assert self.now is None or t >= self.now
        self.now = t
        self.due[:] = [r for r in self.due if r > t]

    def spend(self, t: int, eligible: bool = True):
        self.advance(t)
        if not eligible or len(self.due) == self.capacity:
            return False
        anchor = self.due[-1] if self.serial and self.due else t
        self.due.append(anchor + self.duration)
        return True

    def status(self, t: int):
        self.advance(t)
        if not self.due:
            return self.capacity, None, 0
        return self.capacity - len(self.due), self.due[0] - t, self.due[-1] - t


def check():
    for serial, expected in [
        (True, [(0, 7, 17), (1, 10, 10), (1, 8, 8), (2, None, 0)]),
        (False, [(0, 7, 9), (1, 2, 2), (2, None, 0), (2, None, 0)]),
    ]:
        mode = "serial" if serial else "parallel"
        pool = ChargePool(serial)
        assert pool.spend(0) and pool.spend(2) and not pool.spend(3)
        actual = [pool.status(t) for t in (3, 10, 12, 20)]
        assert actual == expected
        print(mode, "t=3,10,12,20", actual)
        pool = ChargePool(serial)
        assert pool.spend(0) and pool.spend(2) and pool.spend(10)
        assert pool.status(10) == ((0, 10, 20) if serial else (0, 2, 10))
        assert pool.status(30) == (2, None, 0)
        print(mode, "restore-before-spend then jump: ok")
        pool = ChargePool(serial)
        assert pool.spend(0)
        assert not pool.spend(2, eligible=False)
        assert pool.status(2) == (1, 8, 8)
        assert pool.status(60) == (2, None, 0)
        assert pool.spend(60) and pool.status(60) == (1, 10, 10)
        print(mode, "ineligible spend then idle cap without credit: ok")


if __name__ == "__main__":
    check()
