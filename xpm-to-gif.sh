#!/bin/bash
export EXEC_DIR="$(dirname "$(realpath "${0}")")"

declare argStr=""
for arg in "${@}"
do
  argStr+="${arg}"
  argStr+=$'\uFFFF'
done

gimp --new-instance --no-data --no-fonts --batch-interpreter python-fu-eval --batch - --batch "pdb.gimp_quit(1)" <<END
# -*- coding: $(locale charmap) -*-
import sys

def exit (v):
  sys.stderr.write(v + "\n")
  pdb.gimp_quit(1)

args = u"${argStr}".split(u"\uFFFF")[:-1]

syntax = "Syntax: xpm-to-gif <frames per second>|0 [...]"
if len(args) < 1:
  exit(syntax)
try:
  frameRate = float(args[0])
except ValueError as e:
  exit("Frame duration must be a number\n" + syntax)
if frameRate < 0:
  exit("Frame duration must be a positive number\n" + syntax)

def loadXpm (pathName):
  i = pdb.file_xpm_load(pathName, pathName)
  #pdb.gimp_image_scale_full(i, i.width * 1, i.height * 1, 0)
  pdb.gimp_image_convert_indexed(i, 0, 0, 256, 0, 1, "")
  return i

if frameRate == 0:
  for inPathName in args[1:]:
    i = loadXpm(inPathName)
    outPathName = inPathName + ".gif"
    pdb.file_gif_save(i, i.active_layer, outPathName, outPathName, 0, 0, 1, 0)
    pdb.gimp_image_delete(i)
else:
  if len(args) > 1:
    i = loadXpm(args[1])

    for inPathName in args[2:]:
      layer = i.new_layer()

      i1 = loadXpm(inPathName)
      pdb.gimp_edit_copy(i1.active_layer)
      pdb.gimp_image_delete(i1)

      selection = pdb.gimp_edit_paste(layer, True)
      pdb.gimp_floating_sel_anchor(selection)

    outPathName = args[1] + ".gif"
    pdb.file_gif_save(i, i.active_layer, outPathName, outPathName, 0, 0, 1000 / frameRate, 0)
    pdb.gimp_image_delete(i)
END
