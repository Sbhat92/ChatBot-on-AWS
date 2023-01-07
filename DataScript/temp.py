from decimal import Decimal
import json

def createFileForESearch():
    Restaurants = []
    with open('Clean_Data_new.json', 'r') as json_File:
        restaurantList = json.load(json_File)
    for restaurant in restaurantList:
        #print(restaurant)
        Restaurants.append(
            {'id': restaurant['id'], 'cuisine_tags': restaurant['cuisine_tags']}
        )
    print(Restaurants)
    fd = open('uploadOS.json', 'w')
    for restaurant in Restaurants:
        temp = {"index": { "_index": "restaurants", "_type": "Restaurants", "_id": restaurant['id'] }}
        temp2 = {"cuisine_tags" : restaurant['cuisine_tags']}
        
        json.dump(temp, fd)
        fd.write("\n")
        json.dump(temp2, fd)
        fd.write("\n")
    fd.close()


with open("Clean_Data_new.json") as json_file:
    restaurant_list = json.load(json_file, parse_float=Decimal)
    # print (restaurant_list)

createFileForESearch()