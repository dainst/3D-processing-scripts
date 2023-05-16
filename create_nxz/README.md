# Compressed Nexus file generator

Transform Wavefront OBJ files (.obj) or Polygon File Format (.ply) into compressed Nexus (.nxz) files. See also http://vcg.isti.cnr.it/nexus.

## Python 3 dependency requirements
* pymeshlab==2022.2.post2

## Usage
To display the script's help run:
```bash
python create_nxz.py -h
```

Example command:
```bash
python create_nxz.py --source path/to/directory/tree/containing/objs/or/plys
```

Alternatively, you can provide a single file:
```bash
python create_nxz.py --source my_file.obj
```

The script will create a `.nxz` file alongside each `.obj` or `.ply` file it finds.

## Filter
To run different filter to change for example the orientation of the model or edit the texture in order to prepare the file for a correct conversion comment or uncomment the appropriate filter or add a new filter.
