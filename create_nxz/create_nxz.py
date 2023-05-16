import argparse
import logging
import os
import pymeshlab
import shutil

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(format='%(asctime)s-%(levelname)s-%(name)s - %(message)s')

p = pymeshlab.Percentage(0.1)

def process_obj_file(file_path: str, keep_intermediate_files: bool=False):

  output_path =  os.path.dirname(file_path)

  temp_path = f"{output_path}/tmp/"

  if not os.path.exists(temp_path):
      os.makedirs(temp_path)

  file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]

  try:
    ms = pymeshlab.MeshSet()
    # Laden des Modelles
    ms.load_new_mesh(file_path)
    # Filter:
    # Texture Map Defragmentation
    ms.apply_texmap_defragmentation()
    # Erhoehen der Punktdichte
    ms.meshing_surface_subdivision_midpoint(threshold=p)
    # Uebertrag der Farben der Textur auf die Punkte
    ms.compute_color_from_texture_per_vertex()
    # Speichern des Modells als PLY
    ms.save_current_mesh(f"{temp_path}/{file_name_without_extension}.ply", save_textures=False, save_wedge_texcoord=False)

    # Nexus Konvertierung
    nxs_ms = pymeshlab.MeshSet()
    nxs_ms.nxs_build(
      input_file=f"{temp_path}/{file_name_without_extension}.ply",
      output_file=f"{temp_path}/{file_name_without_extension}.nxs"
    )

    nxs_ms.nxs_compress(
      input_file=f"{temp_path}/{file_name_without_extension}.nxs",
      output_file=f"{output_path}/{file_name_without_extension}.nxz"
    )

  except Exception as e:
    logger.error(e)

  finally:
    if not keep_intermediate_files:
      shutil.rmtree(temp_path)

def evaluate_input_file_list(path: str):

  if os.path.isfile(path):
    return [path]
  elif os.path.isdir(path):
    file_list = []
    for root, dirnames, filenames in os.walk(path):
      for filename in filenames:
        if filename.endswith('.obj') or filename.endswith('.ply'):
            file_list.append(os.path.join(root, filename))

    return file_list
  else:
    raise argparse.ArgumentTypeError(f"{path} is no valid input path.")


parser = argparse.ArgumentParser(description='Transform Wavefront OBJ files (.obj) or Polygon File Format (.ply) into compressed Nexus (.nxz) files. See also http://vcg.isti.cnr.it/nexus.')

parser.add_argument('-s', '--source', type=evaluate_input_file_list, required=True, help="Specificy either an input directory or the path to a single file.")
parser.add_argument('-k', '--keep', default=False, action='store_true', help="(Optional) Keep intermediate results in tmp/ directory next to the input files.")

if __name__ == '__main__':
  options = vars(parser.parse_args())

  if (len(options['source']) > 0):
    logger.info(f"Processing {len(options['source'])} files:")
  else:
    logger.info(f"No obj files found.")

  for file_path in options['source']:
    logger.info(f"'{file_path}'")
    process_obj_file(file_path, options['keep'])
