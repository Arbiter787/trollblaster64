from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
import exceptions

if TYPE_CHECKING:
    from entity import Actor


class ActorAction(BaseComponent):
    parent: Actor

    def __init__(
        self,
        max_actions: int = 3,
        current_actions: int = 3,
    ):  
        self.max_actions = max_actions
        self.current_actions = current_actions
    
    @property
    def out_of_actions(self) -> bool:
        return self.current_actions <= 0
    
    @property
    def remaining_actions(self) -> int:
        return self.current_actions
    
    def deduct_actions(self, actions_to_deduct: int = 1) -> None:
        """Deduct actions from an actor. If actions to be deducted exceed remaining actions, raise an exception."""
        if self.current_actions - actions_to_deduct < 0:
            raise exceptions.Impossible("You do not have enough remaining actions to do that.")
        else:
            self.current_actions -= actions_to_deduct
    
    def restore_actions(self) -> None:
        """Set the actor's current actions to its max actions."""
        self.current_actions = self.max_actions
    