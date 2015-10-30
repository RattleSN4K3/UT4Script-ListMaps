ListMaps
==========================
A bash/shell script to list the maps from UT/UE4 created pak files.

## Usage

- Open a terminal
- Optionally browse to your maps folder
- Download the script file:  
`wget -O listmaps.sh https://raw.githubusercontent.com/RattleSN4K3/UT4Script-ListMaps/bash/listmaps.sh`
- Use the script as follows:  
    ```
# list the map name of a single file
bash ./listmaps.sh <file>

# list maps of every file in the given folder
bash ./listmaps.sh <folder>
    ```

- Optionally you can set the executable flag:  
`chmod +x listmaps.sh`
- and being able to call the script directly  
`./listmaps.sh [<file|folder>]`

## Output
<img src=output.png width=800px>

## License
Available under [the MIT license](http://opensource.org/licenses/mit-license.php).

## Author
RattleSN4K3
