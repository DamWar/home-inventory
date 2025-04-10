#. .venv/bin/activate
import csv
from flask import Flask, render_template
from pathlib import Path

app = Flask(__name__)
default_color = '#FFFFFF'


class Enclosure:
    def __init__(self, name: str):
        self.name = name
        self.s_object = []

    def assing_image(self, image_path: Path):
        self.image_path = image_path

    def assign_properties(self, position=[0,0], size=[0,0], color=default_color):
        self.position = position
        self.size = size
        self.color = color

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
        self.subitems = subitems # example: pencil(subitem) inside a small pencils_box(Item) within a big art_box(Container)


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
    rooms_list = []
    
    ## TODO: Refactor into more universal code, which utilizes Enclosure with each directory and Container with *.csv items
    ## TODO: Upon refactoring, add self.type to Enclosure (room, etc.)
    ## Note1: There may be issues with displaying on website, unless very detailed yaml file is provided for each directory, so I'm leaving it for later improvements since I only need current structure
    ## Note2: It might also not be possible due to jinja2 templates' limitation
    rooms_path = Path('code/containers')
    rooms = get_subpaths(rooms_path)
    for room in rooms: # example: living_room/
        if room.is_dir():
            room_obj = Room(room.name)

            container_groups_path = room
            container_groups = get_subpaths(container_groups_path)
            for container_group in container_groups: # example: cabinet
                if container_group.is_dir():
                    container_group_obj = ContainerGroup(container_group.name)

                    containers_path = container_group
                    containers = get_subpaths(containers_path)
                    for container in containers: # example: shelf_1.csv
                        if container.is_file():
                            if container.name == "bg.png": # TODO: (very low priority - efficiency optimization) look for unique files only once, with path generated in above loops, instead of checking every container iteration
                                container_group_obj.assing_image(containers_path.joinpath("bg.png"))
                            if container.suffix == ".csv":
                                container_obj = Container(container.name)
                                if (container.stem + ".png") in containers: # TODO: check for other image types
                                    container_obj.assing_image(container.with_suffix(".png")) # TODO: assign correct suffix after considering other image types
                                container_group_obj.assign_container(container_obj)

                                items = read_container_csv(container)
                                for item in items: # example: "pen, 1"
                                    item_obj = Item(item.name)
                                    container_obj.assign_item(item_obj)
                    room_obj.assign_container_group(container_group_obj)
        rooms_list.append(room_obj)
    return render_template('main.html', rooms=rooms_list) #rooms contain all other objects
