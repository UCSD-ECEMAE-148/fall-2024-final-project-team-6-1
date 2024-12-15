# MAE 148 Fall 2024 Team 6 Final Project

## Table of Contents
- [Team Members](#team-members)
- [Overview](#overview)
- [Software](#software)
- [Hardware](#hardware)
- [Assembled Robot](#assembled-robot)
- [Final Project Demo](#final-project-demo)
- [Results](#results)

## Team Members
- Clayton Hoxworth (MAE)
- Daniel Cruz (ECE)
- Jonathan Cohen (MAE)
- Lucca Frey (MAE)

## Overview
We want to create a self-parking robot, which follows a centerline road path 
with a certain color, and with one input can park in 3 different desired parking spots. 
We also want this robot to go back and forth along this line until this input is given.

## Software
We used OpenCV to recognize lines as it is driving, as well as to associate each parking spot 
with its respective controller input.

We trained parking maneuver motions to both enter and exit the 
parking spot. We tracked RPM and Servo values and used them to normalize our input values. 
We also used a VESC to perform the U-turns at the ends of the centerline.

## Hardware
We used Fusion360 to create CAD models to mount the robot's required electronics.

## Assembled Robot
*(Add an image of the assembled robot here, if available.)*

## Final Project Demo
*(Add a link to a video demo or a description here.)*

## Results
The robot was able to travel back and forth along the centerline and perform U-turns at the 
ends well. It correctly identified each parking spot and performed the parking maneuvers when 
desired. The only issues were for the robot to fully enter the spot consistently, as well as that
the U-turn radius was a bit large.
