from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []
    
    @property
    def items_stacked(self) -> List[List[Item]]:
        """Items in the inventory stacked into lists by item type, if the items are stackable."""
        result_list: List[List[Item]] = []
 
        for item in self.items:
            dupe = False
            for list in result_list:
                if item.name == list[0].name and item.stackable:
                    list.append(item)
                    dupe = True
                    break
            if not dupe:
                result_list.append([item])
        
        return result_list

    def drop(self, item: Item) -> None:
        """Removes an item from the inventory and restores it to the game map, at the player's current location."""
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.gamemap)

        self.engine.message_log.add_message(f"You drop the {item.name}.")