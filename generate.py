# coding=utf-8
import json
import os
from typing import List, Dict, Union

from requests import get,Response
from lxml import etree
import html
from concurrent.futures import ThreadPoolExecutor,wait,as_completed

REPLACE_DIR = "assets"
DOC_HOST = "https://hex-rays.com/products/ida/support/idapython_docs"
ROOT_PATH = r"idapython_docs\html"
LOGO_URL = "https://hex-rays.com/favicon/favicon-32x32.png"

def get_logo():
    logo = get(LOGO_URL)
    logoFile = open("favicon.png", "wb")
    logoFile.write(logo.content)
    logoFile.close()
    print("logo saved")


def _get(url):
    return url,get(url)

def get_url_array_response(url_arr:List[str]) -> List[tuple[str, Response]]:
    taskArray = []

    with ThreadPoolExecutor(max_workers=len(url_arr)) as executor:
        taskArray = [executor.submit(_get,format_uri(page)) for page in url_arr]
    
        for task in as_completed(taskArray):
            print(task.result()[0] + " responsed")
    
    return [task.result() for task in taskArray]


def format_uri(name: str):
    return "{host}/{path}".format(host=DOC_HOST, path=name)


def get_all_href(_elements: List[etree.ElementBase]):
    return [element.get("href") for element in _elements]


def get_utool_preload_doc(_all_page_info, folder_path=""):
    all_in_one = []
    for page_info in _all_page_info:
        name = page_info["path"]
        tmp = [{"t": t["name"], "p": os.path.join(folder_path, name + t["href"]), "d": t["desc"]} for t in
               page_info["globals"]]
        all_in_one.extend(tmp)

    return all_in_one


def get_all_page_globals(_paths: List[tuple[str, Response]]):
    all_page_info = []
    for resUrl,p in _paths:
        # url = format_uri(p)
        content = p.text
        parser = etree.HTML(content)
        li_arr = parser.xpath('/html/body/main/nav/ul/li[position()]')

        dt_arr=[]
        dd_arr=[]

        for dt in parser.xpath('//dt'):
            dt_arr.append(dt.get('id'))
        
        for dd in parser.xpath('//dd'):
            dd_arr.append(dd.xpath('div/div[1]')[0].text.replace('\n','') if(len(dd.xpath('div/div[1]')) != 0 and dd.xpath('div/div[1]')[0].text.replace('\n','') != "") else dd.xpath('div/div/div[1]')[0].text.replace('\n','') if(len(dd.xpath('div/div/div[1]')) != 0) else "")

        docInfo = {}
        
        for index in range(len(dt_arr)):
            docInfo[dt_arr[index]] = dd_arr[index] if(len(dd_arr[index])<100) else dd_arr[index][:96] + '...'
        



        pageInfo = {"path": resUrl.split("/")[-1], "globals": []}
        for li in li_arr:
            # pageInfo["globals"].extend([{"name": co.text, "href": co.get("href")} for co in li.xpath("ul/li//a")])
            pageInfo["globals"].extend([{"name": co.get("title"), "href": co.get("href"), "desc": docInfo[co.get("title")]} for co in li.xpath("ul/li//a")])
        all_page_info.append(pageInfo)

    return all_page_info


def delete_attr(_l):
    remove_proc = ["crossorigin", "integrity"]
    procs = _l.keys()
    for remove in remove_proc:
        if remove in procs:
            del _l.attrib[remove]


def remove_tag(_tags):
    if len(_tags) > 0:
        for i in _tags:
            i.getparent().remove(i)


def replace_path(_l, _attr: str):
    _l.set(_attr, REPLACE_DIR + "/" + _l.get(_attr).split("/")[-1])


def get_indexes(save_dir: str):
    info = get_all_page_globals(page_arr_response)
    rest = get_utool_preload_doc(info, folder_path="idapython_docs/html")
    open(os.path.join(save_dir, "indexes.json"), "w").write(json.dumps(rest))


def get_html_alias(save_dir: str):
    # generate html
    abs_replace_dir = os.path.join(save_dir, REPLACE_DIR)
    try:
        os.makedirs(abs_replace_dir)
    except FileExistsError:
        pass

    # get all static assets
    static_assets = set()

    for resUrl,page in page_arr_response:
        # url = format_uri(page)
        content = page.content.decode("utf-8")
        parser = etree.HTML(content)

        # remove <nav> tag 'Search'
        nav = parser.xpath("/html/body/main/nav")
        remove_tag(nav)

        # remove <a> tag 'Module index'
        nav = parser.xpath("/html/body/main/article/a")
        remove_tag(nav)

        for _l in parser.xpath("//link"):
            href = _l.get("href")
            if href is not None:
                static_assets.add(href)
                replace_path(_l, "href")
            delete_attr(_l)

        for _l in parser.xpath("//script"):
            src = _l.get("src")
            if src is not None:
                static_assets.add(src)
                replace_path(_l, "src")
            delete_attr(_l)

        # TODO: I cannot have better way to transfer '\2002'
        source = etree.tostring(parser).decode("utf-8")
        source = source.replace(r"li:after{content:',&#128;2'}", r"li:after{content: ',\2002'}")

        # open(os.path.join(save_dir, page), "w").write(html.escape(source))
        open(os.path.join(save_dir, resUrl.split("/")[-1]), "w").write(source.replace("&gt;",">"))
        print("save file {}".format(resUrl.split("/")[-1]))

    static_assets_response = get_url_array_response(static_assets)
    for url,response in static_assets_response:
        content = response.text
        open(os.path.join(abs_replace_dir, url.split("/")[-1]), "w", encoding="utf-8").write(content)

    print("all ok!")


res = get(url=format_uri("index.html"))
elements = etree.HTML(res.text).xpath("/html/body/main/article/ul/li//a")
page_arr = get_all_href(elements)
page_arr_response = get_url_array_response(page_arr)
print(page_arr)

get_html_alias(ROOT_PATH)
get_indexes(ROOT_PATH)
get_logo()