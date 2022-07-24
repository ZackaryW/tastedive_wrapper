from dataclasses import dataclass
import dataclasses
import typing
from tastediveW.auth.request import makeRequest, getCSRF
import requests
from tastediveW.title import Title
from requests_toolbelt import MultipartEncoder
import string
import random

@dataclass
class Account:

    load_all : bool = False
    name : str = None
    username : str = None
    email : str = None
    country : str = None
    titles : typing.List[Title] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        if self.load_all:
            self.load()

    def _parse_general_info(self, lines : typing.List[str]):
        splitted = lines[1].split(",")
        self.name = splitted[0].strip()
        self.username = splitted[1].strip()
        self.email = splitted[2].strip()
        self.country = splitted[3].strip()


    def _parse_section(self, section : typing.List[str]):
        line = section[0].lower()

        if "general info" in line:
            return self._parse_general_info(section)
        
        titleType = line.split(" ")[0]
        attitude = line.rsplit(" ",1)[-1][:-2]
    
        pending_titles = ",".join(section[1:])
        pending_titles = pending_titles.split(",")
        # remove empty lines
        pending_titles = [title for title in pending_titles if title != ""]

        for pending in pending_titles:
            title = Title.fromDict(Name=pending, Type=titleType, _ratings=attitude)
            self.titles.append(title)
    
    def load(self):
        content = self.downloadData()
        contentLines = content.decode("utf-8").split("\n")
        
        # remove all empty lines
        contentLines = [line for line in contentLines if line != ""]

        starting_index = None
        ending_index = None

        for i, line in enumerate(contentLines):
            if not (":" in line and "," not in line): 
                continue
            # this is a marker category
            if starting_index is None:
                starting_index = i
            else:
                ending_index = i
                self._parse_section(contentLines[starting_index:ending_index])
                starting_index = None
                ending_index = None

    def downloadData(self):
        """
        Download the data of the account.
        """

        boundary = '----WebKitFormBoundary' \
           + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        fields = {
            "perform_action" : str(1),
            "download_data" : str(1),
            "_csrf_token" : getCSRF(),
        }
        m = MultipartEncoder(fields=fields, boundary=boundary)


        res = makeRequest(
            url = "https://tastedive.com/account/settings",
            request_method= requests.post,
            data = m,
            headers= {
                "Content-Type": m.content_type,
            }
        )

        if res.status_code != 200:
            raise ValueError("Invalid response")

        # get file
        fileContent = res.content
        return fileContent

    def exportData(self, path : str):
        data = self.downloadData()
        with open(path, "wb") as f:
            f.write(data)

        