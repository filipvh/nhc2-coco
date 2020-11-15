from nhc2_coco.coco_discover import CoCoDiscover

def discover_callback(address, is_nhc2):
    print("address: ", address)
    print("is nhc2: ", is_nhc2)


disc = CoCoDiscover(discover_callback)
