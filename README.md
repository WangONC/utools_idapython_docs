utools_idapython_docs

IDA Python SDK Search for utools

From [Mas0nShi/utools_idapython_docs](https://github.com/Mas0nShi/utools_idapython_docs)

## impl

based on [official documentation](https://hex-rays.com/products/ida/support/idapython_docs/)

use html parser replace some cdn refer/resources to local.

moreover, remove useless nodes.

## usage

you can search `IDAPythonDoc` in uTool official store.

## features

- platform of utools
- quick search in globals(variables/function/...)
- search by module
- display a brief description and the module of the current variables/function

## todo

- [ ] update to 9.0

## build

1. `cd utools_idapython_docs`
2. `pip install lxml requests`
3. `python ./generate.py`
4. create a project in uTools DevTools and open the plugin.json file.

## update

### v1.0.0-1.0.1

The following modifications have been made compared to the original project:
- Reduce duplicate requests and utilize a thread pool for concurrent processing to accelerate the request speed.
- Modified the relevant resource paths to enable direct uploading of the generated documentation to uTools.
- Utilize the default 32*32 size logo from the hex-rays website and include a logo request function.
