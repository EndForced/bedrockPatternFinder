from anvil import Chunk, Region
from pathlib import Path
from typing import Union

region = Region.from_file("chunks/r.0.0.mca")

print("Поиск существующих чанков через chunk_location():")
found_any = False

class BedrockPatternFinder:
    def init(self, folder_path):
        self.folder_path = folder_path


for i in range(32):
    for j in range(32):
        location = region.chunk_location(chunk_x=i, chunk_z=j)
        if location != (0, 0):
            print(f"✅ Чанк ({i}, {j}) - location: {location}")
            found_any = True
            # Можно загрузить данные
            try:
                chunk_data = region.chunk_data(i, j)
                chunk = Chunk.from_region(region, chunk_x=i, chunk_z=j)
                print(f"   Успешно загружен, размер NBT: {len(str(chunk_data))}")
                print(region.chunk_data(i, j))
            except Exception as e:
                print(f"   Ошибка загрузки: {e}")

if not found_any:
    print("❌ В регионе нет ни одного чанка")
