from igraph import *
import igraph
import xml.etree.ElementTree as ET
from skimage import io
from skimage import transform
import cv2
import numpy as np
import argparse



def parserargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-image', action='store',
                        dest='image')

    parser.add_argument('-target', action='store',
                        dest='target')

    parser.add_argument('-source', action='store',
                        dest='source')

    parser.add_argument('-plot', action='store',
                        dest='plot',
                        default=False)

    results = parser.parse_args()

    return results.image, results.source, results.target, results.plot 


def imshow(name, image):
    cv2.imshow(name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def do_dictionary_label_list(image):
    dictionary = {}
    label_list = []
    count = 0
    for i, row in enumerate(image):
        for j, pixel in enumerate(row):
            label_list.append(str(count))
            dictionary["({}, {})".format(i, j)] = count
            count += 1
    return dictionary, label_list


def remove_duplicate(vextex_list):
    temp = []
    for a,b in vextex_list :
        if (a,b) not in temp and (b,a) not in temp: #to check for the duplicate tuples
            temp.append((a,b))
    vextex_list = temp * 1 #copy temp to d
    return vextex_list


if __name__ == '__main__':
    image_path, source, target, plot = parserargs()
    print("LOG:\nImage: {}\nSource: {}\nTarget: {}\nPlot: {}".format(image_path, source, target, plot))
    image = cv2.imread(image_path, 0)
    # image = np.array([
    #   [20, 220, 46],
    #    [55, 98, 33],
    #    [22, 11, 99],
    #    ]
    #    )


    X = image.shape[0]-1
    Y = image.shape[1]-1

    neighbors = lambda x, y : [(x2, y2) for x2 in range(x-1, x+2)
                                   for y2 in range(y-1, y+2)
                                   if (-1 < x <= X and
                                       -1 < y <= Y and
                                       (x != x2 or y != y2) and
                                       (0 <= x2 <= X) and
                                       (0 <= y2 <= Y))]


    vextex_list = []
    weight_list = []

    dictionary = {}
    label_list = []
    weight_list = {}
    dictionary, label_list = do_dictionary_label_list(image)

    for i, row in enumerate(image):
        for j, pixel in enumerate(row):
            for n in neighbors(i, j):
                vextex_list.append( (dictionary["({}, {})".format(i, j)], dictionary["({}, {})".format(n[0], n[1])]) )
                weight_list[(dictionary["({}, {})".format(i, j)], dictionary["({}, {})".format(n[0], n[1])])] = abs(float(image[(i,j)]) - float(image[n]))   


    vextex_list = remove_duplicate(vextex_list)




    g = Graph()
    g.add_vertices(image.shape[0]*image.shape[1])
    g.add_edges(vextex_list)
    g.vs["name"] = label_list
    g.vs["label"] = label_list
    g.es["weight"] = 0

    ks = list(weight_list)

    while ks:
        pair = ks.pop(0)
        aux = str(pair).replace("(","").replace(")", "").replace(",","").split(" ")
        first = aux[0]
        second = aux[1]
        g[first, second] = weight_list[pair]

    path = g.shortest_paths_dijkstra(source=source, target=target, weights=g.es["weight"], mode=OUT)
    print("****\nShortest_path: ", path[0][0])
    
    if plot:
        layout = g.layout("kk")
        igraph.plot(g, layout = layout)