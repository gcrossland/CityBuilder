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
args = u"${argStr}".split(u"\uFFFF")[:-1]

for inPathName in args:
  outPathName = inPathName + ".gif"
  i = pdb.file_xpm_load(inPathName, inPathName)
  #pdb.gimp_image_scale_full(i, i.width * 1, i.height * 1, 0)
  #pdb.file_png_save_defaults(i, i.active_layer, outPathName, outPathName)
  pdb.gimp_image_convert_indexed(i, 0, 0, 256, 0, 1, "")
  pdb.file_gif_save(i, i.active_layer, outPathName, outPathName, 0, 0, 1, 0)
  pdb.gimp_image_delete(i)
END
