from io import BytesIO
from webbrowser import Error

from anvil import Chunk, Region, Block
from pathlib import Path
from typing import Union, List
import os
import sys

class BedrockPatternFinder:

    def __init__(self, folder_path: Union[str, Path]):
        """
        Finds bedrock patterns
        :param folder_path:
        takes path to folder with .mca files.
        Could be a str or path like object
        """
        self.CHUNK_INDEX_START = -3
        self.CHUNK_INDEX_END = -1

        if not os.path.exists(folder_path):
            raise ValueError(f"Path does not exist '{folder_path}'")

        if not os.path.isdir(folder_path):
            raise ValueError(f"Path is not to directory '{folder_path}'")

        if not os.listdir(folder_path):
            raise FileNotFoundError(f"Given directory is empty '{folder_path}'")

        self.mca_files = self.__load_mca_files(folder_path)
        self.chunks = self.__files_to_chunks(self.mca_files)

    @staticmethod
    def __load_mca_files(path: Union[str, Path]):
        """
        :param path:
        :return: list of .mca files
        """
        path = Path(path)
        mca_files = {}

        for file_name in os.listdir(path):
            if file_name.endswith(".mca"):

                try:
                    file_path = Path(path, file_name)
                    with open(file_path, 'rb') as f:
                        mca_files[file_name] = {}
                        mca_files[file_name]["data"] = f.read()

                except Exception as e:
                    raise ValueError(f"Unknown error while reading .mca files: '{e}' , path: '{file_name}'")

        if not mca_files:
            raise FileNotFoundError(f"directory '{path}' contains no .mca files")

        return mca_files

    def __files_to_chunks(self, files: dict[Union[str,Path]:dict[bytes]]):
        for filename in files.keys():
            try:
                indexes = filename.split(".")[self.CHUNK_INDEX_START:self.CHUNK_INDEX_END]
                indexes = [int(i)*32 for i in indexes]
                # print(filename)

                files[filename]["chunks"] = self.chunk_loader(files[filename]["data"], indexes[0], indexes[1])
                # print(f"loaded {len(files[filename]['chunks'])} from {filename}")
                self.cube_finder(files[filename]["chunks"])

            except Exception as e:
                raise ValueError(f"Unknown error while calculating chunk indexes: for '{filename}', '{e}'")
        return files

    @staticmethod
    def chunk_loader(file: bytes, region_x: int, region_z: int):
        print(f"Processing region: ({region_x}, {region_z})")

        try:
            file_obj = BytesIO(file)
            region = Region.from_file(file_obj)
            chunks = []

            for local_x in range(32):
                for local_z in range(32):
                    try:
                        location = region.chunk_location(chunk_x=local_x, chunk_z=local_z)

                        if location != (0, 0):
                            chunk = Chunk.from_region(region, chunk_x=local_x, chunk_z=local_z)

                            chunks.append({
                                'chunk': chunk,
                                'global_x': region_x * 32 + local_x,
                                'global_z': region_z * 32 + local_z,
                                'local_x': local_x,
                                'local_z': local_z,
                                'region_x': region_x,
                                'region_z': region_z
                            })

                    except Exception as e:
                        print(f"Error loading chunk ({local_x}, {local_z}): {e}")
                        continue

            return chunks

        except Exception as e:
            print(f"Error creating region: {e}")
            return []

    def cube_finder(self, chunks):
        def single_chunk_check(chunk):
            for x in range(1,14):
                for z in range(1,14):
                    cords = self.from_cord_to_cube_3x3((x,z))
                    for cord in cords:
                        # print(str(chunk["chunk"].get_block(*cord).id))
                        if chunk["chunk"].get_block(*cord).id != "bedrock":
                            # print(chunk["chunk"].get_block(*cord))
                            # print("fail")
                            return
                    print("found", chunk["global_x"], chunk["global_z"])

        for chunk in chunks:
            single_chunk_check(chunk)



    def from_cord_to_cube_3x3(self, cord):
        x, z = cord
        cube_cords = []

        for dy in [-1, 0, 1]:  # y: 126, 127, 128
            for dx in [-1, 0, 1]:  # x: x-1, x, x+1
                for dz in [-1, 0, 1]:  # z: z-1, z, z+1
                    cube_cords.append((x + dx, 126 + dy, z + dz))

        return cube_cords



if __name__ == "__main__":
    pass

