import sys
import math
import time
import random
import asyncio
import threading
import tkinter as tk
from io import StringIO
from PIL import Image, ImageTk
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import CyclicBehaviour
from spade.behaviour import PeriodicBehaviour

#calcular distancia (manhattan tipo city layout)
def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])