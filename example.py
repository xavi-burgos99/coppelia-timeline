import coppelia
from coppelia import deg2rad, rad2deg
from timeline import Timeline

# Start the connection
sim, client = coppelia.connect()

# Get the objects in the scene
cuboid  = sim.getObjectHandle('Cuboid')
joint1 = sim.getObjectHandle('Joint1')
joint2 = sim.getObjectHandle('Joint2')
suctionPad = sim.getObjectHandle('suctionPad')

# Set the start position of the cube
sim.setObjectPosition(cuboid, [0, 0, 0.5])

# Start the simulation
sim.startSimulation()

# Create a new timeline
tl = Timeline(sim, {
	'default': {
		'duration': 2    # Default duration for all movements
	},
	'yoyo': True,      # Repeat the timeline reversely
	'onStart': lambda: print('Start timeline'),
	'onUpdate': lambda: print('Update timeline'),
	'onComplete': lambda: print('Complete timeline')
})

# Add movements to the timeline
tl.to(joint1, {
	'angle': deg2rad(90),
})
tl.to(joint2, {
	'angle': deg2rad(-90),
	'duration': 1	     # Override the default duration
}, '<1')		         # Execute this movement 1 second after the previous movement is started
tl.to(suctionPad, {
	'duration': 0.5,
	'onStart': lambda target: print('Activate suction pad'),
	'onEnd': lambda target: print('Deactivate suction pad')
}, '>-50%')          # Execute this movement 50% before the previous movement is completed
tl.to(joint1, {
	'angle': 0,
	'duration': 1
}, '+=2')            # Execute this movement 2 seconds after the timeline ending

# Start the timeline
tl.play()

# End the simulation
sim.stopSimulation()
