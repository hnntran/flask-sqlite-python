# flask-sqlite-python

API
1. An endpoint /device/{colocation} exists that returns a list of all devices within that
colocation
2. An endpoint /interface/{type}/{status} exists that returns a list of interfaces with its
corresponding device
3. An endpoint /device/{id}/tags which lists the tags for this device.
4. An endpoint /tags/{tag_id}/device which lists all the devices which have this tag.
5. The API should be implemented using Flask.
