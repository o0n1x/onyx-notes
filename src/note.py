#notes class

import re
from frontmatter import Frontmatter
from datetime import datetime , date
from note_io import write_note
class Note():
    
    
    def __init__(self,raw_md : str = None ):
        """
        initalize a note object.
        accepts input raw text from frontmatter file (md file with yaml as header)
        """
        #raw text (raw_md includes header)
        self.raw_md = raw_md 
        try:
            self.yaml_header_dict = Frontmatter.read(raw_md)
        except Exception as e:
            #TODO: implement so error can show in the user interface
            print(f"Error:{e}")
            self.yaml_header_dict = None
        if self.yaml_header_dict:
            self.yaml_header = self.yaml_header_dict["frontmatter"]
            self.attributes = self.yaml_header_dict["attributes"] 
            self.body = self.yaml_header_dict["body"] 
        else:
            self.yaml_header = None
            self.attributes = None
        #metadata
        self.parse_attributes()

        #links to other notes
        self.links = []
    

    #TODO: Add support for custom attributes
    def get_formatted_md(self) -> str:
        "returns markdown string of the note formatted with updated metadata if any"
        md = ""
        md += "---\n"
        md+= f"title: {self.title}\n"
        md += f"tags: {self.tags}\n"
        md += f"created: {self.created_date}\n"
        md += f"last_modified: {self.modified_date}\n"
        md += f"---\n"
        if self.yaml_header_dict and self.yaml_header_dict["frontmatter"] != "":
            md += self.yaml_header_dict["body"]
        else:
            md += self.raw_md
        return md

    def __eq__(self, value):
        if (type(value) == str):
            if(self.raw_md == value):
                return True
            return False
        if (self.raw_md == value.raw_md):
            return True
        return False

    #TODO: make it possible so that dates can use / instead of - 
    
    def parse_attributes(self) -> None:
        """
        internal function used when initalizing a note object.
        parses attributes dictionary for expected values: tags,title,created, and last_modified
        """
        if self.attributes and type(self.attributes) == dict:
            #tags
            if "tags" in self.attributes and type(self.attributes["tags"]) == list:
                self.tags = self.attributes["tags"]
            else:
                self.tags = []
            #title
            if "title" in self.attributes and type(self.attributes["title"]) == str:
                self.title = self.attributes["title"]
            else:
                self.title = "Untitled Note"
            #date Created
            if "created" in self.attributes:
                created_date = self.attributes["created"]
                if type(created_date) == datetime:
                    self.created_date = created_date
                elif type(created_date) == date:
                    self.created_date = datetime.combine(created_date, datetime.min.time())
                else:
                    self.created_date = datetime.now().replace(microsecond=0)
            else:
                self.created_date = datetime.now().replace(microsecond=0)
            #date modified
            if "last_modified" in self.attributes:
                if type(self.attributes["last_modified"]) == datetime:
                    self.modified_date = self.attributes["last_modified"]
                elif type(self.attributes["last_modified"]) == date:
                    self.modified_date = datetime.combine(self.attributes["last_modified"], datetime.min.time())
                else:
                    self.modified_date = datetime.now().replace(microsecond=0)
            else:
                self.modified_date = datetime.now().replace(microsecond=0)
        else:
            self.tags = []
            self.title = "Untitled Note"
            self.created_date = datetime.now().replace(microsecond=0)
            self.modified_date = datetime.now().replace(microsecond=0)
        #TODO: Support for saving other custom attributes for costimizability and support reasons
    def __repr__(self):
        return  self.__str__() +"\n" + self.raw_md 
    
    def  __str__(self):
        return f"Title: {self.title}\t Tags: {self.tags}\nCreated: {self.created_date.date()}\tLast Edited: {self.modified_date.date()}\nNote length: {len(self.raw_md)}"

    