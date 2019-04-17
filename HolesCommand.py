import adsk.core
import adsk.fusion
import traceback

import os
from os.path import expanduser
import csv

from .Fusion360Utilities.Fusion360Utilities import AppObjects
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase


# Function to convert a csv file to a list of dictionaries.
# Takes in one variable called "csv_file_name"
def csv_dict_list(csv_file_name):

    # Open variable-based csv,
    # Iterate over the rows and map values to a list of dictionaries
    reader = csv.DictReader(open(csv_file_name, 'r'))
    dict_list = []
    for line in reader:
        dict_list.append(line)
    return dict_list

def make_holes(hole_list):

    ao = AppObjects()

    profile_collection = adsk.core.ObjectCollection.create()

    # Get reference to the sketches and plane
    sketches = ao.root_comp.sketches
    xy_plane = ao.root_comp.xYConstructionPlane

    # Create a new sketch and get lines reference
    sketch = sketches.add(xy_plane)
    circles = sketch.sketchCurves.sketchCircles

    input_units = 'in'

    for hole in hole_list:
        x = ao.units_manager.evaluateExpression(hole['x'], input_units)
        y = ao.units_manager.evaluateExpression(hole['y'], input_units)
        radius = ao.units_manager.evaluateExpression(hole['radius'], input_units)
        # x = float(hole['x'])
        # y = float(hole['y'])
        # radius = float(hole['radius'])

        center_point = adsk.core.Point3D.create(x, y, 0)
        circles.addByCenterRadius(center_point, radius)

    for profile in sketch.profiles:
        profile_collection.add(profile)

    # Create an extrusion input
    extrudes = ao.root_comp.features.extrudeFeatures
    ext_input = extrudes.createInput(profile_collection, adsk.fusion.FeatureOperations.CutFeatureOperation)

    # Set the distance extent to be single direction
    extent_all = adsk.fusion.ThroughAllExtentDefinition.create()
    ext_input.setOneSideExtent(extent_all, adsk.fusion.ExtentDirections.PositiveExtentDirection)

    # Create the extrusion
    extrudes.add(ext_input)


def make_points(point_list):
    ao = AppObjects()
    # Get reference to the sketches and plane
    sketches = ao.root_comp.sketches
    xy_plane = ao.root_comp.xYConstructionPlane

    # Get construction points
    construction_points = ao.root_comp.constructionPoints

    # Create construction point input
    point_input = construction_points.createInput()

    # Create a new sketch and get lines reference
    sketch = sketches.add(xy_plane)
    points = sketch.sketchPoints

    for point in point_list:
        point_3d = adsk.core.Point3D.create(float(point['x']), float(point['y']), float(point['z']))
        sketch_point = points.add(point_3d)
        # Create construction point by point
        point_input.setByPoint(sketch_point)
        const_point = construction_points.add(point_input)
        const_point.name = point['name']


# Simple add-in to create a plate with holes
class HolesCommand(Fusion360CommandBase):

    # Run when the user presses OK
    def on_execute(self, command: adsk.core.Command,
                   inputs: adsk.core.CommandInputs,
                   args, input_values):

        the_file_name = input_values['the_file_name']

        # Read in the csv hole and return a list of 1 dictionary per hole
        hole_list = csv_dict_list(the_file_name)

        # Create holes based on the imported csv
        make_holes(hole_list)

    # Run when the user selects your command icon from the Fusion 360 UI
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        csv_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'holes_csv.csv')

        ao = AppObjects()

        inputs.addStringValueInput('the_file_name', 'Input File: ', csv_file)



# Simple add-in to create a plate with holes
class PointMakerCommand(Fusion360CommandBase):

    # Run when the user presses OK
    def on_execute(self, command: adsk.core.Command,
                   inputs: adsk.core.CommandInputs,
                   args, input_values):

        # Get the values from the user input
        the_file_name = input_values['the_file_name']

        # Read in the csv hole and return a list of 1 dictionary per hole
        point_list = csv_dict_list(the_file_name)

        # Create holes based on the imported csv
        make_points(point_list)

    # Run when the user selects your command icon from the Fusion 360 UI
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        csv_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PointMaker.csv')

        inputs.addStringValueInput('the_file_name', 'Input File: ', csv_file)