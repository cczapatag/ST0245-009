
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: JulianMazo, CristianZapata & HaroldGonzález
This code uses certain data to create a CART or ID3 decision tree.
With this tree, it will be able to make prediction of future data.
Uses Graphviz to graph the tree.
"""

# IMPORT LIBRARIES

import math  # To use some math functions.
from graphviz import Digraph  # To graph the tree.
import os  # To facilitate interaction with users.


# AUXILIARY METHODS

#O(n)
def class_counts(data):
    """ Creates a dictionary which stores the number of times that each prediction value appears given a certain data.
    
    :param data: a matrix that stores certain data such that its final column has the prediction values.
    :return: classes that is a dictionary which stores the number of times that each prediction value appears.
    """
    classes = {}  # Creates the dictionary.
    
    for row in data:
        label = row[-1]
        if label not in classes:
            classes[label] = 0  # Creates the key for a prediction value.
        classes[label] += 1  # Counts a case for the prediction value.
        
    return classes

#O(1)
def is_number(value):
    """ Checks if a given value is numeric.
    
    :param value: a value of any type.
    :return: a boolean.
    """
    return isinstance(value, int) or isinstance(value, float)

#O(n)
def critical_values(data, column):
    """ Creates a dictionary which stores the values with the greater and lower number of success cases from a column of a given data to get the best information gain.
    
    :param data: a matrix which stores certain data such that its final column has the prediction values.
    :param column: a list which stores values from a column of the given data.
    :return: a tuple with bestValue and worstValue which are the values with greater and lower number of success cases, respectively.
    """
    values = {} # Creates the values dictionary.
    
    for row in data:
        dato = row[column]  
        if dato not in values:
            values [dato] = 0  # Creates a key if the value is not in the dictionary.
        values [dato] += int(row[-1])  # Counts a case that the value has success.
        
    bestValue = None
    worstValue = None
    bestSuccess = 0 
    worstSucces = len(data)
    
    for val in values: # Searches the values with greater and lower number of success cases.
        if (values[val] >= bestSuccess): 
            bestSuccess = values[val]
            bestValue = val
        if (values[val] <= worstSucces):
            worstSucces = values[val]
            worstValue = val

    return bestValue, worstValue

#O(n)
def partition(data, question):
    """ Divides a given data in two matrices matching each row of the data with a given question.
    
    :param data: a matrix which stores certain data.
    :param question: an object of type Question that determines if a given value satisfy certain condition.
    :return: true_rows and false_rows that are the matrices with the rows that satisfy the condition of the question and the rows that do not, respectively.
    """
    true_rows, false_rows = [], []  # Creates the matrices.
    
    for row in data:
        if question.match(row):  # Evaluates each row with the question.
            true_rows.append(row)
        else:
            false_rows.append(row)
            
    return true_rows, false_rows

#O(n)
def gini(data):
    """ Calculates the gini index of a given data.
    
    :param data: a matrix which stores certain data.
    :return: impurity which is the gini index.
    """
    counts = class_counts(data)  # Counts the prediction values to determine the formula.
    impurity = 1 
    
    for label in counts:
        prob_of_lbl = counts[label] / float(len(data))
        impurity -= prob_of_lbl**2
        
    return impurity

#O(n)
def entropy(data):
    """ Calculates the entropy of a given data.
    
    :param data: a matrix which stores certain data.
    :return: impurity which is the entropy.
    """
    counts = class_counts(data)  # Counts the prediction values to determine the formula.
    impurity = 0
    
    for label in counts:
        prob_of_lbl = counts[label] / float(len(data))
        impurity -= prob_of_lbl * math.log2(prob_of_lbl)
        
    return impurity

#O(n)
def info_gain(left, right, current_uncertainty):
    """ Calculates the information with the partition of certain data and a given gini impurity.
    
    :param left: a matrix with certain data.
    :param right: a matrix with certain data.
    :param current_uncertainty: the gini impurity of the data.
    :return: a float which is the information gain of the data.
    """
    p = float(len(left)) / (len(left) + len(right))
    
    return current_uncertainty - p * gini(left) - (1 - p) * gini(right)

#O(n)
def info_gain_e(left, right, current_uncertainty):
    """ Calculates the information with the partition of certain data and a given entropy.
    
    :param left: a matrix with certain data.
    :param right: a matrix with certain data.
    :param current_uncertainty: the gini impurity of the data.
    :return: a float which is the information gain of the data.
    """
    p = float(len(left)) / (len(left) + len(right))
    
    return current_uncertainty - p * entropy(left) - (1 - p) * entropy(right)

#O(m*n)
def find_best_split_CART(data, header):
    """ Determines which column and value give the best information gain using the gini impurity and build an object of type Question with that value.
    
    :param data: a matrix that stores certain data such that its final column has the prediction values.
    :param header: a list with the labels of the data to build the questions.
    :return: a tuple with best_gain and best_question which are the value of the best information gain and the question with the value that gave that gain.
    """
    best_gain = 0
    best_question = None
    current_uncertainty = gini(data)
    n_features = len(header) - 1  # Counts the number of columns of the data.

    for column in range(n_features):

        values = critical_values(data, column)  # Searches the values that give the best information gain from each column.

        for val in values:

            question = Question(column, val, header)
            true_rows, false_rows = partition(data, question)

            if len(true_rows) == 0 or len(false_rows) == 0:  # If there is no impurity, there is no gain.
                continue

            gain = info_gain(true_rows, false_rows, current_uncertainty)

            if gain >= best_gain:
                best_gain, best_question = gain, question

    return best_gain, best_question

#O(m*n)
def find_best_split_ID3(data, header):
    """ Determines which column and value give the best information gain using the entropy and build an object of type Question with that value.
    
    :param data: a matrix that stores certain data such that its final column has the prediction values.
    :param header: a list with the labels of the data to build the questions.
    :return: a tuple with best_gain and best_question which are the value of the best information gain and the question with the value that gave that gain.
    """
    best_gain = 0
    best_question = None
    current_uncertainty = entropy(data)
    n_features = len(header) - 1  # Counts the number of columns of the data.

    for column in range(n_features):
    
        values = critical_values(data, column)  # Searches the values that give the best information gain from each column.

        for val in values:
            
            question = Question(column, val, header)
            true_rows, false_rows = partition(data, question)

            if len(true_rows) == 0 or len(false_rows) == 0:  # If there is no impurity, there is no gain.
                continue

            gain = info_gain_e(true_rows, false_rows, current_uncertainty)

            if gain >= best_gain:
                best_gain, best_question = gain, question

    return best_gain, best_question

#O(n*m*2^n)
def build_CART_tree(data, header, limit = -1):
    """ Recursively creates an object of type DecisionNode as a Node of a CART Tree.
    
    :param data: a matrix that stores certain data such that its final column has the prediction values.
    :param header: a list with the labels of the data to build the questions.
    :param limit: maximum level of the tree.
    :return: an object of type DecisionNode.
    """
    if limit == 0:  # If the tree arrives to the max level of recursion, creates a Leaf.
        return Leaf(data)

    gain, question = find_best_split_CART(data, header)  # Searches the best information gain and question to divide the tree.

    if gain == 0:  # If there is no information gain, creates a Leaf.
        return Leaf(data)

    true_rows, false_rows = partition(data, question)  # Splits the data according to the best question.

    true_child = build_CART_tree(true_rows, header, limit - 1)  # Creates the true child of the Node with the data that satisfy the question.
    false_child = build_CART_tree(false_rows, header, limit - 1)  # Creates the false child of the Node with the data that doesn't satisfy the question.

    return DecisionNode(question, true_child, false_child)

#O(2^n)
def build_ID3_tree(data, header, limit = -1):
    """ Recursively creates an object of type DecisionNode as a Node of a ID3 Tree.
    
    :param data: a matrix that stores certain data such that its final column has the prediction values.
    :param header: a list with the labels of the data to build the questions.
    :param limit: maximum level of the tree.
    :return: an object of type DecisionNode.
    """
    
    if limit == 0:  # If the tree arrives to the max level of recursion, creates a Leaf.
        return Leaf(data)

    gain, question = find_best_split_ID3(data, header)  # Searches the best information gain and question to divide the tree.

    if gain == 0:  # If there is no information gain, creates a Leaf.
        return Leaf(data)

    true_rows, false_rows = partition(data, question)  # Splits the data according to the best question.

    true_child = build_ID3_tree(true_rows, header, limit - 1)  # Creates the true child of the Node with the data that satisfy the question.
    false_child = build_ID3_tree(false_rows, header, limit - 1)  # Creates the false child of the Node with the data that doesn't satisfy the question.

    return DecisionNode(question, true_child, false_child)

#O(2^n)
def import_tree():
    """ Reads a .txt file and creates an object of type DefaultTree if it is a print of a previously made CART or ID3 Tree.
    
    :return: tree that is the CART or ID3 tree previously made.
    """
    r = str(input("Ingrese el nombre del archivo a leer: "))  # Interaction with the user.
    print()
    os.system("pause")
    os.system("cls")
    print("Leyendo...\n")
    
    f = open(r, "r")  # Open the file
    
    header = f.readline()  # Read the labels of the data.
    header = header[2:len(header)-2].split("', '")
    header[-1] = header[-1][0:len(header[-1])-2]
    
    tree = DefaultTree(read_node(f, header), header)  # Creates the tree with the read_node method.
    
    return tree

#O(2^n)
def read_node(f, header):
    """ With a opened file, determines with each line of the file if it refers to a Node or a Leaf and creates it.
    
    :param f: an opened .txt file with a saved tree.
    :param header: the labels of the data to build the questions of the nodes.
    :return: an object or type DecisionNode or Leaf.
    """
    s = f.readline()
    
    if s == "" or s == None: # If there is no another line, doesn't return anything.
        return None
    
    s = s.split()
    
    question = ""  # Checks if the string is a question of a Node and creates it.
    
    if s[0] == "Is":
        
        t = s[3][0:len(s[3])-1]
        
        try:  # Checks if the question uses a numeric value.
            t = int(t)
            question = Question(header.index(s[1]), t, header)
        except(ValueError):
            try:
                t = float(t)
                question = Question(header.index(s[1]), t, header)
            except(ValueError):
                question = Question(header.index(s[1]), t, header)
                
        f.readline()
        
        true_child = read_node(f, header)  # Creates the true child with the next lines of the file.
        f.readline()
        false_child = read_node(f, header)  # Creates the false child with the next lines of the file.
        
        return DecisionNode(question, true_child, false_child)
    
    elif len(s) == 5:  # Creates the leaves.
        data = [[int(s[1][1])]]*int(s[2][0:len(s[2])-1]) + [[int(s[3][0])]]*int(s[4][0:len(s[4])-1])
        
        return Leaf(data)
    
    else:
        data = [[int(s[1][1])]]*int(s[2][0:len(s[2])-1])
        
        return Leaf(data)

class Question:
    """ An object type that implements the question to decide if certain data satisfy or not a condition.
    """
    
    #O(1)
    def __init__(self, column, value, header):
        """ Constructs a new Question object.
        
        :param column: a column of certain data.
        :param value: a value of any type.
        :param header: the labels of the data to classify.
        """
        self.column = column
        self.value = value
        self.header = header
    
    #O(1)
    def match(self, data):
        """ Determines if a given data satisfies the condition of the question.
        
        :param data: the data to classify.
        :return: a boolean.
        """
        val = data[self.column]
        
        if is_number(val) and is_number(self.value):
            return val >= self.value
        else:
            return str(val) == str(self.value)
    
    #O(1)
    def __str__(self):
        """ Prints the question with the label an value to check.
        
        :return: a string.
        """
        condition = "=="
        if is_number(self.value):  # If the question uses a numeric value.
            condition = ">="
        return "Is %s %s %s?" % (self.header[self.column], condition, str(self.value))

class Leaf:
    """ An object type that stores the possibilities that certain data get each predicition value.
    """
    
    #O(n)
    def __init__(self, data):
        """ Counts the cases of success and failure of a given data and storages it in a dictionary.
        
        :param data: a matrix that stores certain data such that its final column has the prediction values.
        """
        self.predictions = class_counts(data)
    
    #O(1)
    def imprimir(self, spacing = ""):
        """ Prints the cases of each prediction value appearance in the data.
        
        :return: a string.
        """
        return spacing + "Prediction: " + str(self.predictions)
    
    #O(1)
    def graph(self, digraph, name):
        try:
            p = round((self.predictions.get(1)/(sum(self.predictions.values()) * 1.0)) * 100, 2)
        except(TypeError, ValueError):
            p = 0
        label = "Probability of success: " + str(p) + "%"
        color = "red"
        if p > 50.0:
            color = "orange"
        if p > 60.0:
            color = "gold"
        if p > 75.0:
            color = "cyan"
        if p > 90.0:
            color = "lime"
        digraph.node(name, label, style = "filled", color = color)
        return digraph

class DecisionNode:
    
    #O(1)
    def __init__(self, question, true_child, false_child):
        self.question = question
        self.true_child = true_child
        self.false_child = false_child
    
    #O(2^n)
    def imprimir(self, spacing = ""):
        s = spacing + str(self.question) + "\n" + spacing + "--> True:" + "\n" + self.true_child.imprimir(spacing + "  ")  + "\n" + spacing + "--> False:" + "\n" + self.false_child.imprimir(spacing + "  ")
        return s
    
    #O(2^n)
    def graph(self, digraph, name):
        digraph.node(name, str(self.question)[3:len(str(self.question))-1], style = "filled")
        digraph = self.true_child.graph(digraph, name + 't')
        digraph.edge(name, name + 't', 'True')
        digraph = self.false_child.graph(digraph, name + 'f')
        digraph.edge(name, name + 'f', 'False')
        return digraph

class CARTTree:

    #O(2^n)
    def __init__(self, data, header, limit = -1):
        self.root = build_CART_tree(data, header, limit)
        self.header = header
    
    #O(2^n)
    def __str__(self):
        return str(self.header) + "\n" + self.root.imprimir()
    
    #O(2^n)
    def graphic(self):
        digraph = Digraph(format = "png")
        return self.root.graph(digraph, 'r')


class ID3Tree:
    
    #O(2^n)
    def __init__(self, data, header, limit = -1):
        self.root = build_ID3_tree(data, header, limit)
        self.header = header
    
    #O(2^n)
    def __str__(self):
        return str(self.header) + "\n" + self.root.imprimir()
    
    #O(2^n)
    def graphic(self):
        digraph = Digraph(format = "png")
        return self.root.graph(digraph, 'r')

class DefaultTree:
    
    #O(1)
    def __init__(self, root, header):
        self.root = root
        self.header = header
    
    #O(2^n)
    def __str__(self):
        return str(self.header) + "\n" + self.root.imprimir()
    
    #O(2^n)
    def graphic(self):
        digraph = Digraph(format = "png")
        return self.root.graph(digraph, 'r')

def classify(row, node):
    if isinstance(node, Leaf):
        return node.predictions

    if node.question.match(row):
        return classify(row, node.true_child)
    else:
        return classify(row, node.false_child)

def print_prediction(predictions):
    total = sum(predictions.values()) * 1.0
    probs = {}
    for lbl in predictions.keys():
        probs[lbl] = str(int(predictions[lbl] / total * 100)) + "%"
    return probs
