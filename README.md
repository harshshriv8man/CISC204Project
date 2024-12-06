# CISC/CMPE 204 Modelling Project

Welcome to the major project for CISC/CMPE 204!

Change this README.md file to summarize your project, and provide pointers to the general structure of the repository. How you organize and build things (which files, how you structure things, etc) is entirely up to you! The only things you must keep in place are what is already listed in the **Structure** section below.

## Summary

Given the fuel of a rocket and the radius of the orbital assist body, will the mission from the take off-body, to an orbital assist around the orbital assist body, to landing on the landing body be successful?

This will be using a grid to represent space where the rocket takes up one cell and can move one cell at a time. There will be conditions that the rocket needs to meet to move to certain cells, and fuel will be used up when doing so. These conditions are split into three parts: takeoff, assist, and landing.



## Structure

* `documents`: Contains folders for both of your draft and final submissions. README.md files are included in both.
* `run.py`: General wrapper script that you can choose to use or not. Only requirement is that you implement the one function inside of there for the auto-checks.
* `test.py`: Run this file to confirm that your submission has everything required. This essentially just means it will check for the right files and sufficient theory size.

## How to run

To run with default settings, simply run run.py.

Instructions:

When you run the program, it will print three stages containing the environment for each stage (grid).

Green True means Planet (Later will also represent SpaceObjects), yellow False means checkpoint (The rocket must reach these in order to move on to the next stage),
blue True means Person, and red False means empty space.

The rocket will start in stage 1 in (or 1 above in the case of even radii planets) the center of the planet, one column to the right.

The rocket can move through empty space, checkpoints and people. If the rocket is trapped in a loop, the program will end.

The rocket must reach the final column in stage 1 to continue; go through a checkpoint beneath the planet, then above the planet, and finally back to left column in stage 2; and reach the second last column to the right in stage 3 to succeed and have the SAT Solver begin solving.

You can summon SpaceObjects to redirect

Story:

How to modify those default settings:

1. To get larger planets and grids to work with, change the constant 'RADIUS' to anything >= 2. WARNING: The larger you set this value, the exponentially many constraints there will be for the SAT Solver to solve, so at larger values, depending on your computer, it may or may not successfully run. Default is 2.
2. To change the range at which Beacons can save people, change the constant 'BEACON_RANGE'. Make it as large as you want (within the bounds of the grid), or set it to 0 so no one can be saved! Up to you. Default is 1.
   Example: BEACON_RANGE = 1 means:
   xxx
   x0x
   xxx
   Where x is the saving range and 0 is the Beacon.
3. To increase or decrease the number of Beacons the SAT Solver can place, change constraint.add_at_most_k(E, 6, beacons) such that the 6 is the number of max Beacons you would like. Default is 6.
