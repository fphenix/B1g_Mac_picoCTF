# B1g_Mac_picoCTF
An innovative way to crack the picoCTF/picoGym B1g_Mac challenge!

Intro:
------

I spent a lot of time studying and analyzing the B1g_Mac picoCTF/picoGym challenge.
Although I find it in many ways very frustrating and a bit over the top, yet, I did learn A LOT from it and in the end had fun with it.

I wanted to be able to crack it solely on my Linux machine, and came up with a solution that I did not see thus far!

Pre-requisits:
--------------

You probably need to understand the solution to the challenge to go on with the rest of my rant.
Specifically, you need to understand what the main.exe does (even more specifically the _hideInFile() function.)

B1g_Mac on Linux only:
----------------------

This issue is to get a precise enough value for the lastWriteTime/ModificationTime file attribute.
The ```$> stat``` command fails in that regard.

I then wondered where did that value come from.
Surely it was somehere in the zip file because the unzipping would restore those FILETIME attributes to the file.

Sure enough! Digging in the PKZIP Specs, here's what we find out:

At the end of a .zip file, a "Central Directory" block stores some metadata for each of the files zipped.
The signature for each Central Directory entry is b'PK\x02\x01'

If you understand the main.exe well enough, you know that it is the "*Copy.bmp" files (in the test/ folder) that hide the flag (or part of it, 2 bytes at a time).

Every Central Directory entry defines an "Extra Field" of length 36 bytes.

The Extra Fields are defined with the ID "0x000A", which is the reserved ID for "NTFS".

The NTFS Extra Field stores the precise time values (Modif, Access, Creation), and more to the point the one we are interested in: the Stegofy'ed version of the value for the "LastWriteTime" attribute.

Now, I am nowhere near a pro at Python. I am usually able to get the result I want with probably poorly written code.
The point here is not code (although I am always interested in learning new things to improve my coding, so feel free to send constructive critisism). The point is that with no debugger (i.e. "no breakpoint", cuz', well, I did abuse the decompiler/code browser of Ghidra a lot in this challenge ^^), no emulator or esotheric libraries, no need to jump to Windows, I was still able to reconstruct the flag with a simple Linux-only script.

Without further ado, here's the script that cracks picoCTF "B1g_Mac"!
If you know PKZIP file format, then it's pretty much self explanatory.

The code!
---------
```
#!/usr/bin/python3 -u

"""fphenix @ https://github.com/fphenix/B1g_Mac_picoCTF"""

import os

filename = "b1g_mac.zip"
fileindex = 0
statePhase = 0

centralDirSignature = b'PK\x01\x02'
bmpCopyFileName = b'Copy'
bmpCopyFileExte = b'.bmp'
flag = ''

with open(filename, 'rb') as fh:
	while (fourbytes := fh.read(4)):
		if (statePhase == 0) and (fourbytes == centralDirSignature):
			print(f'Found a Central Directory Signature at {hex(fileindex)}')
			statePhase = 1
			fileindex = fileindex + 4
		elif (statePhase == 1) and (fourbytes == bmpCopyFileName):
			print(f'   * "Copy" at {hex(fileindex)}')
			statePhase = 2
			fileindex = fileindex + 4
		elif (statePhase == 2) and (fourbytes == bmpCopyFileExte):
			print(f'   * ".bmp" at {hex(fileindex)}')
			statePhase = 3
			fileindex = fileindex + 16 	# go in the NTFS Extra Field where LastWriteTime is stored
		elif (statePhase == 3):
			flag += chr(fourbytes[1])
			flag += chr(fourbytes[0])
			print(f'  Got : "{chr(fourbytes[1])}" and "{chr(fourbytes[0])}" around {hex(fileindex)}')
			statePhase = 0
			fileindex = fileindex + 2
		else:
			fileindex = fileindex + 1

		fh.seek(fileindex, os.SEEK_SET)

print('\nFlag is : {}\n'.format(flag))
```
