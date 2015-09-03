import os
import sys

from struct import unpack as st_unpack
from collections import namedtuple

UT4_GAME_DIRECTORY = r"UnrealTournament/Content/"
UE4_PACKAGE_MAGIC = 0x5A6F12E1

# for Python 2/3 compatibility:
try:
	xrange
except NameError:
	xrange = range

class Pak(object):
	import os

	def __init__(self,stream):
		self.read(stream)
		
	def initialize(self,version,index_offset,index_size,footer_offset,index_sha1,mount_point=None,records=None):
		self.version       = version
		self.index_offset  = index_offset
		self.index_size    = index_size
		self.footer_offset = footer_offset
		self.index_sha1    = index_sha1
		self.mount_point   = mount_point
		self.records       = records or []
		
	def read(self,stream):
		stream.seek(-44, 2)
		footer_offset = stream.tell()
		footer = stream.read(44)
		magic, version, index_offset, index_size, index_sha1 = st_unpack('<IIQQ20s',footer)

		if magic != UE4_PACKAGE_MAGIC:
			raise ValueError('Invalid pak file')
			
		if version != 3:
			raise ValueError('Unknown pak version: %d' % version)

		if index_offset + index_size > footer_offset:
			raise ValueError('Corrupt pak file')

		stream.seek(index_offset, 0)
		mount_point = self.read_string(stream)
		entry_count = st_unpack('<I',stream.read(4))[0]

		self.initialize(version, index_offset, index_size, footer_offset, index_sha1, mount_point)

		for i in xrange(entry_count):
			filename = self.read_string(stream)		
			record = self.read_record(stream, filename)
			self.records.append(record)

		if stream.tell() > footer_offset:
			raise ValueError('Records exceed size')
			
	def read_string(self,stream):
		path_len, = st_unpack('<I',stream.read(4))
		return stream.read(path_len).rstrip(b'\0').decode('utf-8').replace('/',os.path.sep)

	def read_record(self,stream, filename):
		# skip, we don't need extra info
			
		stream.seek(8, 1) # offset
		stream.seek(8, 1) # size
		stream.seek(8, 1) # uncompressed
		compression_method, = st_unpack('<I',stream.read(4))
		stream.seek(20, 1) # sha1
		
		if compression_method != 0x00:
			block_count, = st_unpack('<I', stream.read(4))
			stream.seek(block_count * 16, 1) # compression block

		stream.seek(1, 1) # encrypted
		stream.seek(4, 1) # compression block size

		return Record(filename)
		
	def print_info(self,pak_file,game_directory="",detailed=False,batch=False,out=sys.stdout):
		self.game_dir = game_directory
		
		maps = 0
		lastindex = 0
		for idx, record in enumerate(self.records):
			if record.filename.endswith(".umap"):
				lastindex = idx
				maps += 1
			
		if maps == 0:
			out.write("No maps found.\n")
			return False
					
		pak_name = pak_file.replace("\\", "/")
		if not batch: pak_name = pak_name.rsplit("/")[-1]
		
		headersize = max(35, len(pak_name))
		out.write(pak_name+"\n")
		out.write("-"*headersize+"\n")
		
		if maps > 1:
			out.write("Maps (%d):\n" % maps)	
		elif maps == 0:
			out.write("No maps found.\n")
		
		index = 1
		for record in self.records:
			if record.filename.endswith(".umap"):
			
				# sanitize names
				map = self.sanitize_map(record.filename)
				mappath = record.filename.replace("\\", "/")
				mapfile = map.rsplit("/")[-1]
				mapname = mapfile.rsplit(".", 1)[0]
				mapurl = map.rsplit(".", 1)[0]
				
				if detailed:
					if maps > 1:
						out.write(" [%3s]\tMap name: %s\n" % (index, mapname))
						out.write("\tMap path: %s\n" % mappath)
						out.write("\tMap  URL: %s\n" % mapurl)
					else:
						out.write("Map name: %s\n" % mapname)
						out.write("Map path: %s\n" % mappath)
						out.write("Map  URL: %s\n" % mapurl)
						
				elif maps == 1:
					out.write("%s\n" % (mapurl))
				else:
					out.write("%s %s = %s\n" % (index, mapname, mapurl))
				
				index += 1
		
		out.write("="*headersize+"\n")
		if batch: out.write("\n")
		
		return True
			
	def sanitize_map(self,map,out=sys.stdout):
		# correct path
		map = os.path.join(self.mount_point,map)
		map = map.replace("\\", "/")
		
		# remove trailing directory traversal
		map = map.strip("./")

		# replace game directory
		if self.game_dir and map.startswith(self.game_dir):
			map = map.replace(self.game_dir, "Game/")

		# add trailing slash
		if not map.startswith("/"): map = "/"+map

		return map
	
class Record_(namedtuple('RecordBase', [
	'filename', 'offset', 'compressed_size', 'uncompressed_size', 'compression_method',
	'timestamp', 'sha1', 'compression_blocks', 'encrypted', 'compression_block_size'])):
	pass

class Record(Record_):
	def __new__(cls, filename, offset=0, compressed_size=0, uncompressed_size=0, compression_method=0, sha1=[20],
	             compression_blocks=[20], encrypted=0, compression_block_size=0):
		return Record_.__new__(cls, filename, offset, compressed_size, uncompressed_size,
		                      compression_method, None, sha1, compression_blocks, encrypted,
		                      compression_block_size)	
		

def main(argv):

	args = len(argv)
	help = (args == 0)
	
	print("");
	
	if not help:
		
		# normalize args
		argc = []
		for arg in argv:
			if arg.startswith("-"):
				argc.append(arg.lower().replace("--", "-"))
		
		if args < 1:
			raise SyntaxWarning('Missing file name')
		elif args > 1 and not argv[1].startswith("-"):
			raise SyntaxWarning('Missing quotes')
		elif not argv[0]:
			raise SyntaxWarning('Empty parameters')
		
		pakfile = argv[0];
		
		if pakfile.startswith("-"):
			raise SyntaxWarning('Unknown option/parameter: %s' % pakfile)
	
		if not os.path.exists(pakfile):
			raise SyntaxWarning('Invalid path')
		elif not os.access(pakfile, os.R_OK):
			raise SyntaxWarning('Unable to read given file/folder')
		else:
			
			optfull = ("-full" in argc)
		
			if os.path.isfile(pakfile):
				with open(pakfile,"rb") as stream:
					pak = Pak(stream)
					pak.print_info(pakfile,UT4_GAME_DIRECTORY, detailed=optfull)
			else:
				count = 0
				for root, dirs, files in os.walk(pakfile, followlinks=True):
					for file in files:
						fullpath = os.path.join(root, file)
						if fullpath.endswith(".pak") and os.access(fullpath, os.R_OK):
							with open(fullpath,"rb") as stream:
								pak = Pak(stream)
								printpath = fullpath.replace(pakfile, "", 1).strip("/\\")
								if pak.print_info(printpath,UT4_GAME_DIRECTORY, batch=True, detailed=optfull):
									count += 1
				
				if count < 1:
					print("No packages with maps found.\n")

	else: # if not help
	
		print("Retrieve map names from UT4 packages")
		print("-------------------------------------")
		print("Usage: ListMaps.exe <File|Path>")

	# just wait for keypress to support drag'n'drop in Windows (from Explorer)
	print("")		
	os.system('pause')  #windows

if __name__ == '__main__':
	try:
		main(sys.argv[1:])
	except SyntaxWarning as syn:
		sys.stderr.write("%s\n" % syn)
		os.system('pause')  #windows
		sys.exit(1)
	except (ValueError, NotImplementedError, IOError) as exc:
		sys.stderr.write("%s\n" % exc)
		os.system('pause')  #windows
		sys.exit(1)

