"""
SCUMM Tools: SOU Rip - Sound ripper for SCUMM v6 games (Day Of The Tentacle and Sam & Max)
Copyright (C) 2024 UnBeatWater

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
# This code is not meant to be pretty or fast, but it is functional, I think.

from os import makedirs
from colorama import Fore


EXTRACT_DIR = 'monster_extracted'

def save_sound(sound_number, sound_data):
	file_name = f'{EXTRACT_DIR}/sound{sound_number}.voc'
	print(f'{Fore.LIGHTGREEN_EX}Writing "{file_name}"...')
	with open(file_name, 'wb') as f:
		f.write(sound_data)


# SOU specs (from ScummVM Wiki)
# Block name			4 bytes ("SOU ")
# Block size			4 bytes
# One or more:
# 	Block name		4 bytes ("VCTL")
# 	Block size		4 bytes
# 	Lip-sync tags		variable * 2 bytes LE
# 	Sound data		variable ("Crea" block / VOC file)
def main():
	makedirs(EXTRACT_DIR, exist_ok=True)
	with open('monster.sou', 'rb') as f:
		if f.read(4) != b'SOU ':
			raise Exception('File is not a SOU file!')
		f.read(4)
		
		sound_number = 1
		
		while True:
			header = f.read(4)
			if len(header) < 4:
				break
			if header != b'VCTL':
				raise Exception('Sound blocks are not VCTL!')
			print(f'{Fore.LIGHTYELLOW_EX}Block:')
			print(f'{Fore.LIGHTYELLOW_EX}  Header: {Fore.LIGHTBLUE_EX}"{header.decode("ascii")}"')
			size = f.read(4)
			if len(size) < 4:
				raise Exception('Failed reading size!')
			size = int.from_bytes(size, byteorder='big') - 8
			print(f'{Fore.LIGHTYELLOW_EX}  Tag Count: {Fore.LIGHTBLUE_EX}{size}')
			
			# Skip the tags
			if len(f.read(size)) < size:
				raise Exception('Failed skipping tags!')
			
			sound_data = b''
			end_of_file = False
			while True:
				read_bytes = f.read(4)
				if len(read_bytes) < 4:
					end_of_file = True
					break
				if read_bytes != b'VCTL':
					sound_data = sound_data + read_bytes[0:1]
				else:
					break
				f.seek(-3, 1)
			
			save_sound(sound_number, sound_data)
			
			if end_of_file == True:
				print(f'{Fore.LIGHTGREEN_EX}Done! Extracted {sound_number} sounds.')
				break
			
			f.seek(-4, 1)
			
			# Hehe he ... hee...
			sound_number = sound_number + 1


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		print(Fore.RED + 'ERROR!:', e)
