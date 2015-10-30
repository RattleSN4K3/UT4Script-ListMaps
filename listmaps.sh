#!/bin/bash

listmaps()
{
	inpak=$1

	# Retrieve raw map path from file.
	rawMapPath=$(tac $inpak | grep -m 1 -oUaP "[^\x00]+\x2e\x75\x6d\x61\x70" | grep -m 1 -oUaP ".*[^\x2e\x75\x6d\x61\x70]");

	# Replace portions of map path.
	mapPath=$(echo $rawMapPath | sed "s/^\(UnrealTournament\/\)\?Content/Game/g");

	# Generate md5 checksum.
	mapChecksum=$(md5sum $inpak | awk '{ print $1 }');

	echo "$(basename $inpak) $mapPath $mapChecksum";
}

# Specify your map path.
args=$@

if [ -d $args ] ; then

	paksDir=$args
	for pak in $(find $paksDir -name "*.pak" ! -name "UnrealTournament-*.pak");
	do
		listmaps $pak
	done

else
	if ! [ -f "$args" ] ; then
		echo "No such file/folder: $args"
		return 1
	fi

	listmaps $args
fi

