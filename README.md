# qtMarkTool

## Description
A tool for mark items with weight, web server use fastapi, interface use pyqt6

---
## Tech stack
GUI: QT6

Server: fastapi

Wsgi: uvicorn

---
## Functions

- [x]  import files
- [x]  set table header
- [x]  add row to table
- [x]  get select click position of table
- [x]  edit table
- [x]  delete row from table
- [x]  connect two tables
- [x]  get value from line edit box(and validate it)
- [x]  base fomula to calculate
- [x]  fastapi server
- [x]  generate QRCode
- [x]  web page to see files
- [x]  web page to input scores
- [x]  refresh score
- [ ]  export csv
- [x]  export config/load config if need.
- [x]  data file read and write if need.
- [ ]  allow anonymity grade

```shell
pyinstaller -F main.py
```
**if program launch slowly**
```shell
pyinstaller -D main.py
```
**if you don't need console window on Windows**
```shell
pyinstaller -F -w main.py
```


