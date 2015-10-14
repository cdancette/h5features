"""Provides the Items class to the h5features module.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import h5py


def unique_items(items):
    """Return False if items is empty or have non-unique elements."""
    if not items:
        return False
    return len(set(items)) == len(items)


class Items(object):
    """This class manages items in h5features files."""

    def __init__(self, data, name='items'):
        """Initializes Items from data.

        data : list of str -- A list of items (e.g. files from
        which the features where extracted).

        """

        if not unique_items(data):
            raise IOError('all items must have different names.')

        self.data = data
        self.name = name

    def create(self, group, nb_lines_by_chunk):
        """Creates an items subgroup in the given group.

        group : HDF5 Group -- The group where to create the 'files'
        subgroup.

        nb_lines_by_chunk : int -- Number of lines (ie filenames)
        stored in a single data chunk.

        """
        str_dtype = h5py.special_dtype(vlen=str)
        group.create_dataset(self.name, (0,), dtype=str_dtype,
                             chunks=(nb_lines_by_chunk,), maxshape=(None,))

    def continue_last_item(self, group):
        """Return True if we can continue writing to last item in the group.

        This method compares the shared items between the given group
        and self. Given these shared items, three cases can occur:

        - No shared items: return False

        - There is only one shared item. It is first in self and last
        in group : return True. In that case the first item in self is
        erased.

        - Otherwise raise IOError.

        """
        # Get items already present in the group
        group_items = group[self.name][...]

        # Shared items between self and the group
        nb_shared = len(set(group_items).intersection(self.data))
        if nb_shared == 1:
            # Assert the last item in group is the first item in self.
            if not self.data[0] == group_items[-1]:
                raise IOError('data can be added only at the end'
                              'of the last written file.')
            self.data = self.data[1:]
            return True
        elif nb_shared > 1:
            raise IOError('groups cannot have more than one shared items.')
        else:
            # No shared items
            return False

    def write(self, group):
        """Write stored items to the given group.

        We assume the items subgroup exists in the given group.

        """
        if self.data:
            nitems = group[self.name].shape[0]
            group[self.name].resize((nitems + len(self.data),))
            group[self.name][nitems:] = self.data
