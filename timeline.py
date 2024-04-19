# Copyright (c) 2024 Xavi Burgos 
# 
# Licensed under the MIT License. See LICENSE file in the project root for full
# license information. Permission is granted to use, copy, modify, and distribute
# this software for any purpose with or without fee, subject to the above
# copyright notice and this permission notice.

import math
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

class Timeline:
  
	def __init__(self, sim: RemoteAPIClient, options: dict = {}):
		"""Create a timeline object
		Args:
			sim (RemoteAPIClient): The CoppeliaSim client object
			options (dict): The timeline options
		"""
		self._sim = sim
		self.__options = options
		if 'default' not in self.__options:
			self.__options['default'] = {}
		elif type(self.__options['default']) != dict:
			raise Exception('"default" option must be a dictionary')
		if 'debug' not in self.__options:
			self.__options['debug'] = False
		elif type(self.__options['debug']) != bool:
			raise Exception('"debug" option must be a boolean')
		if 'yoyo' not in self.__options:
			self.__options['yoyo'] = False
		elif type(self.__options['yoyo']) != bool:
			raise Exception('"yoyo" option must be a boolean')
		if 'steps_per_second' not in self.__options:
			self.__options['steps_per_second'] = 240
		elif type(self.__options['steps_per_second']) != int:
			raise Exception('"steps_per_second" option must be an integer')
		if 'debugs_per_second' not in self.__options:
			self.__options['debugs_per_second'] = 2
		elif type(self.__options['debugs_per_second']) != int:
			raise Exception('"debugs_per_second" option must be an integer')
		elif self.__options['debugs_per_second'] > self.__options['steps_per_second']:
			raise Exception(f'"debugs_per_second" cannot be greater than "steps_per_second" (<= {self.__options["steps_per_second"]})')
		if 'onStart' in self.__options:
			if not callable(self.__options['onStart']):
				raise Exception('"onStart" option must be a function')
		if 'onUpdate' in self.__options:
			if not callable(self.__options['onUpdate']):
				raise Exception('"onUpdate" option must be a function')
		if 'onComplete' in self.__options:
			if not callable(self.__options['onComplete']):
				raise Exception('"onComplete" option must be a function')
		self.__timeline = []
		self.__duration = 0
		self.__previousStart = 0
		self.__previousEnd = 0
		self.__previousDuration = 0
		self.__posibleVars = ['position', 'rotation', 'angle', 'duration', 'ease', 'delay', 'onStart', 'onUpdate', 'onEnd']

	def __decodePosition(self, position) -> float:
		"""Decode the position
		Args:
			position (float): The position in the timeline
		Returns:
			float: The position in the timeline
		"""
		if position is None:
			return self.__duration
		if type(position) == int or type(position) == float:
			if position < 0:
				raise Exception('"position" cannot be negative')
			return position
		if type(position) != str:
			raise Exception('"position" is optional, but must be a number or a string')
		if position == '':
			raise Exception('"position" cannot be empty')
		isPercentage = False
		if position.startswith('<') or position.startswith('>'):
			p = position[0]
			position = position[1:]
			if position == '':
				if p == '<':
					return self.__previousStart
				return self.__previousEnd
			if position.endswith('%'):
				position = position[:-1]
				isPercentage = True
			if position == '':
				raise Exception('"position" needs a digit when using percentage')
			if not position.lstrip('-+').replace('.', '').isnumeric():
				raise Exception('"position" must be a number')
			position = float(position)
			if isPercentage:
				position = position / 100
				position *= self.__previousDuration
			if p == '<':
				position = self.__previousStart + position
			else:
				position = self.__previousEnd + position
			if position < 0:
				raise Exception('"position" cannot be negative')
			return position
		if position.startswith('+=') or position.startswith('-='):
			p = position[0]
			position = position[2:]
			if position.endswith('%'):
				position = position[:-1]
				isPercentage = True
			if position == '':
				raise Exception('"position" needs a digit when using percentage')
			if not position.lstrip('-+').replace('.', '').isnumeric():
				raise Exception('"position" must be a number')
			position = float(position)
			if position < 0:
				raise Exception('"position" cannot be negative')
			if isPercentage:
				position = position / 100
				position *= self.__duration
			if p == '+':
				position = self.__duration + position
			else:
				position = self.__duration - position
			if position < 0:
				raise Exception('"position" cannot be negative')
			return position
		if position.endswith('%'):
			isPercentage = True
			position = position[:-1]
		if not position.lstrip('-+').replace('.', '').isnumeric():
			raise Exception('"position" must be a number')
		position = float(position)
		if position < 0:
			raise Exception('"position" cannot be negative')
		if isPercentage:
			position = position / 100
			position *= self.__duration
		if position < 0:
			raise Exception('"position" cannot be negative')
		return position

	def __mergeVars(self, vars: dict) -> dict:
		"""Merge the variables with the default variables
		Args:
			vars (dict): The target variables
		Returns:
			dict: The complete variables
		"""
		vars_ = self.__options['default'].copy()
		for key in vars:
			vars_[key] = vars[key]
		return vars_

	def __checkVars(self, vars: dict):
		"""Check the variables
		Args:
			vars (dict): The target variables
		"""
		found = False
		for key in self.__posibleVars:
			if key in vars:
				found = True
				break
		if not found:
			raise Exception('No target variables found')
		for key in vars:
			value = vars[key]
			if key == 'position':
				if type(value) != list:
					raise Exception('"position" must be a list')
				if len(value) != 3:
					raise Exception('"position" must have 3 values')
				for i in range(3):
					if type(value[i]) != int and type(value[i]) != float:
						raise Exception('"position" values must be numbers')
			elif key == 'rotation':
				if type(value) != int and type(value) != float:
					raise Exception('"rotation" must be a number')
			elif key == 'angle':
				if type(value) != int and type(value) != float:
					raise Exception('"angle" must be a number')
			elif key == 'duration':
				if type(value) != int and type(value) != float:
					raise Exception('"duration" must be a number')
				if value < 0:
					raise Exception('"duration" cannot be negative')
			elif key == 'ease':
				if value is not None and not callable(value):
					raise Exception('"ease" must be a function')
			elif key == 'delay':
				if type(value) != int and type(value) != float:
					raise Exception('"delay" must be a number')
				if value < 0:
					raise Exception('"delay" cannot be negative')
			elif key == 'onStart' or key == 'onUpdate' or key == 'onEnd':
				if not callable(value):
					raise Exception(f'"{key}" must be a function')
			elif self.__options['debug']:
				print(f'Warning: "{key}" is not a valid variable')
  
	def __completeVars(self, vars: dict) -> dict:
		"""Complete the variables
		Args:
			vars (dict): The target variables
		Returns:
			dict: The complete variables
		"""
		if 'duration' not in vars:
			vars['duration'] = 1
		if 'ease' not in vars:
			vars['ease'] = self.easeInOut
		if 'delay' not in vars:
			vars['delay'] = 0
		return vars

	def to(self, target: dict, vars: dict, position = None) -> 'Timeline':
		"""Add a target animation to the timeline
		Args:
			target (dict): The target object
			vars (dict): The target variables
			position (float): The position in the timeline
		Returns:
			Timeline: The timeline object
		"""
		name = self._sim.getObjectName(target)
		vars = self.__mergeVars(vars)
		self.__checkVars(vars)
		vars = self.__completeVars(vars)
		delay = vars['delay']
		start = self.__decodePosition(position) + delay
		duration = vars['duration']
		end = start + duration
		for t in self.__timeline:
			if target != t['target']:
				continue
			if end > t['start'] and start < t['end']:
				raise Exception('Target animation overlaps with another previous animation')
		self.__timeline.append({
			'target': target,
			'name': name,
			'vars': vars,
			'start': start,
			'end': end,
			'duration': duration
		})
		self.__previousStart = start
		self.__previousEnd = end
		self.__previousDuration = vars['duration']
		if end > self.__duration:
			self.__duration = end
		return self

	@staticmethod
	def easeInOut(t: float) -> float:
		"""The ease-in-out function
		Args:
			t (float): The time (0 to 1)
		Returns:
			float: The eased time
		"""
		if t < 0.5:
			return 4 * t * t * t
		t = 2 * t - 2
		return 0.5 * t * t * t + 1

	@staticmethod
	def easeOut(t: float) -> float:
		"""The ease-out function
		Args:
			t (float): The time (0 to 1)
		Returns:
			float: The eased time
		"""
		t -= 1
		return t * t * t + 1

	@staticmethod
	def easeIn(t: float) -> float:
		"""The ease-in function
		Args:
			t (float): The time (0 to 1)
		Returns:
			float: The eased time
		"""
		return t * t * t

	@staticmethod
	def cubicBezier(t: float, p1x: float, p1y: float, p2x: float, p2y: float) -> float:
		"""The cubicBezier function
		Args:
			t (float): The time (0 to 1)
			p1x (float): The first control point x
			p1y (float): The first control point y
			p2x (float): The second control point x
			p2y (float): The second control point y
		Returns:
			float: The eased time
		"""
		cx = 3.0 * p1x
		bx = 3.0 * (p2x - p1x) - cx
		ax = 1.0 - cx - bx
		cy = 3.0 * p1y
		by = 3.0 * (p2y - p1y) - cy
		ay = 1.0 - cy - by
		def sampleCurveX(t):
			return ((ax * t + bx) * t + cx) * t
		def sampleCurveY(t):
			return ((ay * t + by) * t + cy) * t
		def sampleCurveDerivativeX(t):
			return (3.0 * ax * t + 2.0 * bx) * t + cx
		def solveCurveX(x):
			t2 = x
			for _ in range(8):
				x2 = sampleCurveX(t2) - x
				if abs(x2) < 1e-3:
					return t2
				d2 = sampleCurveDerivativeX(t2)
				if abs(d2) < 1e-3:
					break
				t2 = t2 - x2 / d2
			return t2
		return sampleCurveY(solveCurveX(t))

	@staticmethod
	def linear(t: float) -> float:
		"""The linear function
		Args:
			t (float): The time (0 to 1)
		Returns:
			float: The eased time
		"""
		return t

	def __yoyo(self, timeline: list, duration: float) -> tuple:
		"""Yoyo the timeline
		Args:
			timeline (list): The timeline
			duration (float): The duration
		Returns:
			tuple: The timeline and the duration
		"""
		duration *= 2
		timeline_ = []
		for t in timeline:
			t = t.copy()
			start = t['start']
			t['start'] = duration - t['end']
			t['end'] = duration - start
			timeline_.append(t)
		timeline_.reverse()
		timeline.extend(timeline_)
		return timeline, duration

	@staticmethod
	def deg2rad(deg: float) -> float:
		"""Convert degrees to radians
		Args:
			deg (float): The angle in degrees
		Returns:
			float: The angle in radians
		"""
		return deg * math.pi / 180

	@staticmethod
	def rad2deg(rad: float) -> float:
		"""Convert radians to degrees
		Args:
			rad (float): The angle in radians
		Returns:
			float: The angle in degrees
		"""
		return rad * 180 / math.pi

	def play(self) -> 'Timeline':
		"""Play the timeline
		Returns:
			Timeline: The timeline object
		"""
		duration = self.__duration
		timeline = self.__timeline.copy()
		timeline.sort(key=lambda x: x['start'])
		if self.__options['yoyo']:
			timeline, duration = self.__yoyo(timeline, duration)
		sps = self.__options['steps_per_second']
		duration *= sps
		for t in timeline:
			t['start'] *= sps
			t['end'] *= sps
			t['duration'] *= sps
		if self.__options['debug']:
			for i in range(len(timeline)):
				t = timeline[i]
				s = int(t['start'] / sps * 100) / 100
				e = int(t['end'] / sps * 100) / 100
				d = int(t['duration'] / sps * 100) / 100
				print(f'INFO: Event {i+1}: {t["name"]} -> Start: {s}, End: {e}, Duration: {d}')
			print('')
		duration = math.ceil(duration)
		nTimelines = len(timeline)
		isDebug = self.__options['debug']
		if 'onStart' in self.__options:
			self.__options['onStart']()
		for i in range(duration + 1):
			isDebugTime = False
			if isDebug and i % (sps // self.__options['debugs_per_second']) == 0:
				isDebugTime = True
			for j in range(nTimelines):
				event = timeline[j]
				if i == event['start']:
					if 'position' in event['vars']:
						if 'forcedFinalPosition' in event:
							event["initialPosition"] = event["vars"]["position"]
							event["vars"]["position"] = event["forcedFinalPosition"]
						else:
							initialPosition = self._sim.getObjectPosition(event['target'])
							event["initialPosition"] = initialPosition
							if self.__options['yoyo'] and j < nTimelines // 2:
								timeline[nTimelines - j - 1]["forcedFinalPosition"] = initialPosition
						if isDebug:
							p = event["initialPosition"].copy()
							p[0] = int(p[0] * 100) / 100
							p[1] = int(p[1] * 100) / 100
							p[2] = int(p[2] * 100) / 100
							print(f'INFO: {event["name"]} position has started at: {p[0]}, {p[1]}, {p[2]}')
					if 'rotation' in event['vars']:
						if 'forcedFinalRotation' in event:
							event["initialRotation"] = event["vars"]["rotation"]
							event["vars"]["rotation"] = event["forcedFinalRotation"]
						else:
							initialRotation = self._sim.getObjectOrientation(event['target'])
							event["initialRotation"] = initialRotation
							if self.__options['yoyo'] and j < nTimelines // 2:
								timeline[nTimelines - j - 1]["forcedFinalRotation"] = initialRotation
						if isDebug:
							r = event["initialRotation"].copy()
							r[0] = int(r[0] * 100) / 100
							r[1] = int(r[1] * 100) / 100
							r[2] = int(r[2] * 100) / 100
							print(f'INFO: {event["name"]} rotation has started at: {r[0]}, {r[1]}, {r[2]}')
					if 'angle' in event['vars']:
						if 'forcedFinalAngle' in event:
							event["initialAngle"] = event["vars"]["angle"]
							event["vars"]["angle"] = event["forcedFinalAngle"]
						else:
							initialAngle = self._sim.getJointTargetPosition(event['target'])
							event["initialAngle"] = initialAngle
							if self.__options['yoyo'] and j < nTimelines // 2:
								timeline[nTimelines - j - 1]["forcedFinalAngle"] = initialAngle
						if isDebug:
							deg = self.rad2deg(event["initialAngle"])
							rad = int(event["initialAngle"] * 10000) / 10000
							deg = int(deg * 100) / 100
							print(f'INFO: {event["name"]} angle has started at: {deg}° ({rad} rad)')
					if 'onStart' in event['vars']:
						event['vars']['onStart'](event['target'])
				elif i > event['start'] and i < event['end'] and ('position' in event['vars'] or 'rotation' in event['vars'] or 'angle' in event['vars']):
					ease = event['vars']['ease']
					if 'position' in event['vars']:
						position = event['vars']['position']
						t = (i - event['start']) / event['duration']
						t = ease(t)
						x = position[0] * t + event["initialPosition"][0] * (1 - t)
						y = position[1] * t + event["initialPosition"][1] * (1 - t)
						z = position[2] * t + event["initialPosition"][2] * (1 - t)
						if isDebugTime:
							print(f'INFO: {event["name"]} position is: {x}, {y}, {z}')
						self._sim.setObjectPosition(event['target'], [x, y, z])
					if 'rotation' in event['vars']:
						rotation = event['vars']['rotation']
						t = (i - event['start']) / event['duration']
						t = ease(t)
						x = rotation[0] * t + event["initialRotation"][0] * (1 - t)
						y = rotation[1] * t + event["initialRotation"][1] * (1 - t)
						z = rotation[2] * t + event["initialRotation"][2] * (1 - t)
						if isDebugTime:
							print(f'INFO: {event["name"]} rotation is: {x}, {y}, {z}')
						self._sim.setObjectOrientation(event['target'], [x, y, z])
					if 'angle' in event['vars']:
						angle = event['vars']['angle']
						t = (i - event['start']) / event['duration']
						t = ease(t)
						angle = angle * t + event["initialAngle"] * (1 - t)
						if isDebugTime:
							deg = self.rad2deg(angle)
							rad = int(angle * 10000) / 10000
							deg = int(deg * 100) / 100
							print(f'INFO: {event["name"]} angle is: {deg}° ({rad} rad)')
						self._sim.setJointTargetPosition(event['target'], angle)
					if 'onUpdate' in event['vars']:
						event['vars']['onUpdate'](event['target'])
				elif i == event['end']:
					if 'onUpdate' in event['vars']:
						event['vars']['onUpdate'](event['target'])
					if 'onEnd' in event['vars']:
						event['vars']['onEnd'](event['target'])
					if isDebug:
						if 'position' in event['vars']:
							p = event['vars']['position'].copy()
							p[0] = int(p[0] * 100) / 100
							p[1] = int(p[1] * 100) / 100
							p[2] = int(p[2] * 100) / 100
							print(f'INFO: {event["name"]} position has ended at: {p[0]}, {p[1]}, {p[2]}')
						if 'rotation' in event['vars']:
							r = event['vars']['rotation'].copy()
							r[0] = int(r[0] * 100) / 100
							r[1] = int(r[1] * 100) / 100
							r[2] = int(r[2] * 100) / 100
							print(f'INFO: {event["name"]} rotation has ended at: {r[0]}, {r[1]}, {r[2]}')
						if 'angle' in event['vars']:
							deg = self.rad2deg(event['vars']['angle'])
							rad = int(event['vars']['angle'] * 10000) / 10000
							deg = int(deg * 100) / 100
							print(f'INFO: {event["name"]} angle has ended at: {deg}° ({rad} rad)')
			if 'onUpdate' in self.__options:
				self.__options['onUpdate']()
			self._sim.step()
		if 'onComplete' in self.__options:
			self.__options['onComplete']()
		return self