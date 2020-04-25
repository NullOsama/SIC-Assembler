# SIC-Assembler

SIC-Assembler Project that assembles a SIC architechure scripts and generates the requared files and records.
## Usage

```bash
python assembler.py <input script path> <intermediate file path> <listing file path> <object file path>
```
Example: 
```bash
python .\assembler.py  .\sample_tests\source.asm .\intermediate.mdt .\listing.lst .\object_file.obj
```


It takes the script in the inputfile source and generates the symbol table, program name, program length, ... etc.
After generating the intermediate file it will generate both the listing file containing the object code for each instruction and the object file which contains the generated text records.
Literals are supported and stored in the symbole table.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.


## License

[MIT](https://choosealicense.com/licenses/mit/)
