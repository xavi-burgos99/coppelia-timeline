# Copyright (c) 2024 Xavi Burgos 
# 
# Licensed under the MIT License. See LICENSE file in the project root for full
# license information. Permission is granted to use, copy, modify, and distribute
# this software for any purpose with or without fee, subject to the above
# copyright notice and this permission notice.

import math
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

coppelia_client = None
coppelia_sim = None

def connect():
	"""Connect to CoppeliaSim via the Remote API
	Returns:
		RemoteAPIClient: The client object
		RemoteAPIServer: The sim object
	"""
	global coppelia_client, coppelia_sim
	client = RemoteAPIClient()
	sim = client.require('sim')
	sim.setStepping(True)
	coppelia_sim = sim
	coppelia_client = client
	return sim, client

def wait(duration: float, steps_per_second: int = 240):
	"""Wait for a specified duration
	Args:
		duration (float): The duration to wait for
		steps_per_second (int): The number of simulation steps per second
	"""
	global coppelia_sim
	if coppelia_sim is None:
		raise Exception("Not connected to CoppeliaSim, call \"coppelia_connect()\" first.")
	steps = math.ceil(duration * steps_per_second)
	for _ in range(steps):
		coppelia_sim.step()
  
def deg2rad(deg):
	"""Convert degrees to radians
	Args:
		deg (float): The angle in degrees
	Returns:
		float: The angle in radians
	"""
	return deg * math.pi / 180

def rad2deg(rad):
	"""Convert radians to degrees
	Args:
		rad (float): The angle in radians
	Returns:
		float: The angle in degrees
	"""
	return rad * 180 / math.pi
  

""" START SIMULATION: Start the simulation """
# sim.startSimulation()

""" PAUSE SIMULATION: Pause the simulation """
# sim.pauseSimulation()

""" STOP SIMULATION: Stop the simulation """
# sim.stopSimulation()

""" STEP SIMULATION: Step the simulation (next frame) """
# sim.step()

""" GET OBJECTS: Load objects from the scene into a variable """
# cube = sim.getObjectHandle('Cube')
# sphere = sim.getObjectHandle('Sphere')
# joint1 = sim.getObjectHandle('Joint1')
# joint2 = sim.getObjectHandle('Joint2')
# suctionPad = sim.getObjectHandle('SuctionPad')

""" GET OBJECT POSITIONS: Get the position of an object """
# cube_pos = sim.getObjectPosition(cube)
# sphere_pos = sim.getObjectPosition(sphere)

""" SET OBJECT POSITIONS: Set the position of an object """
# sim.setObjectPosition(cube, [0, 0, 0])
# sim.setObjectPosition(sphere, [5, 5, 5])

""" GET JOINT POSITIONS: Get the position of a joint """
# joint1_pos = sim.getJointPosition(joint1)
# joint2_pos = rad2deg(sim.getJointPosition(joint2))

""" SET JOINT POSITIONS: Set the position of a joint """
# sim.setJointPosition(joint1, 0)
# sim.setJointPosition(joint2, rad2deg(90))

""" GET JOINT TARGET POSITIONS: Get the target position of a joint """
# joint1_target = sim.getJointTargetPosition(joint1)
# joint2_target = rad2deg(sim.getJointTargetPosition(joint2))

""" SET JOINT TARGET POSITIONS: Set the target position of a joint """
# sim.setJointTargetPosition(joint1, 0)
# sim.setJointTargetPosition(joint2, deg2rad(90))
