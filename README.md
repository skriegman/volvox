# volvox

First, make sure you have voxcraft:

```git clone https://github.com/voxcraft/voxcraft-sim.git```

You'll need to swtich branches to get the volvox model:

```git checkout dev-sam```

Build it:

```mkdir build && cd build && cmake .. && make -j10```

Note the build dir path

```pwd``` 

and put it [here](https://github.com/skriegman/volvox/blob/10b9a14a7cccd90ee32a09ff6807c8f901dbc989/single_robot.py#L32).

Now with python3 run the script with seed 0:

```python single_robot.py 0``` 

