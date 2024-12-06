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

Other:

Constraints are added to decide where the Beacon can't go, then based on that, the SAT Solver will choose up to 6 (or however many you change it to) Beacons to be True (placed in the valid locations). It will not tell you how many people are saved, however based on the locations of the Beacons and the BEACON_RADIUS, it's simple enough to interpret.

## Structure

* `documents`: Contains folders for both of your draft and final submissions. README.md files are included in both.
* `run.py`: General wrapper script that you can choose to use or not. Only requirement is that you implement the one function inside of there for the auto-checks.
* `test.py`: Run this file to confirm that your submission has everything required. This essentially just means it will check for the right files and sufficient theory size.

## How to run

To run with default settings, simply run run.py.

Instructions:

When you run the program, it will print three stages containing the environment for each stage (grid).

Green True means Planet (Later will also represent SpaceObjects and the Rocket), yellow False means checkpoint (The rocket must reach these in order to move on to the next stage),
blue True means Person, and red False means empty space.

A person will print over top of the rocket if the rocket moves through a person, so don't be afraid that the rocket disappears at some point along its journey!

The rocket will start in stage 1 in (or 1 above in the case of even radii planets) the center of the planet, one column to the right.

The rocket can move through empty space, checkpoints and people. If the rocket is trapped in a loop, the program will end.

The rocket must reach the final column in stage 1 to continue; go through a checkpoint beneath the planet, then above the planet, and finally back to left column in stage 2; and reach the second last column to the right in stage 3 to succeed and have the SAT Solver begin solving.

The object of the game is to save as many people stranded in space as you can before the rocket completes its journey. You can do this by moving the rocket close to the stranded people; Beacons can only be placed within the radius of the rocket along its path (default is 1), and all people within the beacon's radius (default 1) will be saved.

Remember, the SAT Solver can only place up to 6 Beacons as default, so it will randomly pick out of the valid locations you give it.

You can move the rocket by summoning SpaceObjects in front of the rocket, redirecting its path. The rocket will turn 90 degrees right whenever it runs into a SpaceObject, a planet, or the edge of the grid, so try to use the natural features of space to your advantage.

You can enter SpaceObjects into the grid when prompted, they will take the form "y, x, grid", where y, x, and grid are integers (grid can be 1, 2, or 3. y, x can be any integer within the range of the grid (< 2 * RADIUS, > -1)). The first two are the coordinates of your location, and the third is which stage you would like the SpaceObject to be placed in. Make sure you have the spaces and commas just like the example, or it may not work. Space Objects can only be placed on empty space that is not the starting position of the Rocket.

How to modify those default settings:

1. To get larger planets and grids to work with, change the constant 'RADIUS' to anything >= 2. WARNING: The larger you set this value, the exponentially many constraints there will be for the SAT Solver to solve, so at larger values, depending on your computer, it may or may not successfully run. Default is 2.
2. To change the range at which Beacons can save people, change the constant 'BEACON_RANGE'. Make it as large as you want (within the bounds of the grid), or set it to 0 so no one can be saved! Up to you. Default is 1.
   Example: BEACON_RANGE = 1 means:
   xxx
   x0x
   xxx
   Where x is the saving range and 0 is the Beacon.
3. To increase or decrease the number of Beacons the SAT Solver can place, change constraint.add_at_most_k(E, 6, beacons) such that the 6 is the number of max Beacons you would like. Default is 6.
4. Beacons don't show what grid they're on to begin with, since the compilation time of the SAT Solver took way too long on all of our computers when we added that. But if you would like to see that, and think your computer can handle it, on line 162 (last line in Beacon class), add ', {self.grid}' just to the right of '{self.y}, {self.x}'.
