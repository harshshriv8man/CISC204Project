# CISC/CMPE 204 Modelling Project

Welcome to the major project for CISC/CMPE 204!

Change this README.md file to summarize your project, and provide pointers to the general structure of the repository. How you organize and build things (which files, how you structure things, etc) is entirely up to you! The only things you must keep in place are what is already listed in the **Structure** section below.

## Summary

What if a SAT Solver could be used to run a game? Well, it turns out it can! In part.

Story:

This program is a game set in a future where the people of Earth have colonized a distant planet named "Post Tenebras Spero Lucem" after the many lives it took to get there. However, not all hope is lost for those lives,
as every person on the journey was injected with a syrum before liftoff that allowed them to stay alive for an extended period in open space (thank science!). Mission Saviour has been initiated, and we need you to navigate
the rocket through the stages the original ship took, making your path to save as many people as possible while still being able to reach Post Tenebras Spero Lucem in the end. How do you do this? Well, we've equipped the
ship computer with 6 beacons that can call out, gather and save people within a 3x3 SpaceGrid^TM around itself. The ship computer will pick the most optimal places to put these 6 beacons along your entire journey, and can
only reach out one cell (including diagonals) from the rocket to place these beacons. So as the captain of this vessel, you get access to experimental technology, allowing you to summon SpaceObjects^TM anywhere along the
rocket's journey that did not previously contain anything. When the rocket runs into any of your SpaceObjects, a planet, or the edge of the mission zone, it will turn right 90 degrees until it can move forward again. 
We've also equipped the passengers of the previous mission with rocket-proof armour, so they will survive a direct impact by the rocket. But please keep note, the armour does not midigate the pain.

Good luck, Captain.
People of Earth, signing off.

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

The object of the game is to save as many people stranded in space as you can before the rocket completes its journey. You can do this by moving the rocket close to the stranded people; it will place a beacon once its close enough, and all people within the beacon's radius will be saved. The rocket will automatically place the beacons in the most optimal place it can along its path, so it's up to you to get it there. You only get six beacons per game, so be strategic about where you place them! You can move the rocket by summoning SpaceObjects in front of the rocket, redirecting its path. The rocket will turn 90 degrees right whenever it runs into a SpaceObject, a planet, or the edge of the grid, so try to use the natural features of space to your advantage. You can enter SpaceObjects into the grid when prompted, they will take the form "x, y, grid", where all three are integers. The first two are the coordinates of your location, and the third is which stage you would like the SpaceObject to be placed in. Make sure you have the spaces and commas just like the example, or it may not work.

How to modify those default settings:

1. To get larger planets and grids to work with, change the constant 'RADIUS' to anything >= 2. WARNING: The larger you set this value, the exponentially many constraints there will be for the SAT Solver to solve, so at larger values, depending on your computer, it may or may not successfully run. Default is 2.
2. To change the range at which Beacons can save people, change the constant 'BEACON_RANGE'. Make it as large as you want (within the bounds of the grid), or set it to 0 so no one can be saved! Up to you. Default is 1.
   Example: BEACON_RANGE = 1 means:
   xxx
   x0x
   xxx
   Where x is the saving range and 0 is the Beacon.
3. To increase or decrease the number of Beacons the SAT Solver can place, change constraint.add_at_most_k(E, 6, beacons) such that the 6 is the number of max Beacons you would like. Default is 6.
