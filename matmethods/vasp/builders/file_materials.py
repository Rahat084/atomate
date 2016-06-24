from tqdm import tqdm

from pymatgen import Composition

__author__ = 'Anubhav Jain <ajain@lbl.gov>'


class FileMaterialsBuilder:
    def __init__(self, materials_write, data_file, delimiter=",", header_lines=0):
        """
        Updates the database using a data file. Format of file must be:
        <material_id or formula>, <property>, <value>
        for which <property> is the materials key to update.

        Comment lines should start with '#'.

        Args:
            materials_write: mongodb collection for materials (write access needed)
            data_file: (str) path to data file
            **kwargs: **kwargs for csv reader
        """
        self._materials = materials_write
        self._data_file = data_file
        self._delimiter = delimiter
        self.header_lines = header_lines


    def run(self):
        print("Starting FileMaterials Builder.")
        with open(self._data_file, 'rb') as f:
            line_no = 0
            lines = [line for line in f]  # only good for small files
            pbar = tqdm(lines)
            for line in pbar:
                line = line.strip()
                if not line.startswith("#"):
                    line_no += 1
                    if line_no > self.header_lines:
                        line = line.split(self._delimiter)

                        try:
                            search_val = int(line[0])
                            search_key = "material_id"
                        except:
                            search_key = "formula_reduced_abc"
                            search_val = Composition(line[0]).reduced_composition.alphabetical_formula

                        key = line[1]
                        val = line[2]
                        try:
                            val = float(val)
                        except:
                            pass

                        x = self._materials.update(
                            {search_key: search_val}, {"$set": {key: val}})

                        if x["n"] == 0:
                            raise ValueError("Could not find entry with {}={}".format(search_key, search_val))

        print("FileMaterials Builder finished processing")