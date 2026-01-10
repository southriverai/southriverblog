import zipfile
import json
from typing import List

from dutch_politics.model import PoliticalEntry
def read_data_from_zip(path_file_data: str) -> List[PoliticalEntry]:
    entry_list = []
    with zipfile.ZipFile(path_file_data, 'r') as zip_ref:
        # Get list of JSON files in the zip
        json_files = [f for f in zip_ref.namelist() if f.endswith('.json')]
        # Read each JSON file directly from the zip
        for json_file in json_files:
            with zip_ref.open(json_file) as f:
                data = json.load(f)
                entry_list.append(PoliticalEntry(**data))
    return entry_list

if __name__ == "__main__":
    # load the zip file and read json files directly from it:
    path_file_data = 'data/entry_content.zip'
    entry_list = read_data_from_zip(path_file_data)
    print(len(entry_list))
    list_politician_name = []
    list_politician_name_title = []
    for entry in entry_list[:10]:
        print(json.dumps(entry.model_dump(), indent=4))
        for element in entry.entry_elements:
            list_politician_name.append(element.speaker_name)
            list_politician_name_title.append(element.speaker_name_title)