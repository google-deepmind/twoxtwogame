# Copyright 2024 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Prepare package for export to CTAN.

This script:
* Compiles a PDF of twoxtwogame_doc.tex.
* Packages the relevant files into a zip archive.

Usage:
```python
python3 ./prepare_ctan_upload.py --dir=~/twoxtwogame
```
"""

import argparse
import os
import shutil
import subprocess
import tempfile

_README_FILENAME = "README.md"
_LICENSE_FILENAME = "LICENSE"
_STY_FILENAME = "twoxtwogame.sty"
_DOC_FILENAME = "twoxtwogame_doc.tex"
_PDF_FILENAME = "twoxtwogame_doc.pdf"
_LATEX = "pdflatex"
_STRIP_START = "## Example Functionality\n"
_STRIP_END = "## Installation\n"

parser = argparse.ArgumentParser(description="Prepare CTAN package.")
parser.add_argument("--dir", default=None, type=str, required=False,
                    help="Where to save package archive.")

def main(args) -> None:
  twoxtwo_dir = os.path.dirname(os.path.realpath(__file__))

  readme_path = os.path.join(twoxtwo_dir, _README_FILENAME)
  license_path = os.path.join(twoxtwo_dir, _LICENSE_FILENAME)
  sty_path = os.path.join(twoxtwo_dir, _STY_FILENAME)
  doc_path = os.path.join(twoxtwo_dir, _DOC_FILENAME)
  
  # Strip images from README.
  readme_lines = []
  with open(readme_path, "r") as f:
    include_line = True
    for line in f.readlines():
      if line == _STRIP_START:
        include_line = False
      elif line == _STRIP_END:
        include_line = True
      if include_line:
        readme_lines.append(line)

  with tempfile.TemporaryDirectory() as temp_dir:
    temp_dir_ = os.path.join(temp_dir, "twoxtwogame")
    os.mkdir(temp_dir_)
    print(f"Made temp directory at {temp_dir}")

    with tempfile.TemporaryDirectory() as temp_latex_dir:
      # Call latex twice to mitigate potential referencing problems.
      command = [
          _LATEX, "--shell_escape", f"-output-directory={temp_latex_dir}",
          "-halt-on-error", doc_path]
      print("Building pdf first time...")
      subprocess.call(command)
      print("Building pdf second time...")
      subprocess.call(command)
      shutil.move(
          os.path.join(temp_latex_dir, _PDF_FILENAME),
          os.path.join(temp_dir_, _PDF_FILENAME))
          
    with open(os.path.join(temp_dir_, _README_FILENAME), "w") as f:
      f.writelines(readme_lines)

    shutil.copyfile(license_path, os.path.join(temp_dir_, _LICENSE_FILENAME))
    shutil.copyfile(sty_path, os.path.join(temp_dir_, _STY_FILENAME))

    out_dir = args.dir
    if not out_dir:
      out_dir = os.path.join(os.path.expanduser("~"), "twoxtwogame")

    print(f"Saving archive at {out_dir}")
    shutil.make_archive(out_dir, "zip", temp_dir)


if __name__ == "__main__":
  main(parser.parse_args())
