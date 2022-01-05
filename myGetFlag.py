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
			fileindex = fileindex + 16 				# go in the NTFS Extra Field where LastWriteTime is stored
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
