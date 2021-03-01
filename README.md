# Saccadic localization of frame-induced position shifted probes 

This repository contains the experiment code, data, and analysis code for the FIPS Saccade experiment. 

## Experiment

Details of the methodology and procedure is found in `MEHTOD.md` file. Psychophysical (perceptual task) and 
eye-tracking (Saccade task) measurements were collected in separate sessions (two sessions per each). There were 
also two training sessions before each part of the experiment, so the order of sessions were `perceptual-training -> 
peceptual-task-1 -> perceptual-task-2 -> saccade-training -> saccade-task-1 -> saccade-task-2`.

_TODO: {experiment flow figure}_

## Procedure

### 1) Perceptual task

Use multiple interleaved QUEST staircase to find 50% proportion of "right-shift" responses. Left and right shifts 
should be randomly interleaved in 2 session of 240 trials each, divided into 6 blocks. 


### 2) Saccade task

- _Fixation period_: Each trial starts with participants fixating on a dot in the center of the screen. 
  After a random interval sampled uniformly from 400-600ms, the frame appears at the left-most position of its path.
- _Stabilization period_: The frame moves for a minimum of 3 cycles of its motion. Probes flash for 3-5 frames at 
  the reversal points of the frame.
- _Cue period_: After the stabilization period, the fixation disappears at one of six points in time equally 
  spaced along a full cycle of motion on each trial. The disappearance is the participants' cue to saccade to the 
  "red" probe.
- _Saccade_: As soon as the gaze position is detected to be 2dva away from center of fixation, the target (red probe) 
  is removed.\

Each session of the Saccade task comprises 384 trials divided into 12 blocks. If fixation was broken, 
the trial was aborted and put at the end of the block.