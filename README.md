# Project Manim

My journey in learning manim for creating physics animation
This code runs on Manim 3b1b and not ManimCE

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv _venv`
3. Activate virtual environment
4. Install dependencies: `pip install -r requirements.txt`

## Current Progress
The implementation of pytorch into processing some of the code with GPU for better performance
### Settign Up _testvenv
For the creation of a test environment
Once cloned the repository and setting up a default environment. create another virtual environment and install the same packages + pytorch based on your set up following https://pytorch.org/get-started/locally/



## Usage

The project is divided into 3 packages or building blocks namely:
1. objects
2. utils
3. scenes

### 1. objects
Where physics objects live things such as: fields, particles, waves
### 2. utils
Where most functions and calculations are
### 3. scenes
Where scene creation codes are

## To run codes for scene generation:
### Once your Env is acativated do:
manimgl scenes/your-desire-code.py -w

other question you email me at: minsopheaktra@me.com