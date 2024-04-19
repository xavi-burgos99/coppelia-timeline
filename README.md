# Coppelia Sim and Timelines for Python
This is a Python wrapper for the CoppeliaSim remote API. It is based on the official remote API for CoppeliaSim. This library also includes a timeline module that allows you to create multiple movements in parallel.

# Installation
This library uses the ZeroMQ remote API for CoppeliaSim. To use this library, you need to install the official package.

## ZeroMQ remote API
You can install the dependencies using the following command:

```bash
pip install -r requirements.txt
```

or you can install the dependencies manually:

```bash
pip install coppeliasim_zmqremoteapi_client
```

## Coppelia and Timeline modules
To use the timeline module, you need to import `coppelia` and `timeline` modules into your project. You can do this by copying the files into your project.

# Usage
To use this library, is enough to import the `coppelia` file and start using the functions. Alternatively, you can also import the `timeline` module to use the timeline functions, enabling multiple movements to be executed in parallel. Here is a simple example of how to use this library:

```python
import coppelia
from coppelia import deg2rad, rad2deg
from timeline import Timeline

# Start the connection
sim, client = coppelia.connect()

# Get joints objects
joint1 = sim.getObjectHandle('Joint1')
joint2 = sim.getObjectHandle('Joint2')

# Start the simulation
sim.startSimulation()

# Create a new timeline
tl = Timeline(sim, {
	'default': { 'duration': 3 },  # Default variables for all movements
	'onComplete': lambda: print('Complete timeline')
})

# Add first movement of Joint1 to the timeline
tl.to(joint1, {
	'angle': deg2rad(90)   # Set the target angle
})

# Add second movement of Joint2 to the timeline
tl.to(joint2, {
	'angle': deg2rad(-90), # Set the target angle
	'duration': 2          # Override the default duration
}, '<1')                 # Execute 1 second after previous movement is started

# Start the timeline
tl.play()

# End the simulation
sim.stopSimulation()
```

Also, you can check a more complex example in the [example.py](example.py) file.

# Coppelia documentation
This library includes the following functions to interact with the CoppeliaSim server:

## `connect()`:
Starts the connection with the CoppeliaSim server.

> ### Returns
> * `sim` (CoppeliaSim): The CoppeliaSim object.
> * `client` (ZMQRemoteAPIClient): The ZeroMQ remote API client.

<br>

## `wait(duration, steps_per_second=240)`:
Waits for the given duration before continuing the execution.

> ### Parameters
> * `duration` (float): The duration to wait.
> * `steps_per_second` (int): The number of steps per second. Default is 240.

<br>

## `deg2rad(degrees)`:
Converts the given degrees to radians.

> ### Parameters
> * `degrees` (float): The degrees to convert.

> ### Returns
> * `radians` (float): The radians converted.

<br>

## `rad2deg(radians)`:
Converts the given radians to degrees.

> ### Parameters
> * `radians` (float): The radians to convert.

> ### Returns
> * `degrees` (float): The degrees converted.


# Timeline documentation
To create a new timeline, you need to initialize a new `Timeline` object. The timeline object receives the CoppeliaSim object and a dictionary with the timeline configuration, like in the example below:

```python
tl = Timeline(sim, {
	'default': { 'duration': 3 },  # Default variables for all movements
	'onComplete': lambda: print('Complete timeline')
})
```

## Start execution
To start the timeline execution, you need to call the `play` function. This function will start the timeline execution of an existing timeline object, like in the example below:

```python
tl.play()
```

## Timeline configuration
The configuration dictionary can have the following keys:

| Key | Description | Default | Possible values |
| --- | --- | --- | --- |
| `debug` | If the timeline should print debug messages. | `False` | `True` or `False` |
| `debugs_per_second` | The number of debug messages per second. | `2` | Integer greater than 0 and less than `steps_per_second` |
| `default` | Variables that will be used as default for all movements. | `{}` | [Movement variables](#movement-variables) |
| `steps_per_second` | The number of steps per second. | `240` | Integer greater than 0 |
| `yoyo` | If the timeline should repeat reversely after the end. | `False` | `True` or `False` |
| `onStart` | Callback function that will be executed when the timeline starts. | `None` | Function |
| `onUpdate` | Callback function that will be executed when the timeline updates. | `None` | Function |
| `onComplete` | Callback function that will be executed when the timeline completes. | `None` | Function |

## Adding movements
To add a new movement to the timeline, you need to call the `to` function. This function receives the target object, a dictionary with the movement variables and, optionally, the position of the movement in the timeline, like in the example below:

```python
tl.to(joint1, {
	'angle': deg2rad(90),
	'duration': 2
	'delay': 1
}, '+=2')
```

### Movement variables
The movement variables dictionary can have the following keys:

| Key | Description | Default | Possible values |
| --- | --- | --- | --- |
| `angle` | The target angle of the movement for joints. | `None` | Float |
| `delay` | The delay of the movement. | `0` | Float greater than or equal to 0 |
| `duration` | The duration of the movement. | `1` | Float greater than 0 |
| `ease` | The ease function of the movement. | `Timeline.easeInOut` | [Ease functions](#ease-functions) |
| `onStart` | Callback function that will be executed when the movement starts. | `None` | Function |
| `onUpdate` | Callback function that will be executed when the movement updates. | `None` | Function |
| `onEnd` | Callback function that will be executed when the movement ends. | `None` | Function |
| `position` | The target position of the movement for any object. | `None` | List of floats `[x, y, z]` |
| `rotation` | The target orientation of the movement for any object. | `None` | List of floats `[x, y, z]` |

### Position in the timeline
The position of the movement in the timeline can be defined in three ways:

#### Absolute position
The movement will start at the given time in seconds or percentage of the timeline. Examples:

* `2`: The movement will start 2 seconds after the timeline starts.
* `2.5`: The movement will start at 2.5 seconds after the timeline starts.
* `50%`: The movement will start at 50% of the timeline.

#### Relative position
The movement will take into account the previous movement to calculate the start time. Use the `<` or `>` symbol to indicates if the movement should start at the start or end, respectively, of the previous movement. Examples:

* `<`: The movement will start at the same time as the previous movement.
* `>`: The movement will start at the end of the previous movement. (Used by default)
* `<2`: The movement will start 2 seconds after the previous movement starts.
* `<-1`: The movement will start 1 second before the previous movement starts.
* `>-2.5`: The movement will start 2.5 seconds before the previous movement ends.
* `>+1`: The movement will start 1 second after the previous movement ends.
* `<50%`: The movement will start at 50% of the previous movement.
* `>-50%`: The movement will start at 50% before the previous movement ends.

#### End position
The movement will start at the end of the timeline. Use the `+=` and `-=` symbols to indicates if the movement should start after or before the timeline ends, respectively. Examples:

* `+=1`: The movement will start 1 second after the timeline ends.
* `+=2.5`: The movement will start at 2.5 seconds after the timeline ends.
* `+=50%`: The movement will start at 50% (respect to the timeline duration) after the timeline ends.
* `-=2`: The movement will start 2 seconds before the timeline ends.
* `-=1.5`: The movement will start at 1.5 seconds before the timeline ends.
* `-=25%`: The movement will start at 25% (respect to the timeline duration) before the timeline ends.


## Ease functions
One of movement variables is the `ease` function. This function is used to interpolate the movement between the start and end values. By

All ease functions will receive a float `t` that represents the time in the range of 0 to 1. The function should also return a float in the range of 0 to 1.

The following ease functions are available:

* `linear(t)`: The movement will be constant during the movement execution.

* `easeIn(t)`: The movement will start slow and will accelerate at the end of the movement.

* `easeOut(t)`: The movement will start fast and will decelerate at the end of the movement.

* `easeInOut(t)`: The movement will start slow, accelerate in the middle, and decelerate at the end of the movement.


### Custom ease function
Also, a custom ease function can be defined. To do this, we will provide the `cubicBezier` function that receives two vectors, represented by `p1x` and `p1y` for the first vector and `p2x` and `p2y` for the second vector. The function will return the custom ease function with the desired acceleration curve.

To create a custom ease function, you can use the following example:

```python
# Define the custom ease function
def myCustomEase(t):
	return cubicBezier(t, 0.25, 0, 0.25, 1)

tl.to(joint1, {
	'angle': deg2rad(90),
	'ease': myCustomEase    # Set the custom ease function here
})
```

# Acknowledgments
This library is based on the official remote API for CoppeliaSim. You can find more information about the remote API in the [CoppeliaSim documentation](https://www.coppeliarobotics.com/helpFiles/en/remoteApiOverview.htm).

# License
This library is licensed under the MIT License. You can find more information in the [LICENSE](LICENSE) file.
