import argparse
import logging
import os
import pymeshlab
import shutil

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.basicConfig(format='%(asctime)s-%(levelname)s-%(name)s - %(message)s')


def process_mesh(file_path: str, keep_intermediate_files: bool):

  output_path =  os.path.dirname(file_path)

  temp_path = f"{output_path}/tmp/"

  if not os.path.exists(temp_path):
      os.makedirs(temp_path)

  file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]

  ms = pymeshlab.MeshSet()
  ms.load_new_mesh(file_path)
  ms.compute_color_from_texture_per_vertex()

  ms.save_current_mesh(f"{temp_path}/{file_name_without_extension}.ply", save_textures=False, save_wedge_texcoord=False)

  nxs_ms = pymeshlab.MeshSet()
  nxs_ms.nxs_build(
    input_file=f"{temp_path}/{file_name_without_extension}.ply",
    output_file=f"{temp_path}/{file_name_without_extension}_uncompressed.nxs"
  )

  nxs_ms.nxs_compress(
    input_file=f"{temp_path}/{file_name_without_extension}_uncompressed.nxs",
    output_file=f"{output_path}/{file_name_without_extension}.nxs"
  )

  if not keep_intermediate_files:
    shutil.rmtree(temp_path)

def evaluate_input_file_list(path: str):
  if os.path.isfile(path):
    return [path]
  elif os.path.isdir(path):
    file_list = []

    for root, dirnames, filenames in os.walk(path):
      for filename in filenames:
        if filename.endswith('.obj'):
            file_list.append(os.path.join(root, filename))

    return file_list
  else:
    raise argparse.ArgumentTypeError(f"{path} is no valid input path.")


parser = argparse.ArgumentParser(description='Transform Wavefront OBJ files (.obj) into compressed Nexus (.nxs) files.')

parser.add_argument('-s', '--source', type=evaluate_input_file_list, required=True, help="Specificy input directory or file path.")
parser.add_argument('-k', '--keep', default=False, action='store_true', help="(Optional) Keep intermediate results in tmp/ directory next to the input files.")

if __name__ == '__main__':
  options = vars(parser.parse_args())

  if (len(options['source']) > 0):
    logger.info(f"Processing {len(options['source'])} files:")
  else:
    logger.info(f"No obj files found.")

  for file in options['source']:
    logger.info(f"  '{file}'")
    process_mesh(file, options['keep'])
