#. .venv/bin/activate
import csv
from flask import Flask
from pathlib import Path

app = Flask(__name__)


class Enclosure:
    def __init__(self, name: str, position=[0,0], size=[0.0], color='999999', image_path: Path = None):
        self.name = name
        self.position = position
        self.size = size
        self.color = color
        self.image_path = image_path
        self.s_object = []

    def _assign_smaller_object(self, s_object: object):
        self.s_object.append(s_object)

### Those subclasses are entirely for easier readability of inventory() code ###
class Room(Enclosure): 
    def assign_container_group(self, container_groups: object):
        super()._assign_smaller_object(container_groups)
class ContainerGroup(Enclosure): 
    def assign_container(self, containers: object):
        super()._assign_smaller_object(containers)
class Container(Enclosure): 
    def assign_item(self, item: object):
        super()._assign_smaller_object(item)
    

class Item:
    def __init__(self, name: str, quantity = 1, subitems = []):
        self.name = name
        self.quantity = quantity
        self.subitems = subitems

def read_container_csv(file: str) -> list[object]:
    with open(file, newline='') as csv_file: #I decided to use csv first, since I don't know the final database structure and I'd rather just code right now instead of contemplating my containers' structure
        container = csv.DictReader(csv_file)
        line_count = 0
        items = []
        for item in container:
            if item.get("quantity") is None: #default in dict.get() doesn't work if None is already set (it only works when index is not set)
                item["quantity"] = 1
            item_object = Item(item.get("name"), item.get("quantity"), item.get("subitems"))
            items.append(item_object)
            if line_count == 0:
                print(f'Column names are {", ".join(item)}')
                line_count += 1
            print(f'\t{item["name"]} is stored in quantity of {item["quantity"]}.')
            line_count += 1
        print(f'Processed {line_count} lines.')
    return items

def get_subpaths(path: Path) -> list[str]:
    subpaths = []
    for subpath in path.iterdir():
        subpaths.append(subpath)
    return subpaths


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/inventory')
def inventory():
    rooms_path = Path('code/containers')
    rooms = get_subpaths(rooms_path)
    for room in rooms: # example: living_room/
        if room.is_dir():
            container_groups_path = room
            container_groups = get_subpaths(container_groups_path)
            for container_group in container_groups: # example: cabinet
                if container_group.is_dir():
                    containers_path = container_group
                    containers = get_subpaths(containers_path)
                    for container in containers: # example: shelf_1.csv
                        if container.is_file():
                            items = read_container_csv(container)
                            for item in items:
                                print(item.name)
                                print(item.quantity)
                                print(item.subitems)
    return 'Placeholder'
