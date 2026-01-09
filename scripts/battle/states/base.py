from abc import ABC, abstractmethod


class BattleState(ABC):
    def __init__(self, scene: "BattleScene"):
        self.scene = scene

        # self.scene.system.debug_dump_units(
        #     self.scene.allies + self.scene.enemies
        # )

    @abstractmethod
    def enter(self) -> None:
        pass

    @abstractmethod
    def exit(self) -> None:
        pass

    @abstractmethod
    def handle(self) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def render(self, surface) -> None:
        pass
