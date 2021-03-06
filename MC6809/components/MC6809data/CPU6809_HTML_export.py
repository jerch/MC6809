"""
    6809 instruction set data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    data from:
        * http://www.maddes.net/m6809pm/sections.htm#sec4_4
        * http://www.burgins.com/m6809.html
        * http://www.maddes.net/m6809pm/appendix_a.htm#appA

    :copyleft: 2013-2014 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os
import sys

PY2 = sys.version_info[0] == 2
if PY2:
    range = xrange

from MC6809.components.MC6809data.MC6809_op_data import OP_DATA, BYTE, WORD
from MC6809.components.MC6809data.MC6809_op_docs import OP_DOC


OUTFILENAME = "CPU6809_opcodes.html"

WIDTH_DICT = {
    None: "no",
    BYTE: "byte",
    WORD: "word",
}


class Cell(object):
    def __init__(self, txt):
        self.txt = txt
        self.rowspan = 0
        self.headline = None
    def html(self):
        if self.rowspan is None:
            return ""
        elif self.rowspan == 1:
            return "<td>%s</td>" % self.txt
        return '<td rowspan="%i" title="%s: %s">%s</td>' % (
            self.rowspan,
            self.headline, self.txt,
            self.txt,
        )

    def __str__(self):
        return "<'%s' rowspan=%s>" % (self.txt, self.rowspan)
    __repr__ = __str__


headlines = (
  "instruction",
  "mnemonic",
  "CC flags",
  "example",
  "op code",
  "bytes",
  "cycles",
  "address mode",
  "needs ea",
  "read from memory",
  "write to memory",
  "register",
)


# Collect the data for the table from MC6809_data_raw2
data = []
for instruction, instr_data in sorted(OP_DATA.items()):
    for mnemonic, memoric_data in sorted(instr_data["mnemonic"].items()):
        instruction_doc = OP_DOC[instruction]
        mnemonic_doc = instruction_doc["mnemonic"][mnemonic]

        for op_code, op_data in sorted(memoric_data["ops"].items()):

            addr_mode = op_data["addr_mode"]
            if addr_mode:
                addr_mode = addr_mode.replace("_", " ").lower()

            if op_code > 0xff:
                op_code = "$%04x" % op_code
            else:
                op_code = "$%02x" % op_code


            data.append([
                instruction,
                mnemonic,
                mnemonic_doc["HNZVC"] or "",
                mnemonic_doc["desc"] or "",
                op_code,
                op_data["bytes"],
                op_data["cycles"],
                addr_mode,

                "yes" if memoric_data["needs_ea"] else "no",
                WIDTH_DICT[memoric_data["read_from_memory"]],
                WIDTH_DICT[memoric_data["write_to_memory"]],
                memoric_data["register"] or "-",

            ])


# add rowspan information
for colum_no in range(len(data[0])):
    old_cell = None
    same_count = 0
    for row in reversed(data):
        cell = row[colum_no] = Cell(row[colum_no])
        if old_cell is None:
            same_count = 1
        elif cell.txt == old_cell.txt:
            old_cell.rowspan = None
            same_count += 1
        else:
            old_cell.rowspan = same_count
            same_count = 1
        old_cell = cell
    old_cell.rowspan = same_count


# add headline to cells (used for td title="")
for row in data:
    for cell, headline in zip(row, headlines):
        if cell.rowspan is not None:
            cell.headline = headline


# generate html file
with open(OUTFILENAME, 'w') as htmlfile:
    htmlfile.write("""<!DOCTYPE html>
<html>
<head>
<style>
table, th, td{border-collapse:collapse;border:1px solid black;}
th, td {padding:5px;}
</style>
</head>
<body>
<h1>6809 opcodes:</h1>
<table>
<tr>
""")
    for headline in headlines:
        htmlfile.write("\t<th>%s</th>\n" % headline)
    htmlfile.write("</tr>\n")

    for row in data:
        htmlfile.write("\t<tr>\n")
        for cell in row:
            if cell.rowspan is not None:
                htmlfile.write("\t\t%s\n" % cell.html())
        htmlfile.write("\t</tr>\n")
    htmlfile.write("</table>")
    htmlfile.write(
        "<addr>This file was generated by %s</addr>" % os.path.split(__file__)[1]
    )
    htmlfile.write("</body></html>")


print("file %r written" % OUTFILENAME)
print(" -- END -- ")
