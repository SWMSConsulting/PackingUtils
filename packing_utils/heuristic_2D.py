from typing import List, Tuple

import greedypacker

from data.container import Container
from data.item import Item
from data.space import Space


class GreedyPackerWrapper():
    def __init__(self):
        self.pack_algo = "maximal_rectangle"
        self.heuristic = "bottom_left"
        self.wastemap = True
        self.rotation = True

    def solve(self,
            container: Container,
            items: List[Item]
    ) -> List[Item]:

        solver = greedypacker.BinManager(
            container.width, container.height, 
            pack_algo=self.pack_algo, 
            heuristic=self.heuristic, 
            wastemap=self.wastemap, 
            rotation=self.rotation,
            sorting=False)

        _items = []
        for item in items:
            _items.append(greedypacker.Item(width=item.width, height=item.height))
        solver.add_items(*_items,)
        solver.execute()
        result = self._convert_to_item_list(solver.bins[0])

        return result

    def _convert_to_item_list(self, bin):
        items = []
        if isinstance(bin, greedypacker.maximal_rectangles.MaximalRectangle):
            for e in bin.items:
                items.append(Item(width=e.width, height=e.height).pack(x=e.x, y=e.y))
        else:
            return NotImplemented

        return items 

class Guillotine_cut_solver():

    _pre_sort_function = None
    _fit_function = None
    _cut_function = None
    _clean_up_space_function = None

    def __init__(self, fit_function="best_area", cut_function="max_rectangle"):

        self._parse_cut_function(cut_function)
        self._parse_fit_function(fit_function)

    def solve(
            self,
            container: Container,
            items: List[Item]
    ) -> List[Item]:

        self.validate_parameter()

        if self._pre_sort_function:
            items = self.pre_sort_function(items)

        self.free_spaces = [Space(0, 0, container.width, container.height)]

        for index, item in enumerate(items):

            filtered_spaces = list(filter(lambda x: (
                x.width >= item.width and x.height >= item.height
            ), self.free_spaces))

            perfect_matches = list(filter(lambda x: (
                x.width == item.width and x.height == item.height), self.free_spaces))

            if len(filtered_spaces) > 0:

                if len(perfect_matches) > 0:
                    space = perfect_matches[0]
                else:
                    space = self._fit_function(item, filtered_spaces)
                items[index] = item.pack(space.x_min, space.y_min)

                self.free_spaces.remove(space)

                placed_space = Space(space.x_min, space.y_min,
                                     space.x_min + item.width, space.y_min + item.height)

                new_cuts = self._cut_function(space, placed_space)
                # print(new_cuts)
                self.free_spaces += new_cuts

                if self._clean_up_space_function:
                    self.free_spaces = self._clean_up_space_function(
                        self.free_spaces, placed_space)

        return items

    def clean_up_spaces(self, spaces: List[Space], placedSpace: Space) -> List[Space]:

        spaces_to_clean = spaces.copy()
        for s1 in spaces:
            if s1.intersects(placedSpace):
                new_cuts = self._cut_function(s1, placedSpace)
                spaces_to_clean += new_cuts

        spaces_to_clean = list(set(spaces_to_clean))
        spaces_to_remove = []
        for s1 in spaces_to_clean:
            for s2 in spaces_to_clean:
                if s1 != s2 and s1.is_subset_of(s2):
                    spaces_to_remove.append(s1)

        for s in set(spaces_to_remove):
            spaces_to_clean.remove(s)

        return spaces_to_clean

    def _cut_spaces(self, inputSpace: Space, cutSpace: Space) -> List[Space]:

        s1 = Space(
            cutSpace.x_max, cutSpace.y_min,
            inputSpace.x_max, cutSpace.y_max
        )
        s2 = Space(
            cutSpace.x_min, cutSpace.y_max,
            cutSpace.x_max, inputSpace.y_max
        )
        s3 = Space(
            cutSpace.x_max, cutSpace.y_max,
            inputSpace.x_max, inputSpace.y_max
        )
        return s1, s2, s3

    def _cut_spaces_horizontal(self, inputSpace: Space, cutSpace: Space) -> List[Space]:
        # horizontal cut (s2 + s3, s1)
        s1, s2, s3 = self._cut_spaces(inputSpace, cutSpace)
        return [Space(s2.x_min, s2.y_min, s3.x_max, s3.y_max), s1]

    def _cut_spaces_vertical(self, inputSpace: Space, cutSpace: Space) -> List[Space]:
        # vertical cut (s1 + s3, s2)
        s1, s2, s3 = self._cut_spaces(inputSpace, cutSpace)
        return [Space(s1.x_min, s1.y_min, s3.x_max, s3.y_max), s2]

    def cut_shorter_axis(self, inputSpace: Space, cutSpace: Space) -> List[Space]:
        """cut along the shorter axis

        Args:
            inputSpace (Space): space to cut from
            cutSpace (Space): space to cut

        Returns:
            List[Space]: remaining spaces
        """
        if inputSpace.width < inputSpace.height:
            return self._cut_spaces(inputSpace, cutSpace, horizontal=True)
        else:
            return self._cut_spaces(inputSpace, cutSpace, horizontal=False)

    def cut_longer_axis(self, inputSpace: Space, cutSpace: Space) -> List[Space]:
        """cut along the longer axis

        Args:
            inputSpace (Space): space to cut from
            cutSpace (Space): space to cut

        Returns:
            List[Space]: remaining spaces
        """
        if inputSpace.width >= inputSpace.height:
            return self._cut_spaces(inputSpace, cutSpace, horizontal=True)
        else:
            return self._cut_spaces(inputSpace, cutSpace, horizontal=False)

    def cut_shorter_leftover_axis(self, inputSpace: Space, cutSpace: Space) -> List[Space]:
        """cut along the shorter leftover axis 

        Args:
            inputSpace (Space): space to cut from
            cutSpace (Space): space to cut

        Returns:
            List[Space]: remaining spaces
        """
        if inputSpace.width - cutSpace.width < inputSpace.height - cutSpace.height:
            return self._cut_spaces(inputSpace, cutSpace, horizontal=True)
        else:
            return self._cut_spaces(inputSpace, cutSpace, horizontal=False)

    def cut_longer_leftover_axis(self, inputSpace: Space, cutSpace: Space) -> List[Space]:
        """cut along the longer leftover axis 

        Args:
            inputSpace (Space): space to cut from
            cutSpace (Space): space to cut

        Returns:
            List[Space]: remaining spaces
        """
        if inputSpace.width - cutSpace.width >= inputSpace.height - cutSpace.height:
            return self._cut_spaces(inputSpace, cutSpace, horizontal=True)
        else:
            return self._cut_spaces(inputSpace, cutSpace, horizontal=False)

    def cut_min_area(self, inputSpace: Space, cutSpace: Space) -> List[Space]:
        """cut to append the remaining space to the smaller area

        Args:
            inputSpace (Space): space to cut from
            cutSpace (Space): space to cut

        Returns:
            List[Space]: remaining spaces
        """
        right, top, _ = self._cut_spaces(inputSpace, cutSpace)
        if top.area < right.area:
            return self._cut_spaces_horizontal(inputSpace, cutSpace)
        else:
            return self._cut_spaces_vertical(inputSpace, cutSpace)

    def cut_max_area(self, inputSpace: Space, cutSpace: Space) -> List[Space]:
        """cut to append the remaining space to the larger area

        Args:
            inputSpace (Space): space to cut from
            cutSpace (Space): space to cut

        Returns:
            List[Space]: remaining spaces
        """
        right, top, _ = self._cut_spaces(inputSpace, cutSpace)
        if top.area >= right.area:
            return self._cut_spaces_horizontal(inputSpace, cutSpace)
        else:
            return self._cut_spaces_vertical(inputSpace, cutSpace)

    def cut_max_rectangle(self, inputSpace: Space, cutSpace: Space):
        """cut to append the remaining space to the larger area

        Args:
            inputSpace (Space): space to cut from
            cutSpace (Space): space to cut

        Returns:
            List[Space]: remaining spaces
        """
        s1, s2, s3 = self._cut_spaces(inputSpace, cutSpace)
        return [
            Space(s2.x_min, s2.y_min, s3.x_max, s3.y_max),
            Space(s1.x_min, s1.y_min, s3.x_max, s3.y_max)
        ]

    def fit_best_area(self, item: Item, filtered_spaces: List[Space]) -> Space:
        """minimize the area of remaining spaces

        Args:
            item (Item): item to fit
            filtered_spaces (List[Space]): possible positions where item can fit in

        Returns:
            Space: selected position
        """
        selected_space = min(filtered_spaces, key=lambda x: x.area)
        return selected_space

    def fit_worst_area(self, item: Item, filtered_spaces: List[Space]) -> Space:
        """maximize the area of remaining spaces

        Args:
            item (Item): item to fit
            filtered_spaces (List[Space]): possible positions where item can fit in

        Returns:
            Space: selected position
        """
        selected_space = max(filtered_spaces, key=lambda x: x.area)
        return selected_space

    def fit_best_short_side(self, item: Item, filtered_spaces: List[Space]) -> Space:
        """minimize the length of the remaining shorter side

        Args:
            item (Item): item to fit
            filtered_spaces (List[Space]): possible positions where item can fit in

        Returns:
            Space: selected position
        """
        selected_space = min(filtered_spaces, key=lambda x: min(
            x.width - item.width, x.height - item.height))
        return selected_space

    def fit_worst_short_side(self, item: Item, filtered_spaces: List[Space]) -> Space:
        """maximize the length of the remaining shorter side

        Args:
            item (Item): item to fit
            filtered_spaces (List[Space]): possible positions where item can fit in

        Returns:
            Space: selected position
        """
        selected_space = max(filtered_spaces, key=lambda x: min(
            x.width - item.width, x.height - item.height))
        return selected_space

    def fit_best_long_side(self, item: Item, filtered_spaces: List[Space]) -> Space:
        """minimize the length of the remaining longer side

        Args:
            item (Item): item to fit
            filtered_spaces (List[Space]): possible positions where item can fit in

        Returns:
            Space: selected position
        """
        selected_space = min(filtered_spaces, key=lambda x: max(
            x.width - item.width, x.height - item.height))
        return selected_space

    def fit_worst_long_side(self, item: Item, filtered_spaces: List[Space]) -> Space:
        """maximize the length of the remaining longer side

        Args:
            item (Item): item to fit
            filtered_spaces (List[Space]): possible positions where item can fit in

        Returns:
            Space: selected position
        """
        selected_space = max(filtered_spaces, key=lambda x: max(
            x.width - item.width, x.height - item.height))
        return selected_space

    def _parse_cut_function(self, cut_function):
        if cut_function == "min_area":
            self._cut_function = self.cut_min_area
        elif cut_function == "max_area":
            self._cut_function = self.cut_max_area
        elif cut_function == "shorter_leftover_axis":
            self._cut_function = self.cut_shorter_leftover_axis
        elif cut_function == "longer_leftover_axis":
            self._cut_function = self.cut_longer_leftover_axis
        elif cut_function == "shorter_axis":
            self._cut_function = self.cut_shorter_axis
        elif cut_function == "longer_axis":
            self._cut_function = self.cut_longer_axis

        elif cut_function == "max_rectangle":
            self._cut_function = self.cut_max_rectangle
            self._clean_up_space_function = self.clean_up_spaces
        else:
            raise ValueError(f"cut function is not supported: {cut_function}")

    def _parse_fit_function(self, fit_function):
        if fit_function == "best_area":
            self._fit_function = self.fit_best_area
        elif fit_function == "best_short_side":
            self._fit_function = self.fit_best_short_side
        elif fit_function == "best_long_side":
            self._fit_function = self.fit_best_long_side
        elif fit_function == "worst_area":
            self._fit_function = self.fit_worst_area
        elif fit_function == "worst_short_side":
            self._fit_function = self.fit_worst_short_side
        elif fit_function == "worst_long_side":
            self._fit_function = self.fit_worst_long_side
        else:
            raise ValueError(f"fit function is not supported: {fit_function}")

    def validate_parameter(self):
        if self._fit_function is None:
            raise Exception("fit_function is None")

        if self._cut_function is None:
            raise Exception("cut_function is None")


if __name__ == "__main__":
    solver = GreedyPackerWrapper() #Guillotine_cut_solver()
    c = Container(5,5)
    items = [Item(1, 2) for _ in range(8)]
    print(solver.solve(c, items))
